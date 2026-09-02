import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import our custom modules
from app.utils.pdf_parser import extract_clean_text_from_pdf
from app.graph import app_graph

app = FastAPI(title="Legal Document Engine API")

# Allow frontend applications to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def health_check():
    return {"status": "Legal Engine is running smoothly! 🚀"}

@app.post("/api/audit")
async def audit_contract(file: UploadFile = File(...)):
    """
    Receives a PDF upload, parses the text, runs the LangGraph AI pipeline, 
    and returns the structured JSON audit report.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # 1. Save the uploaded file temporarily
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2. Parse the PDF into raw text using PyMuPDF
        print(f"\n📄 Parsing {file.filename}...")
        raw_text = extract_clean_text_from_pdf(file_path)
        
        # Guardrail: Limit text size to prevent exceeding Groq token limits on massive PDFs
        safe_text = raw_text[:15000] 

        # 3. Feed the text into the LangGraph AI Pipeline
        print("🚀 Starting Multi-Agent AI Graph Execution...")
        initial_state = {"raw_text": safe_text}
        final_output = app_graph.invoke(initial_state)

        # 4. Return the structured results to the frontend
        print("✅ Audit Complete! Sending payload back to client.")
        return {
            "status": "success",
            "filename": file.filename,
            "summary": final_output.get("final_report", {}),
            "clauses": final_output.get("audited_clauses", [])
        }

    except Exception as e:
        print(f"❌ Error during audit: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while analyzing the document.")
    finally:
        # 5. Clean up the temporary file so we don't clog up the server storage
        if os.path.exists(file_path):
            os.remove(file_path)