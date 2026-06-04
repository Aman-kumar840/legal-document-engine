import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.3-70b-versatile"

def generate_summary(analyzed_clauses: list) -> dict:
    """
    Takes the full list of analyzed clauses (with risk scores and market comparisons)
    and generates an executive summary and a list of critical red flags.
    """
    system_prompt = """
    You are a Lead Corporate Attorney. You are reviewing an automated audit of a contract.
    You will be provided with a JSON list of clauses, their risk scores (1-10), and market context.
    
    Your job is to produce a final report containing:
    1. 'executive_summary': A concise, 2-3 sentence overview of the contract's overall risk profile.
    2. 'critical_flags': A brief list of the most dangerous clauses (scores 7-10) that need immediate renegotiation. If none exist, return an empty list.
    
    You must output ONLY a valid JSON object. Do not include markdown tags like ```json.
    
    Format required:
    {
      "executive_summary": "Overall, this contract is highly aggressive...",
      "critical_flags": ["The IP Ownership clause immediately transfers all rights without compensation."]
    }
    """

    user_payload = json.dumps(analyzed_clauses, indent=2)

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze these audited clauses:\n\n{user_payload}"}
            ],
            model=MODEL_NAME,
            temperature=0.2, # Slightly higher temperature for better natural language generation
            response_format={"type": "json_object"}
        )
        
        raw_output = response.choices[0].message.content
        
        if raw_output.startswith("```json"):
            raw_output = raw_output.replace("```json", "").replace("```", "").strip()
            
        return json.loads(raw_output)
        
    except Exception as e:
        print(f"Error in Summarizer Agent execution: {e}")
        return {"executive_summary": "Error generating summary.", "critical_flags": []}

# Local Testing Block
if __name__ == "__main__":
    print("Testing Summarizer Agent...")
    
    # Mock data representing the output from our previous agents
    mock_audit_data = [
        {
            "clause_text": "Either party may terminate upon 30 days notice.",
            "clause_type": "Termination",
            "risk_score": 2,
            "risk_reason": "Mutual and standard timeframe.",
            "market_status": "Standard"
        },
        {
            "clause_text": "Company owns all intellectual property created by Contractor forever, without additional pay.",
            "clause_type": "IP Ownership",
            "risk_score": 9,
            "risk_reason": "Highly aggressive one-sided IP grab.",
            "market_status": "Unfavorable"
        }
    ]
    
    final_report = generate_summary(mock_audit_data)
    print(json.dumps(final_report, indent=2))