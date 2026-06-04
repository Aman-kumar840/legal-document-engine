import json
from backend.app.graph import app_graph

if __name__ == "__main__":
    print("🚀 Initializing Legal Document Engine End-to-End Test Pipeline...")
    
    # A mock aggressive contract string containing standard and dangerous clauses
    mock_contract = """
    CONFIDENTIALITY AGREEMENT
    1. The Receiving Party agrees not to disclose any proprietary data to third parties.
    2. This Agreement may be terminated by either party upon thirty (30) days prior written notice.
    3. All intellectual property created, designed, or developed by the Contractor prior to or during this agreement shall immediately transfer and belong exclusively to the Company without any additional compensation.
    """
    
    # Fire up the engine!
    initial_state = {"raw_text": mock_contract}
    final_output = app_graph.invoke(initial_state)
    
    print("\n================== 🎯 FINAL AUDIT REPORT ==================")
    print(json.dumps(final_output["final_report"], indent=2))
    print("\n================== 🔍 DETAILED CLAUSE METRICS =============")
    print(json.dumps(final_output["audited_clauses"], indent=2))