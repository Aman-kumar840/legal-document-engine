import requests
import json
import sys

API_URL = "http://127.0.0.1:8000/api/audit"
PDF_PATH = "sample.pdf"

def test_api():
    print(f"🚀 Initiating API request to {API_URL}...")
    
    try:
        # Open the PDF in binary read mode
        with open(PDF_PATH, "rb") as pdf_file:
            # Create a dictionary to hold the file payload
            files = {"file": (PDF_PATH, pdf_file, "application/pdf")}
            
            print(f"📤 Uploading {PDF_PATH} to the engine...")
            # Send the POST request to our FastAPI endpoint
            response = requests.post(API_URL, files=files)
            
        # Check if the server responded with a 200 OK success code
        if response.status_code == 200:
            print("\n✅ SUCCESS! The API processed the document. Here is the JSON payload:\n")
            # Print the formatted JSON response
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\n❌ API Error {response.status_code}:")
            print(response.text)
            
    except FileNotFoundError:
        print(f"❌ Error: Could not find '{PDF_PATH}'. Please put a PDF in this folder and name it '{PDF_PATH}'.")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API. Is your Uvicorn server running in the other terminal?")

if __name__ == "__main__":
    test_api()