import requests
import os

# --- Configuration ---
# Set this to the folder containing your Story Protocol images
IMAGE_FOLDER = "./story_protocol_assets"
# The endpoint on your running FastAPI server that adds the vector
ADD_VECTOR_URL = "http://127.0.0.1:8000/add-vector"
# List of image file extensions to process
ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')

def batch_ingestion():
    """
    Iterates through the IMAGE_FOLDER and uploads each image to the FastAPI server
    to be converted into a vector and stored in ChromaDB.
    """
    if not os.path.isdir(IMAGE_FOLDER):
        print(f"ERROR: Image folder not found at '{IMAGE_FOLDER}'.")
        print("Please create the folder and place your images inside.")
        return

    print("--- Starting Batch Ingestion ---")
    print(f"Targeting URL: {ADD_VECTOR_URL}")

    file_count = 0
    success_count = 0
    
    # Iterate through all files in the designated directory
    for filename in os.listdir(IMAGE_FOLDER):
        file_path = os.path.join(IMAGE_FOLDER, filename)
        
        # Check if it's a file and has an allowed image extension
        if os.path.isfile(file_path) and filename.lower().endswith(ALLOWED_EXTENSIONS):
            file_count += 1
            print(f"\nProcessing file {file_count}: {filename}")

            # Prepare the file for the POST request
            # Requests requires a dictionary mapping the form field name ('file') 
            # to a tuple (filename, file_object, mimetype)
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (filename, f, 'image/jpeg')}
                    
                    # Make the POST request to the /add-vector endpoint
                    response = requests.post(ADD_VECTOR_URL, files=files)

                # Check for successful HTTP status code
                if response.status_code == 200:
                    data = response.json()
                    success_count += 1
                    print(f"SUCCESS: {filename} added. New database count: {data.get('new_total_count', 'N/A')}")
                else:
                    # Handle API error response
                    error_detail = response.json().get('detail', 'No details provided.')
                    print(f"FAILURE: {filename} failed with status {response.status_code}. Detail: {error_detail}")

            except requests.exceptions.ConnectionError:
                print(f"FATAL ERROR: Could not connect to the server at {ADD_VECTOR_URL}.")
                print("Please ensure your FastAPI application is running!")
                return
            except Exception as e:
                print(f"UNEXPECTED ERROR processing {filename}: {e}")

    print("\n--- Batch Ingestion Complete ---")
    print(f"Total files attempted: {file_count}")
    print(f"Total files successfully added: {success_count}")

if __name__ == "__main__":
    batch_ingestion()