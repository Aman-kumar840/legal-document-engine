import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize the Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# The specific model we want to use (Llama 3 70B is incredibly smart for parsing)
MODEL_NAME = "llama-3.3-70b-versatile"

def extract_clauses(text_chunk: str) -> list:
    """
    Takes a chunk of raw contract text and uses Llama 3 to extract 
    distinct legal clauses into a structured JSON format.
    """
    
    # The system prompt acts as the "Brain" setup for the agent
    system_prompt = """
    You are an elite legal data extraction tool. Your ONLY job is to extract distinct legal clauses from the provided text.
    You must classify the 'type' of clause (e.g., Liability, Termination, IP Ownership, Payment, Confidentiality, General).
    
    You must reply ONLY with a valid JSON array of objects. Do not include markdown formatting like ```json or any conversational text.
    
    Format required:
    [
      {
        "clause_text": "The exact wording of the clause here.",
        "clause_type": "The Category"
      }
    ]
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract clauses from this text:\n\n{text_chunk}"}
            ],
            model=MODEL_NAME,
            temperature=0.1, # Keep this very low so the AI doesn't hallucinate or get creative
            # This is a special Groq feature that forces the output to be strictly JSON
            response_format={"type": "json_object"} 
        )
        
        # Groq's json_object mode requires a root key, so we parse it carefully
        # Note: If json_object fails, we fall back to standard string parsing
        raw_output = response.choices[0].message.content
        
        # Strip potential markdown if the model ignores the prompt instruction
        if raw_output.startswith("```json"):
            raw_output = raw_output.replace("```json", "").replace("```", "").strip()
            
        # We wrap the expected array in a dictionary to satisfy Groq's JSON mode constraints
        # But we need to handle whatever it spits out safely.
        try:
             parsed_json = json.loads(raw_output)
             # If the LLM returned a dict with an array inside (e.g., {"clauses": [...]})
             if isinstance(parsed_json, dict):
                 # Find the first list value in the dict
                 for key, value in parsed_json.items():
                     if isinstance(value, list):
                         return value
                 return [parsed_json] # Fallback if it just returned a single object
             return parsed_json if isinstance(parsed_json, list) else []
        except json.JSONDecodeError:
            print("Failed to parse JSON. Raw output was:", raw_output)
            return []
            
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return []

# Quick local test block
if __name__ == "__main__":
    sample_text = """
    8. TERMINATION. This Agreement may be terminated by either party upon thirty (30) days prior written notice.
    9. CONFIDENTIALITY. The Receiving Party agrees not to disclose any proprietary data to third parties.
    """
    print("Testing Extractor Agent...")
    results = extract_clauses(sample_text)
    print(json.dumps(results, indent=2))