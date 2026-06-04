import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Simple health check flag
ISCONFIGURED = all([GROQ_API_KEY, QDRANT_URL, QDRANT_API_KEY])

if __name__ == "__main__":
    print(f"Environment Loaded Successfully: {ISCONFIGURED}")
    if not ISCONFIGURED:
        print("Missing variables detected! Check your .env assignments.")