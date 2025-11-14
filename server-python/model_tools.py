import numpy as np
from PIL import Image
import torch 
import open_clip
import chromadb
from chromadb.utils import embedding_functions
from typing import Dict, Any

# We assume the vector dimension is 768 based on the ViT-B-16 model
VECTOR_DIMENSION = 768 


# --- (1) Model Loading Function ---

# NOTE: The OpenCLIP model structure is 'ViT-B-16' and its weights are 'openai'
MODEL_NAME = "ViT-B-16"
PRETRAINED_WEIGHTS = "openai"

def load_ip_model(model_name: str = MODEL_NAME, weights_name: str = PRETRAINED_WEIGHTS) -> Dict[str, Any]:
    """
    Loads the OpenCLIP vision model and initializes the ChromaDB vector store.
    """
    print(f"--- Loading OpenCLIP model: {model_name}/{weights_name} ---")
    
    try:
        # 1. Define the device (use GPU if available, otherwise CPU)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 2. Load the model and the required image preprocessing object
        model, _, preprocess = open_clip.create_model_and_transforms(
            model_name, 
            pretrained=weights_name, 
            device=device
        )
        
        # 3. Set model to evaluation mode (CRUCIAL)
        model.eval() 
        
        # --- ChromaDB Initialization ---
        print("--- Initializing ChromaDB Vector Store ---")

        # 4. Initialize the Chroma Client (stores data locally in a folder named 'chroma_data')
        chroma_client = chromadb.PersistentClient(path="./chroma_data")
        
        # 5. Define the Embedding Function for Chroma
        class DummyEmbeddingFunction(embedding_functions.EmbeddingFunction):
            def __call__(self, texts: list[str]) -> list[list[float]]:
                return [[0.0] * VECTOR_DIMENSION] * len(texts)

        clip_ef = DummyEmbeddingFunction()

        
        # 6. Get or Create the Collection (your table of vectors)
        collection_name = "ip_vector_collection"
        
        try:
            collection = chroma_client.get_collection(name=collection_name)
            print(f"Loaded existing collection: {collection_name}. Count: {collection.count()}")
        except Exception:
            collection = chroma_client.create_collection(
                name=collection_name, 
                embedding_function=clip_ef
            )
            print(f"Created new collection: {collection_name}")
            
        # 7. Return the model assets AND the database collection
        print(f"Model and VectorDB loaded successfully on device: {device}")
        return {
            "model": model, 
            "preprocess": preprocess, 
            "device": device,
            "vector_db": collection
        }
        
    except Exception as e:
        print(f"FATAL ERROR: Could not load OpenCLIP model or ChromaDB. Details: {e}")
        raise


# --- (2) Vector Generation Function ---

def generate_ip_vector(loaded_assets: Dict[str, Any], image: Image.Image) -> np.ndarray:
    """
    Generates a feature vector from a PIL Image object using the pre-loaded OpenCLIP model.
    """
    model = loaded_assets["model"]
    preprocess = loaded_assets["preprocess"]
    device = loaded_assets["device"]

    # 1. Preprocessing (Uses the specific function provided by OpenCLIP)
    input_tensor = preprocess(image).unsqueeze(0).to(device) 
    
    # 2. Inference (Running the model)
    with torch.no_grad():
        vector_output = model.encode_image(input_tensor)
        vector_output /= vector_output.norm(dim=-1, keepdim=True)
        
    # 3. Post-processing
    return vector_output.cpu().numpy().squeeze()


# --- (3) Vector Addition Function ---

def add_vector_to_db(collection: chromadb.Collection, vector: np.ndarray, file_name: str, metadata: dict = None) -> int:
    """
    Adds a single vector to the ChromaDB collection.
    """
    collection.add(
        embeddings=[vector.tolist()],
        documents=[f"Vector for file: {file_name}"],
        metadatas=[metadata or {}],
        ids=[file_name]
    )
    return collection.count()


# --- (4) Vector Search Function ---

def search_vector_db(collection: chromadb.Collection, query_vector: np.ndarray, n_results: int = 10) -> dict:
    """
    Queries the ChromaDB collection to find the most similar vectors.
    """
    results = collection.query(
        query_embeddings=[query_vector.tolist()],
        n_results=n_results,
        include=['metadatas', 'distances'] 
    )
    return results