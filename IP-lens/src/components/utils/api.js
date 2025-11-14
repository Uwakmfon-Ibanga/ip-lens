const API_KEY = 'KOTbaGUSWQ6cUJWhiJYiOjPgB0kTRu1eCFFvQL0IWls'; // Your Testnet API Key
const BASE_URL = 'https://staging-api.storyprotocol.net'; // Staging/Testnet Endpoint
const SEARCH_PATH = '/api/v4/search';
const ENDPOINT = BASE_URL + SEARCH_PATH;

const requestBody = {
  mediaType: "image",
  pagination: {
    limit: 20,
    offset: 0
  },
  query: "dragon NFT"
};

export async function searchApi() {
  try {
    const response = await fetch(ENDPOINT, {
      method: 'POST',
      headers: {
        // Specify that the request body is JSON
        'Content-Type': 'application/json',
        // Pass the required API key for authentication
        'X-Api-Key': API_KEY
      },
      // Convert the JavaScript object to a JSON string
      body: JSON.stringify(requestBody) 
    });

    // Check if the response was successful (status code 200-299)
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    // Parse the JSON response body
    const data = await response.json();
    console.log('Search Results:', data);
    
    // You can process the 'data' object here

  } catch (error) {
    console.error('There was a problem with the fetch operation:', error);
  }
}

// Call the function to execute the request
searchApi();