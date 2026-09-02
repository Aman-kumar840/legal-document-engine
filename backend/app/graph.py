import os
import json
from typing import List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# Import your specialized agents
from app.agents.extractor import extract_clauses
from app.agents.scorer import score_clause_risk
from app.agents.comparator import compare_with_market_benchmarks
from app.agents.summarizer import generate_summary

# 1. Define the State Structure that flows between agents
class State(TypedDict):
    raw_text: str
    extracted_clauses: List[Dict[str, Any]]
    audited_clauses: List[Dict[str, Any]]
    final_report: Dict[str, Any]

# 2. Define Node 1: Extraction
def extraction_node(state: State) -> Dict[str, Any]:
    print("🤖 [Node: Extractor] Parsing document into target clauses...")
    clauses = extract_clauses(state["raw_text"])
    return {"extracted_clauses": clauses}

# 3. Define Node 2: Clause Analyzer (Combines Scoring & Comparison)
def analysis_node(state: State) -> Dict[str, Any]:
    print(f"🤖 [Node: Analyzer] Processing {len(state['extracted_clauses'])} clauses...")
    audited_list = []
    
    for clause in state["extracted_clauses"]:
        text = clause.get("clause_text", "")
        ctype = clause.get("clause_type", "")
        
        print(f"   ↳ Auditing '{ctype}' clause...")
        # Run Scorer and Comparator agents
        score_data = score_clause_risk(text, ctype)
        market_data = compare_with_market_benchmarks(text, ctype)
        
        # Merge all findings into a unified clause object
        audited_clause = {
            **clause,
            "risk_score": score_data.get("risk_score", 1),
            "risk_reason": score_data.get("risk_reason", ""),
            "market_status": market_data.get("market_status", "Unknown"),
            "market_comparison_analysis": market_data.get("market_comparison_analysis", "")
        }
        audited_list.append(audited_clause)
        
    return {"audited_clauses": audited_list}

# 4. Define Node 3: Executive Summary Compiler
def summarizer_node(state: State) -> Dict[str, Any]:
    print("🤖 [Node: Summarizer] Generating executive summary and looking for critical red flags...")
    report = generate_summary(state["audited_clauses"])
    return {"final_report": report}

# 5. Construct the State Graph Workflow
workflow = StateGraph(State)

# Add our processing units
workflow.add_node("extractor", extraction_node)
workflow.add_node("analyzer", analysis_node)
workflow.add_node("summarizer", summarizer_node)

# Set the directional pipeline execution flow
workflow.add_edge(START, "extractor")
workflow.add_edge("extractor", "analyzer")
workflow.add_edge("analyzer", "summarizer")
workflow.add_edge("summarizer", END)

# Compile the compiled executable graph
app_graph = workflow.compile()