IP Lens
A full-stack application for uploading images, generating vector embeddings, and searching intellectual property (IP) assets using AI models and ChromaDB.
Features

Upload images via web UI
Generate vector embeddings for images using a Python backend
Store and search image vectors in ChromaDB
Batch ingestion of assets
Download assets from Story Protocol API
FastAPI backend with REST endpoints
Vite + React frontend

Project Structure
IP-lens/
  ├─ IP-lens/                # Frontend (React + Vite)
  │    ├─ src/components/    # React components
  │    ├─ src/assets/        # Static assets
  │    ├─ index.html         # Main HTML file
  │    └─ ...
  ├─ server-python/          # Backend (FastAPI + Python)
  │    ├─ app.py             # FastAPI app
  │    ├─ ingestion_script.py# Batch ingestion script
  │    ├─ model_tools.py     # Model loading & vector logic
  │    ├─ story_protocol_downloader.py # Asset downloader
  │    └─ ...
  └─ venv/                   # Python virtual environment
       └─ scripts/           # Activation scripts
       
Important Notice
⚠️ Backend Hosting Issue: We experienced issues hosting the backend because the memory it uses exceeds the free tier limits. The backend is not currently hosted online.
Running Locally (Required)
You must run the FastAPI backend locally on your machine to use this application. The frontend will not be able to send requests until the server is running locally.
Getting Started
Prerequisites

Python 3.8+
Node.js 16+
npm or yarn

Backend Setup

Activate the virtual environment from the root directory:

bash   # On Windows
   source ./venv/scripts/activate
   
   # On macOS/Linux
   source ./venv/bin/activate

Navigate to the backend directory:

bash   cd server-python

Install Python dependencies (if not already installed):

bash   pip install -r requirements.txt

Start the FastAPI server on port 8000:

bash   uvicorn app:app --reload --port 8000
The backend should now be running at http://localhost:8000

(Optional) Download assets from Story Protocol:

Create a .env file in server-python/
Add your Story Protocol API key:



     STORY_PROTOCOL_API_KEY=your_api_key_here

Run the downloader:

bash     python story_protocol_downloader.py

(Optional) Batch ingest images:

bash   python ingestion_script.py
Frontend Setup

Navigate to the frontend directory:

bash   cd IP-lens

Install Node dependencies:

bash   npm install

Start the Vite development server:

bash   npm run dev

Access the application in your browser (typically at http://localhost:5173)

API Endpoints
The FastAPI backend provides the following endpoints:

POST /add-vector — Upload an image, generate its vector embedding, and add to ChromaDB
GET /assets/{filename} — Retrieve an image by filename
POST /generate-vector — Generate a vector embedding for an uploaded image
POST /search-vector — Search for similar images using vector similarity

Environment Variables
Backend (.env in server-python/)
STORY_PROTOCOL_API_KEY=your_api_key_here
Frontend
Configure API_BASE_URL in your React configuration to point to http://localhost:8000
Troubleshooting
"Cannot connect to backend"

Ensure the FastAPI server is running on http://localhost:8000
Check that the virtual environment is activated
Verify no other service is using port 8000

"Module not found" errors

Make sure you've activated the virtual environment
Run pip install -r requirements.txt in the server-python/ directory

Frontend can't reach backend

Confirm the backend is running
Check CORS settings in app.py
Verify the API base URL in frontend configuration

Technology Stack

Frontend: React, Vite, JavaScript
Backend: FastAPI, Python
Vector Database: ChromaDB
AI/ML: Image embedding models (details in model_tools.py)

License
MIT
Author
Uwakmfon Ibanga
Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
Support
For setup assistance, refer to this README or check the GitHub repository issues section.
