import React, { useState, useRef, useMemo } from "react";

const ImageUpload = () => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [fileDataUrl, setFileDataUrl] = useState(null);
  const [fileDetails, setFileDetails] = useState({
    name: null,
    type: null,
    size: null,
  });
  // State to hold the URL of the image selected for comparison
  const [comparedImage, setComparedImage] = useState(null);
  

  // New state for search results
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [score, setScore] = useState(null);

  const fileInputRef = useRef(null);

  const isImage = useMemo(
    () => fileDetails.type?.startsWith("image/"),
    [fileDetails.type]
  );
  const isProcessable = useMemo(
    () => isImage && uploadedFile,
    [isImage, uploadedFile]
  );

  // Base URL for the FastAPI server
  const API_BASE_URL = "http://localhost:8000";

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSearchResults([]); // Clear previous results
    setComparedImage(null); // Clear comparison image

    if (file) {
      setUploadedFile(file);
      setFileDetails({ name: file.name, type: file.type, size: file.size });

      const reader = new FileReader();
      reader.onloadend = () => {
        setFileDataUrl(reader.result);
      };

      reader.readAsDataURL(file);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  // Performs vector generation AND search
  const handleSearchSimilarity = async () => {
    if (!uploadedFile || !isImage) return;

    setIsLoading(true);
    setSearchResults([]);
    setComparedImage(null); // Clear comparison when starting a new search

    const formData = new FormData();
    formData.append("file", uploadedFile);

    try {
      const response = await fetch(`${API_BASE_URL}/search-vector`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          `Server Error (${response.status}): ${
            errorData.detail || response.statusText
          }`
        );
      }

      const data = await response.json();

      setSearchResults(data.results || []);
    } catch (error) {
      console.error("Error during similarity search:", error);
      alert(`Search failed: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Takes the Similarity Score (0 to 1) as input
  

  // Helper function to create the correct URL path
  const createLocalImageUrl = (filename) => {
    return `${API_BASE_URL}/assets/${filename}`;
  };

  return (
    <div className="flex flex-wrap justify-center gap-9 bg-gray-100 p-1 sm:p-8 min-h-screen">
      {/* --- Left Column: Image Upload and Search Button --- */}
      <div className="flex flex-col gap-3 items-center p-9 rounded-2xl shadow-xl w-[45%] h-fit top-4">
        <div>
          <h1 className="text-[#5352B2] font-semibold text-[32px]">
            IP Vector Similarity Search
          </h1>
          <p className="font-medium text-[20px] text-black opacity-50">
            Upload an Image to generate it’s OpenCLIP vector
          </p>
        </div>

        {/* Upload Area */}
        <div
          className={`
             rounded-2xl overflow-hidden cursor-pointer relative size-[400px] 
            transition-all duration-300 shadow-lg bg-linear-120 from-[#DCDEFEE8] to-[#EACFDDEB]
            hover:shadow-2xl hover:scale-[1.01] border-[#1849D6]
            ${
              fileDataUrl ? " border-4 border-dashed" : "border-4 border-dashed"
            }
            flex flex-col justify-center items-center p-4 sm:p-8
          `}
          onClick={() => {handleUploadClick(), handleSearchSimilarity();}}
          
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept="image/*"
          />

          {fileDataUrl ? (
            <>
              {isImage ? (
                <img
                  src={fileDataUrl}
                  alt={`Preview of ${fileDetails.name}`}
                  className="w-full h-full object-contain max-h-96 rounded-xl"
                />
              ) : (
                <div className="flex flex-col items-center justify-center w-full h-full text-gray-700 p-4">
                  <p className="font-semibold text-xl text-center break-all">
                    {fileDetails.name}
                  </p>
                </div>
              )}
            </>
          ) : (
            <div className="text-center p-4 flex flex-col items-center">
              <img className="size-[50px]" src="/folder.png" alt="folder" />
              <p className="text-gray-600 font-medium text-lg">
                Click to browse or drag file here
              </p>
              <p className="text-gray-400 text-sm mt-1">Image files only</p>
            </div>
          )}
        </div>

        {/* File Details */}
        <div className=" p-4 bg-gray-100 rounded-lg shadow-inner max-w-xl w-full text-sm">
          <p className="font-semibold text-gray-700 mb-2">
            Query Asset Details:
          </p>
          <ul className="list-none p-0 text-gray-600 space-y-1">
            <li>
              <span className="font-medium">File Name:</span>{" "}
              {fileDetails.name || "N/A"}
            </li>
            <li>
              <span className="font-medium">File Type:</span>{" "}
              {fileDetails.type || "N/A"}
            </li>
          </ul>
        </div>

        {/* Action Button */}
        <button
          onClick={handleSearchSimilarity}
          disabled={!isProcessable || isLoading}
          className={`
             px-8 py-3 cursor-pointer hover:bg-blue-600 rounded-xl font-bold text-lg flex items-center justify-center gap-2
            shadow-lg transition-all duration-200 w-full max-w-xs
            ${
              isProcessable && !isLoading
                ? "bg-[#615FFF] hover:bg-[#615FFF] text-white"
                : "bg-gray-300 text-gray-600 cursor-not-allowed"
            }
          `}
        >
          {isLoading ? (
            <>Searching Database...</>
          ) : (
            <>Generate IP Vector</>
          )}
        </button>
      </div>






      {
        uploadedFile && (
          <div className="w-[45%] flex flex-col gap-6">
        {/* --- Middle Column: Comparison View (Appears only when comparedImage is set) --- */}
      {comparedImage && (
        <div className="flex flex-col items-center justify-center p-4 rounded-2xl w-full h-fit top-4">
          <div className="flex gap-3 items-center">
            <div className=" p-2 rounded-xl bg-blue-100 size-fit">
              <img
                src={fileDataUrl}
                alt="Query Image"
                className=" size-70 object-contain rounded-lg border border-gray-200"
              />
            </div>
            
            <div className=" p-2 rounded-xl bg-blue-100 size-fit">
              <img
                src={comparedImage}
                alt="Compared Image"
                className=" size-70 object-contain rounded-lg border border-gray-200"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src =
                    "https://placehold.co/256x256/f0f4f8/94a3b8?text=NO+IMG";
                }}
              />
            </div>
          </div>
          <span className="mt-4 font-semibold  bg-[#615FFF] rounded-md text-white text-base p-3  text-center  w-full">Similarity Score: {(score * 100).toFixed(2)}%</span>
          <button
            onClick={() => setComparedImage(null)}
            className="mt-6 px-4 py-2 text-sm bg-[#5352B2] text-white rounded-lg hover:bg-[#7371ce] transition-colors shadow-md"
          >
            Clear Comparison
          </button>

        </div>
      )}

      {/* --- Right Column: Search Results --- */}
          {uploadedFile && (
            <div
              className={`w-full ${
                comparedImage ? "lg:col-span-1" : "lg:col-span-1"
              }`}
            >
              <h2 className="text-[#5352B2] font-semibold text-[32px]">
                Similarity Results ({searchResults.length})
              </h2>

              {searchResults.length > 0 && (
                <p className="font-medium text-[20px] text-black opacity-50">
                  Found {searchResults.length} similar IP Assets in the
                  database. Click on a result to compare it.
                </p>
              )}

              {isLoading && searchResults.length === 0 && (
                <div className="p-6 text-center bg-yellow-100 border border-yellow-300 rounded-xl text-yellow-800 font-medium">
                  Indexing and Searching... Please wait.
                </div>
              )}

              {/* Display Results */}
              <div className="grid grid-cols-1 gap-6 h-[36rem] overflow-y-auto">
                {searchResults.map((result, index) => {
                  // New calculation for a similarity score S between 0 and 1
                  const similarityScore = 1 - result.distance / 2;
                  ;

                  // Generate the URL for this specific result
                  const resultImageUrl = createLocalImageUrl(
                    result.metadata?.filename || result.id
                  );

                  return (
                    <div
                      // FIX: Wrapped the state setter in an anonymous function so it only runs on click
                      
                      key={result.id}
                      className="p-5 rounded-xl shadow-lg flex flex-col sm:flex-row gap-4 border-l-4 border-[#5352B2] hover:shadow-2xl transition-shadow cursor-pointer hover:bg-indigo-50"
                     >
                      {/* Thumbnail Area */}
                      <div className="sm:w-1/3 w-full">
                        <img
                          src={resultImageUrl}
                          alt={`Result ${index + 1}`}
                          className="w-full h-32 object-cover rounded-lg shadow-md border border-gray-200"
                          // Fallback for missing/broken images
                          onError={(e) => {
                            e.target.onerror = null;
                            e.target.src =
                              "https://placehold.co/128x128/f0f4f8/94a3b8?text=NO+IMG";
                          }}
                        />
                      </div>

                      {/* Details Area */}
                      <div className="sm:w-2/3">
                        <h3 className="text-xl font-semibold text-gray-900 mb-2 leading-tight">
                          IP Asset ID (Match #{index + 1})
                        </h3>

                        <p className="text-sm font-mono break-all bg-gray-100 p-2 rounded-md mb-3">
                          {result.id}
                        </p>

                        <div className="flex justify-between items-center text-sm">
                          <button onClick={() => {setComparedImage(resultImageUrl) ; setScore(similarityScore);}} className="bg-blue-600 p-2 cursor-pointer rounded-md hover:bg-blue-700 text-white font-medium">
                          Check Similarity Score
                          </button>
                      
                        </div>
                      </div>
                    </div>
                  );
                })}

                {/* Empty State */}
                {!isLoading && searchResults.length === 0 && (
                  <div className="p-8 text-center bg-gray-200 rounded-xl border-4 border-dashed border-gray-300 text-gray-600">
                    <p className="font-semibold text-lg">No results yet.</p>
                    <p className="text-sm">
                      Upload an image and click "Search" to find similar IP
                      Assets.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
      </div>
        )
      }
    </div>
  );
};

export default ImageUpload;
