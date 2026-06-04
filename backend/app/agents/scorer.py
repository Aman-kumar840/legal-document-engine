import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.3-70b-versatile"

def score_clause_risk(clause_text: str, clause_type: str) -> dict:
    """
    Analyzes a single legal clause and scores its potential risk to the 
    signing party from 1 (Safe) to 10 (Extremely Dangerous) with a clear reason.
    """
    
    system_prompt = """
    You are an expert corporate legal counsel specializing in risk assessment and contract audits.
    Your task is to analyze a single contract clause and assign a numeric risk score from 1 to 10 based on how dangerous, non-standard, or one-sided it is against the signing party.
    
    Risk Scale Context:
    - 1-3: Standard, low-risk, mutual protection.
    - 4-6: Moderately aggressive, slightly one-sided, warrants observation.
    - 7-10: Extremely aggressive, dangerous, high liability or unfair intellectual property transfers.
    
    You must output ONLY a valid JSON object with exactly two keys: 'risk_score' (as an integer) and 'risk_reason' (a concise, plain-English sentence).
    Do not include markdown tags like ```json.
    
    Format required:
    {
      "risk_score": 8,
      "risk_reason": "Explanation of the trap or severe consequence."
    }
    """

    user_payload = f"Clause Type: {clause_type}\nClause Text: {clause_text}"

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_payload}
            ],
            model=MODEL_NAME,
            temperature=0.1,  # Keep reasoning deterministic
            response_format={"type": "json_object"}
        )
        
        raw_output = response.choices[0].message.content
        
        # Clean up possible markdown artifacts if present
        if raw_output.startswith("```json"):
            raw_output = raw_output.replace("```json", "").replace("```", "").strip()
            
        parsed_score = json.loads(raw_output)
        return parsed_score
        
    except Exception as e:
        print(f"Error calling Groq Risk Scorer: {e}")
        return {"risk_score": 1, "risk_reason": "Error parsing risk parameters."}

# Local Unit Testing Block
if __name__ == "__main__":
    test_clause = "All intellectual property created, designed, or developed by the Contractor prior to or during this agreement shall immediately transfer and belong exclusively to the Company without any additional compensation."
    test_type = "IP Ownership"
    
    print("Testing Risk Scorer Agent...")
    score_result = score_clause_risk(test_clause, test_type)
    print(json.dumps(score_result, indent=2))