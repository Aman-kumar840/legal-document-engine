import os
import json
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize clients and embedding model
client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
client_qdrant = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

# Use the exact same encoder model used during seeding
encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

MODEL_NAME = "llama-3.3-70b-versatile"
COLLECTION_NAME = "legal_clauses"

def compare_with_market_benchmarks(clause_text: str, clause_type: str) -> dict:
    """
    Vectorizes the input clause, queries Qdrant for market examples from the CUAD dataset,
    and asks Llama 3.3 to determine if the clause matches standard market norms.
    """
    try:
        # 1. Convert the input clause into a mathematical vector embedding
        query_vector = encoder.encode(clause_text).tolist()
        
        # 2. Query Qdrant Cloud for the top 2 closest matching real-world examples
        search_result = client_qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=2
        )
        
        # Extract the text of the matched historical clauses
        matched_examples = []
        for hit in search_result:
            matched_examples.append(f"- \"{hit.payload.get('text')}\" (Type: {hit.payload.get('type')})")
            
        market_context = "\n".join(matched_examples) if matched_examples else "No exact market matches found."

        # 3. Use Groq to analyze the delta between the uploaded clause and market context
        system_prompt = """
        You are an expert commercial contract auditor. You are given an uploaded contract clause and a list of standard market benchmark clauses from the CUAD database.
        Your job is to compare them and determine if the uploaded clause is standard, favorable, or unfavorable (aggressive) to the signing party compared to standard market norms.
        
        You must output ONLY a valid JSON object with exactly two keys: 'market_status' (string value: either 'Standard', 'Favorable', or 'Unfavorable') and 'market_comparison_analysis' (a brief sentence explaining why).
        Do not include markdown tags like ```json.
        """
        
        user_payload = f"""
        Uploaded Clause Type: {clause_type}
        Uploaded Clause Text: {clause_text}
        
        Real-world Market Examples Found in DB:
        {market_context}
        """
        
        response = client_groq.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_payload}
            ],
            model=MODEL_NAME,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        raw_output = response.choices[0].message.content
        if raw_output.startswith("```json"):
            raw_output = raw_output.replace("```json", "").replace("```", "").strip()
            
        return json.loads(raw_output)
        
    except Exception as e:
        print(f"Error in Comparator Agent execution: {e}")
        return {"market_status": "Unknown", "market_comparison_analysis": "Could not verify against vector database standard templates."}

# Local Testing Sandbox Block
if __name__ == "__main__":
    print("Testing Comparator Agent against Qdrant Cloud Vector Store...")
    # This clause matches our seeded 'Termination' index clause closely
    sample_clause = "Either party can cancel this agreement by providing a 30-day prior written notice statement to the other."
    sample_type = "Termination"
    
    analysis = compare_with_market_benchmarks(sample_clause, sample_type)
    print(json.dumps(analysis, indent=2))