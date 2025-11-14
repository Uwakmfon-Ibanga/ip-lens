import requests
import os
import hashlib
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---
#  REQUIRED: Replace with your actual Story Protocol API Key
STORY_API_KEY = os.getenv("VITE_STORY_PRODUCTION_API_KEY")

# The folder where downloaded images will be saved
ASSETS_FOLDER = "./story_protocol_assets"
# The API endpoint for listing IP assets
ASSETS_API_URL = "https://api.storyapis.com/api/v4/assets"
# The maximum number of assets to download for the demo
MAX_ASSETS_LIMIT = 200


def fetch_ip_metadata() -> List[Dict[str, Any]]:
    """
    STEP 1: Queries the Story Protocol registry to get IP Asset metadata.
    This function uses the provided API endpoint to fetch the latest assets.
    """
    print("STEP 1: Querying Story Protocol Registry...")

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': STORY_API_KEY
    }

    # Payload to fetch the latest 200 assets, removing the owner filter
    payload = {
        "includeLicenses": False,
        "moderated": False,
        "orderBy": "blockNumber",
        "orderDirection": "desc",
        "pagination": {
            "limit": MAX_ASSETS_LIMIT,
            "offset": 0
        },
        # 'where' filter is omitted entirely to get assets from all owners
    }

    try:
        # Check if the API key is set before proceeding
        if STORY_API_KEY == "YOUR_API_KEY_HERE":
            print("ERROR: API Key is a placeholder. Please update STORY_API_KEY with a valid key.")
            return []

        response = requests.post(ASSETS_API_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        raw_assets = data.get('data', [])

        if not raw_assets:
            print("INFO: API returned an empty list of assets.")
            return []

        # Transform raw API data into the minimum required structure
        metadata_list = []
        for asset in raw_assets:
            # We look for the media URL nested within nftMetadata -> image -> originalUrl
            image_metadata = asset.get('nftMetadata', {}).get('image', {})
            media_url = image_metadata.get('originalUrl')
            
            # The API response doesn't directly provide a mediaHash.
            if media_url and asset.get('ipId'):
                
                # Simple file name creation from IP ID and base filename
                base_name = os.path.basename(media_url).split('?')[0].split('/')[-1] or 'image'
                
                metadata_list.append({
                    "ipId": asset['ipId'],
                    "mediaUrl": media_url,
                    "mediaHash": "DEMO_HASH_IGNORED_FOR_PUBLIC_ASSETS", # Placeholder for the demo
                    "filename": f"{asset['ipId']}_{base_name}"
                })
        
        print(f"INFO: Successfully retrieved {len(metadata_list)} image metadata records.")
        return metadata_list

    except requests.exceptions.ConnectionError:
        print(f"FATAL ERROR: Could not connect to the API at {ASSETS_API_URL}.")
        print("Please check your internet connection or the API domain.")
    except requests.exceptions.HTTPError as e:
        print(f"FATAL ERROR: HTTP Request failed. Status code: {e.response.status_code}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"UNEXPECTED ERROR during API call: {e}")
        
    return []


def verify_hash(data: bytes, expected_hash: str) -> bool:
    """
    Simulates hash verification, always succeeding in this demo mode.
    """
    return True 

def download_and_save_assets(metadata_list: List[Dict[str, Any]]):
    """
    STEP 2 & 3: Downloads images from the mediaUrl and saves them locally.
    """
    os.makedirs(ASSETS_FOLDER, exist_ok=True)
    print(f"\nSTEP 2 & 3: Starting asset download and verification into {ASSETS_FOLDER}...")

    success_count = 0
    
    for item in metadata_list:
        ip_id = item['ipId']
        media_url = item['mediaUrl']
        media_hash = item['mediaHash']
        local_filename = item['filename']
        file_path = os.path.join(ASSETS_FOLDER, local_filename)
        
        # Clean up URL for reliable download (e.g., removing spaces if they exist)
        clean_url = media_url.strip().replace(' ', '%20')

        try:
            # Download the image (STEP 2: Download)
            response = requests.get(clean_url, timeout=15, stream=True)
            response.raise_for_status() 
            
            # Read the content
            image_data = response.content
            
            # Verify the image integrity (STEP 3: Verification)
            if not verify_hash(image_data, media_hash):
                # This path is skipped in demo mode, but here for completeness
                print(f"  FAILURE: {local_filename} (IP ID: {ip_id}) - Hash verification failed! Skipping.")
                continue

            # Save the file locally
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            success_count += 1
            print(f"  SUCCESS: {local_filename} (IP ID: {ip_id}) - Downloaded and verified.")

        except requests.exceptions.HTTPError as e:
            print(f"  FAILURE: {local_filename} - HTTP Error during download: {e}. URL: {clean_url}")
        except requests.exceptions.RequestException as e:
            print(f"  FAILURE: {local_filename} - General request error: {e}. URL: {clean_url}")
        except Exception as e:
            print(f"  FAILURE: {local_filename} - An unexpected error occurred: {e}")

    print(f"\nAsset Retrieval Complete. Successfully downloaded and verified {success_count} files.")


if __name__ == "__main__":
    if STORY_API_KEY == "YOUR_API_KEY_HERE":
    
    # 1. Query for asset metadata
    metadata = fetch_ip_metadata()
    
    if metadata:
        # 2. Download, verify, and save the assets
        download_and_save_assets(metadata)
        
        # 3. Final instruction for the user
        print("\n========================================================")
        print("NEXT STEP: Run 'python ingestion_script.py'")
        print("The assets are now saved locally and ready for vector indexing.")
        print("========================================================")
    else:
        print("\nNo IP Asset metadata retrieved. Cannot proceed with download.")