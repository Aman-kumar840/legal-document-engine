import os
import sys
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Ensure the script can see app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "legal_clauses"

# 1. Standard sample legal clause dataset (Simulating processed CUAD records)
SAMPLE_CUAD_CLAUSES = [
    {
        "text": "Neither party may assign this Agreement or any of its rights or obligations hereunder without the prior written consent of the other party.",
        "type": "Assignment",
        "standard": True
    },
    {
        "text": "Company shall retain exclusive ownership of all intellectual property, inventions, and work product developed or created prior to or during the engagement.",
        "type": "IP Ownership",
        "standard": True
    },
    {
        "text": "Either party may terminate this Agreement at any time, with or without cause, upon giving thirty (30) days written notice to the other party.",
        "type": "Termination",
        "standard": True
    },
    {
        "text": "In no event shall either party be liable to the other for any indirect, incidental, special, punitive, or consequential damages arising out of this agreement.",
        "type": "Limitation of Liability",
        "standard": True
    },
    {
        "text": "Each party agrees to maintain the confidentiality of all proprietary information received from the other party and use it solely for the purpose of this engagement.",
        "type": "Confidentiality",
        "standard": True
    }
]

def seed_database():
    print("Initializing Qdrant Cloud Client...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    print("Loading local embedding model (all-MiniLM-L6-v2)...")
    # This downloads a lightweight, fast local vector model (around 90MB)
    encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    vector_dimension = 384 # Dimension size for all-MiniLM-L6-v2
    
    # 2. Setup the target vector collection
    print(f"Checking if collection '{COLLECTION_NAME}' exists...")
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if not exists:
        print(f"Creating a fresh collection '{COLLECTION_NAME}' with dimension {vector_dimension}...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_dimension, distance=Distance.COSINE),
        )
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists. Preparing data batch upload...")

    # 3. Generate vectors and structural payloads
    points = []
    for idx, item in enumerate(SAMPLE_CUAD_CLAUSES):
        print(f"Encoding clause [{item['type']}]...")
        vector = encoder.encode(item["text"]).tolist()
        
        points.append(
            PointStruct(
                id=idx,
                vector=vector,
                payload={
                    "text": item["text"],
                    "type": item["type"],
                    "is_standard": item["standard"]
                }
            )
        )
        
    # 4. Upsert vectors to Qdrant Cloud
    print(f"Uploading {len(points)} vectors to Qdrant Cloud...")
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print("🚀 Qdrant Vector Knowledge Base successfully seeded!")

if __name__ == "__main__":
    seed_database()