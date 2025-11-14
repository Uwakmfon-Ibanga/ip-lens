from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse # FIXED: JSONResponse imported from fastapi.responses
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
from datetime import datetime
from typing import List, Dict, Any
import os
import shutil

# --- REQUIRED IMPORTS FROM MODEL_TOOLS.PY ---
from model_tools import load_ip_model, generate_ip_vector, add_vector_to_db, search_vector_db 
# --------------------------------------------


# --- (1) Setup ---

# CRITICAL: Use an absolute path to ensure FastAPI finds the assets folder reliably.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_FOLDER = os.path.join(BASE_DIR, "story_protocol_assets")

app = FastAPI(title="IP Lens Vector Generator & Search API")

# Define which origins (frontends) are allowed to access your API
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# --- STATIC FILES SETUP: ---
# 1. Ensure the directory exists
if not os.path.exists(ASSETS_FOLDER):
    os.makedirs(ASSETS_FOLDER)
    print(f"Created assets folder at: {ASSETS_FOLDER}")
    
# 2. Mount the static files: 
# Maps requests to http://localhost:8000/assets/... to the local ASSETS_FOLDER.
app.mount("/assets", StaticFiles(directory=ASSETS_FOLDER), name="assets")
# --- END STATIC FILES SETUP ---


# Global state
MODEL: Dict[str, Any] = {}
VECTOR_DIMENSION = 768 


@app.on_event("startup")
async def startup_event():
    """
    Loads the ML model and initializes the vector database upon server startup.
    """
    global MODEL
    print("--- Starting Application Setup ---")
    MODEL = load_ip_model()
    print("--- Application startup complete. Ready for requests. ---")


# --- (2) Pydantic Response Models ---

class VectorResponse(BaseModel):
    vector: list[float]
    status: str = "success"

class AddResponse(BaseModel):
    id: str
    new_total_count: int
    status: str = "added"
    
class SearchResponseItem(BaseModel):
    id: str
    distance: float
    metadata: dict

class SearchResponse(BaseModel):
    query_filename: str
    results: list[SearchResponseItem]
    status: str = "success"


# --- (3) The API Endpoints ---

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "IP Lens API is running and ready to process images."}


# Endpoint 1: Generate Vector (for quick checks)
@app.post("/generate-vector", response_model=VectorResponse)
async def create_upload_file(file: UploadFile = File(...)):
    """
    Receives an image and returns only the 768-dimensional feature vector.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        
        if not MODEL:
             raise HTTPException(status_code=503, detail="Model is still loading or failed to load.")
        
        # CORE LOGIC: Generate the Vector
        ip_vector = generate_ip_vector(loaded_assets=MODEL, image=image) 
        
        return VectorResponse(vector=ip_vector.tolist())

    except Exception as e:
        print(f"Error during vector generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during vector processing.")


# Endpoint 2: Add Vector (for building the library)
@app.post("/add-vector", response_model=AddResponse)
async def add_image_vector(file: UploadFile = File(...)):
    """
    Generates a vector for the input image, saves it locally, and adds it to the vector database.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        # Read file content and open as PIL Image
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        
        if not MODEL:
            raise HTTPException(status_code=503, detail="Model is still loading or failed to load.")

        # --- NEW: Save file locally ---
        file_name_id = file.filename 
        file_path = os.path.join(ASSETS_FOLDER, file_name_id)
        
        # We check if the file already exists
        if os.path.exists(file_path):
             return JSONResponse(status_code=200, content={"message": f"File {file_name_id} already exists. Skipping save."})

        # Save the file to disk so the frontend can retrieve it later via /assets
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        # --- End NEW: Save file locally ---
        
        # Generate the Vector
        ip_vector = generate_ip_vector(loaded_assets=MODEL, image=image)
        
        # Add to the Database
        collection = MODEL.get("vector_db")
        if not collection:
            raise HTTPException(status_code=500, detail="Vector database not initialized.")

        
        new_count = add_vector_to_db(
            collection=collection,
            vector=ip_vector,
            file_name=file_name_id,
            # CRITICAL: Ensure 'filename' is in metadata so frontend knows what to request
            metadata={"filename": file.filename, "upload_time": str(datetime.now())} 
        )
        
        return AddResponse(id=file_name_id, new_total_count=new_count)

    except Exception as e:
        print(f"Error during vector addition: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error during vector storage: {e}")


# Endpoint 3: Search Vector (the main goal!)
@app.post("/search-vector", response_model=SearchResponse)
async def search_for_similar_images(file: UploadFile = File(...), n_results: int = 5):
    """
    Generates a vector for the input image and searches the database for N most similar vectors.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        
        if not MODEL:
            raise HTTPException(status_code=503, detail="Model is still loading or failed to load.")
            
        # 1. Generate the Query Vector
        query_vector = generate_ip_vector(loaded_assets=MODEL, image=image)
        
        # 2. Search the Database
        collection = MODEL.get("vector_db")
        if not collection:
            raise HTTPException(status_code=500, detail="Vector database not initialized.")
        
        raw_results = search_vector_db(
            collection=collection, 
            query_vector=query_vector, 
            n_results=n_results
        )

        # 3. Format the Results for the Frontend
        # ChromaDB results are nested lists, so we use indices [0]
        ids = raw_results.get('ids', [[]])[0]
        distances = raw_results.get('distances', [[]])[0]
        metadatas = raw_results.get('metadatas', [[]])[0]
        
        formatted_results = []
        for i in range(len(ids)):
            formatted_results.append(SearchResponseItem(
                id=ids[i],
                distance=distances[i],
                metadata=metadatas[i] or {}
            ))
        
        return SearchResponse(
            query_filename=file.filename,
            results=formatted_results
        )

    except Exception as e:
        print(f"Error during vector search: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error during vector search: {e}")