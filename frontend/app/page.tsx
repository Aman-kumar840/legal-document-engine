"use client";

import { useState } from "react";
import { UploadCloud, FileText, AlertTriangle, ShieldCheck, Activity, Download } from "lucide-react";
import jsPDF from "jspdf";
import { toPng } from "html-to-image";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setReport(null);
      setError("");
    }
  };

  const runAudit = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/audit", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to analyze the document. Check your backend.");
      }

      const data = await response.json();
      setReport(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

 // PDF Download Handler
 const downloadPDF = async () => {
  const element = document.getElementById("audit-report-container");
  if (!element) return;

  try {
    // Use html-to-image instead of html2canvas
    const dataUrl = await toPng(element, { 
      backgroundColor: '#f8fafc', // matches slate-50
      pixelRatio: 2 // Keeps the text crisp
    });
    
    const pdf = new jsPDF("p", "mm", "a4");
    const imgWidth = 210; // A4 size width in mm
    const pageHeight = 297; // A4 size height in mm
    
    // Calculate height based on the DOM element's aspect ratio
    const imgHeight = (element.offsetHeight * imgWidth) / element.offsetWidth;
    let heightLeft = imgHeight;
    let position = 0;

    pdf.addImage(dataUrl, "PNG", 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    // If the report is long, add new pages dynamically
    while (heightLeft > 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(dataUrl, "PNG", 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    pdf.save(`AI_Audit_Report_${report?.filename || "document"}.pdf`);
  } catch (err) {
    console.error("Error generating PDF: ", err);
  }
};

  const getRiskColor = (score: number) => {
    if (score >= 7) return "bg-red-100 text-red-800 border-red-300";
    if (score >= 4) return "bg-yellow-100 text-yellow-800 border-yellow-300";
    return "bg-green-100 text-green-800 border-green-300";
  };

  return (
    <main className="min-h-screen bg-slate-50 p-8 font-sans text-slate-900">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Header Section */}
        <header className="text-center space-y-2">
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">
            Legal Document Engine
          </h1>
          <p className="text-slate-500 text-lg">
            AI-powered contract auditing and risk analysis.
          </p>
        </header>

        {/* Upload Section */}
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 text-center space-y-6">
          <div className="flex justify-center">
            <div className="p-4 bg-indigo-50 text-indigo-600 rounded-full">
              <UploadCloud size={40} />
            </div>
          </div>
          
          <div>
            <label className="cursor-pointer bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition">
              Select PDF Document
              <input type="file" accept=".pdf" className="hidden" onChange={handleFileChange} />
            </label>
            {file && <p className="mt-4 text-sm text-slate-600 font-medium">Selected: {file.name}</p>}
          </div>

          <button
            onClick={runAudit}
            disabled={!file || isAnalyzing}
            className={`w-full py-4 rounded-xl font-bold text-lg transition flex justify-center items-center gap-2
              ${!file || isAnalyzing ? "bg-slate-100 text-slate-400 cursor-not-allowed" : "bg-slate-900 text-white hover:bg-slate-800 shadow-md"}
            `}
          >
            {isAnalyzing ? (
              <>
                <Activity className="animate-spin" /> Analyzing Document...
              </>
            ) : (
              "Run AI Audit"
            )}
          </button>

          {error && <p className="text-red-500 font-medium">{error}</p>}
        </div>

        {/* Exportable Wrapper Component */}
        {report && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {/* Quick Export Panel */}
            <div className="flex justify-end">
              <button 
                onClick={downloadPDF}
                className="flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5 rounded-xl font-semibold shadow hover:bg-indigo-700 transition"
              >
                <Download size={18} /> Export Audit PDF
              </button>
            </div>

            {/* Target Export Section */}
            <div id="audit-report-container" className="space-y-6 p-4 bg-slate-50 rounded-2xl">
              
              {/* Executive Summary */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
                <h2 className="text-xl font-bold flex items-center gap-2 border-b pb-4">
                  <FileText className="text-indigo-600"/> Executive Summary
                </h2>
                <p className="text-slate-700 leading-relaxed text-lg">
                  {report.summary.executive_summary}
                </p>
                
                {report.summary.critical_flags.length > 0 && (
                  <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg mt-4">
                    <h3 className="font-bold text-red-800 flex items-center gap-2 mb-2">
                      <AlertTriangle size={20}/> Critical Red Flags Detected
                    </h3>
                    <ul className="list-disc pl-5 text-red-700 space-y-1">
                      {report.summary.critical_flags.map((flag: string, idx: number) => (
                        <li key={idx}>{flag}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Detailed Clause Metrics */}
              <h2 className="text-2xl font-bold pt-4 text-slate-900">Detailed Clause Analysis</h2>
              <div className="grid gap-4">
                {report.clauses.map((clause: any, index: number) => (
                  <div key={index} className={`p-5 rounded-xl border ${getRiskColor(clause.risk_score)}`}>
                    <div className="flex justify-between items-start mb-3">
                      <span className="font-bold uppercase tracking-wider text-sm opacity-80">
                        {clause.clause_type}
                      </span>
                      <span className="font-black text-lg">
                        Risk Score: {clause.risk_score}/10
                      </span>
                    </div>
                    <p className="italic opacity-90 mb-4 text-sm bg-white/40 p-3 rounded-lg border border-white/50 text-slate-800">
                      "{clause.clause_text}"
                    </p>
                    
                    <div className="space-y-2 mt-4 text-sm">
                      <p><strong>AI Verdict:</strong> {clause.risk_reason}</p>
                      <div className="flex items-start gap-2 pt-2 border-t border-black/10">
                        <ShieldCheck size={18} className="mt-0.5 opacity-70"/>
                        <p>
                          <strong>Market Status ({clause.market_status}):</strong> {clause.market_comparison_analysis}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

            </div>
            
          </div>
        )}
      </div>
    </main>
  );
}