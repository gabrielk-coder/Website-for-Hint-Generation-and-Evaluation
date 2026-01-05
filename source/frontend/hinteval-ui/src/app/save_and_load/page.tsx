"use client";

import React, { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import {
  Download,
  Upload,
  FileJson,
  FileSpreadsheet,
  Save,
  Database,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  Code2,
  Copy,
  Check,
  Server,
  TableProperties,
  Info
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_HINTEVAL_API ?? "http://localhost:8000";

// --- UI COMPONENTS ---

const Badge = ({ children, color = "slate" }: { children: React.ReactNode, color?: "slate" | "indigo" | "purple" | "emerald" }) => {
  const styles = {
    slate: "bg-slate-800 text-slate-400 border-slate-700",
    indigo: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
    purple: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    emerald: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  };
  return (
    <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${styles[color]}`}>
      {children}
    </span>
  );
};

const CodeWindow = ({ code, filename, lang = "json" }: { code: string; filename: string, lang?: string }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-lg overflow-hidden border border-slate-800 bg-[#0d1117] shadow-inner">
      {/* Window Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-slate-700" />
            <div className="w-2.5 h-2.5 rounded-full bg-slate-700" />
          </div>
          <span className="text-xs font-mono text-slate-400 opacity-80">{filename}</span>
        </div>
        <button 
          onClick={copyToClipboard}
          className="text-xs text-slate-500 hover:text-white transition-colors flex items-center gap-1"
        >
          {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
        </button>
      </div>
      <div className="p-4 overflow-x-auto custom-scrollbar">
        <pre className="text-xs font-mono leading-relaxed text-slate-300">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );
};

// --- MAIN PAGE ---

export default function SaveLoadPage() {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "success" | "error">("idle");
  const [statusMsg, setStatusMsg] = useState("");
  const [activeGuideTab, setActiveGuideTab] = useState<"full" | "simple" | "csv">("full");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDownload = async (format: "json" | "csv" | "full_json") => {
    try {
      window.location.href = `${API}/save_and_load/export?format=${format}`;
    } catch (e) {
      alert("Failed to download session.");
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus("idle");
    setStatusMsg("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API}/save_and_load/import`, {
        method: "POST",
        body: formData,
        credentials: "include", 
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText);
      }

      const data = await res.json();
      setUploadStatus("success");
      setStatusMsg(data.info || "Session loaded successfully.");
      if (fileInputRef.current) fileInputRef.current.value = "";

    } catch (err: any) {
      setUploadStatus("error");
      setStatusMsg(err.message || "Failed to upload. Check the format guide below.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="bg-slate-950 min-h-screen text-slate-200 font-sans pb-20 selection:bg-indigo-500/30">
      
      {/* 1. Header Section */}
      <div className="bg-slate-900/50 border-b border-white/5 py-12">
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="space-y-2 text-center md:text-left">
              <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3 justify-center md:justify-start">
                <div className="p-2 bg-indigo-500/10 rounded-lg ring-1 ring-indigo-500/30">
                  <Database className="w-6 h-6 text-indigo-400" />
                </div>
                Data Management
              </h1>
              <p className="text-slate-400 text-sm max-w-md">
                Manage your session lifecycle. Export for analysis or import datasets to restore state.
              </p>
            </div>
            {/* Quick Stat or Info could go here if needed */}
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-10 max-w-6xl space-y-12">
        
        {/* 2. Main Actions Grid (Perfectly Symmetrical) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* LEFT: Export Panel */}
          <div className="flex flex-col h-full bg-slate-900/40 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-white/5 bg-gradient-to-r from-slate-900 to-slate-900/50">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Download className="w-5 h-5 text-indigo-400" /> Export Data
              </h2>
              <p className="text-xs text-slate-500 mt-1">Download your current workspace state.</p>
            </div>
            
            <div className="p-6 space-y-4 flex-1">
              {/* Primary Option */}
              <button 
                onClick={() => handleDownload("full_json")}
                className="w-full flex items-start gap-4 p-4 rounded-lg bg-indigo-500/5 border border-indigo-500/20 hover:bg-indigo-500/10 hover:border-indigo-500/40 transition-all group text-left"
              >
                <div className="p-3 bg-indigo-500/20 rounded-md text-indigo-400 group-hover:text-white group-hover:scale-110 transition-all">
                  <Server className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-slate-200 group-hover:text-white">Full Session Backup</span>
                    <Badge color="indigo">Recommended</Badge>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Preserves <span className="text-indigo-300">everything</span>: Question, Answer, Hints, Candidates, and Metrics. Use this to restore your work later.
                  </p>
                </div>
              </button>

              <div className="grid grid-cols-2 gap-4">
                {/* Secondary Option 1 */}
                <button 
                  onClick={() => handleDownload("json")}
                  className="flex flex-col items-start p-4 rounded-lg bg-slate-950 border border-slate-800 hover:border-slate-600 transition-all text-left"
                >
                  <FileJson className="w-5 h-5 text-slate-400 mb-3" />
                  <span className="font-bold text-sm text-slate-300 mb-1">Raw JSON</span>
                  <p className="text-[10px] text-slate-500">Inputs only. No metrics.</p>
                </button>

                {/* Secondary Option 2 */}
                <button 
                  onClick={() => handleDownload("csv")}
                  className="flex flex-col items-start p-4 rounded-lg bg-slate-950 border border-slate-800 hover:border-emerald-500/30 hover:bg-emerald-950/5 transition-all text-left"
                >
                  <FileSpreadsheet className="w-5 h-5 text-emerald-500/70 mb-3" />
                  <span className="font-bold text-sm text-slate-300 mb-1">CSV Export</span>
                  <p className="text-[10px] text-slate-500">Spreadsheet friendly.</p>
                </button>
              </div>
            </div>
          </div>

          {/* RIGHT: Import Panel */}
          <div className="flex flex-col h-full bg-slate-900/40 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-white/5 bg-gradient-to-r from-slate-900 to-slate-900/50">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Upload className="w-5 h-5 text-cyan-400" /> Import Session
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Restore a backup or load new questions. <span className="text-red-400/80">Overwrites current data.</span>
              </p>
            </div>

            <div className="p-6 flex-1 flex flex-col justify-center">
              <div 
                className={`flex-1 min-h-[220px] rounded-xl border-2 border-dashed transition-all flex flex-col items-center justify-center p-6 text-center cursor-pointer group relative overflow-hidden
                  ${uploadStatus === 'error' ? 'border-red-500/30 bg-red-950/5' : 
                    uploadStatus === 'success' ? 'border-emerald-500/30 bg-emerald-950/5' : 
                    'border-slate-700 hover:border-cyan-500/50 hover:bg-slate-950'}`}
                onClick={() => fileInputRef.current?.click()}
              >
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  className="hidden" 
                  accept=".json,.csv" 
                  onChange={handleFileUpload} 
                />

                {isUploading ? (
                  <div className="animate-pulse space-y-3">
                    <div className="p-4 bg-slate-800 rounded-full inline-block"><Upload className="w-8 h-8 text-slate-400" /></div>
                    <div className="text-sm font-bold text-slate-300">Processing file...</div>
                  </div>
                ) : uploadStatus === 'success' ? (
                  <div className="animate-in zoom-in-95 duration-300 space-y-4">
                    <div className="p-3 bg-emerald-500/20 rounded-full inline-block ring-1 ring-emerald-500/40">
                      <CheckCircle2 className="w-10 h-10 text-emerald-400" />
                    </div>
                    <div>
                      <div className="text-base font-bold text-white">Import Complete</div>
                      <div className="text-xs text-slate-400 mt-1 mb-4">{statusMsg}</div>
                    </div>
                    <Button 
                      size="sm"
                      onClick={(e) => { e.stopPropagation(); window.location.href = "/generation_and_evaluation"; }} 
                      className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold w-full"
                    >
                      Return to Generator <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                ) : uploadStatus === 'error' ? (
                  <div className="animate-in shake space-y-3">
                    <div className="p-3 bg-red-500/20 rounded-full inline-block ring-1 ring-red-500/40">
                      <AlertCircle className="w-10 h-10 text-red-400" />
                    </div>
                    <div>
                      <div className="text-base font-bold text-white">Import Failed</div>
                      <div className="text-xs text-red-300 mt-1 max-w-[280px] mx-auto">{statusMsg}</div>
                    </div>
                    <div className="text-[10px] text-slate-500 uppercase font-bold pt-2">Click to try again</div>
                  </div>
                ) : (
                  <div className="space-y-3 group-hover:scale-105 transition-transform duration-300">
                    <div className="p-4 bg-slate-900 rounded-full inline-block shadow-lg group-hover:shadow-cyan-900/20">
                      <Upload className="w-8 h-8 text-slate-400 group-hover:text-cyan-400 transition-colors" />
                    </div>
                    <div>
                      <div className="text-sm font-bold text-white">Click to upload file</div>
                      <div className="text-xs text-slate-500 mt-1">Supports .json or .csv</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 3. Documentation Section (Bottom, Full Width) */}
        <div className="border-t border-slate-800 pt-10">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-slate-800 rounded-lg">
              <Code2 className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Format Specification Guide</h3>
              <p className="text-xs text-slate-500">Ensure your imported files match these schemas.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Guide Sidebar Navigation */}
            <div className="space-y-2">
              <button 
                onClick={() => setActiveGuideTab("full")}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${activeGuideTab === "full" ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20" : "text-slate-400 hover:text-white hover:bg-slate-900"}`}
              >
                <Server className="w-4 h-4" /> Full Backup (JSON)
              </button>
              <button 
                onClick={() => setActiveGuideTab("simple")}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${activeGuideTab === "simple" ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20" : "text-slate-400 hover:text-white hover:bg-slate-900"}`}
              >
                <FileJson className="w-4 h-4" /> Raw Data (JSON)
              </button>
              <button 
                onClick={() => setActiveGuideTab("csv")}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${activeGuideTab === "csv" ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20" : "text-slate-400 hover:text-white hover:bg-slate-900"}`}
              >
                <TableProperties className="w-4 h-4" /> Batch CSV
              </button>
            </div>

            {/* Guide Content Window */}
            <div className="lg:col-span-3">
              {activeGuideTab === "full" && (
                <div className="animate-in fade-in slide-in-from-left-2 duration-300">
                  <div className="flex items-center gap-3 mb-2">
                    <Badge color="purple">System Format</Badge>
                    <span className="text-xs text-slate-400">Includes all application state. Use for complete restores.</span>
                  </div>
                  <CodeWindow 
                    filename="full_backup.json" 
                    code={`{
  "version": "v2.0",
  "question": "What is the capital of Brazil?",
  "answer": "Brasília",
  "hints": [
    { "hint_id": 1, "text": "It was founded in 1960." }
  ],
  "candidates": ["Rio", "Brasília", "São Paulo"],
  "metricsById": { 
    "1": { "convergence": 0.95, "relevance": 1.0 } 
  },
  "eliminationMap": {
    "1": [false, false, true]
  }
}`} 
                  />
                </div>
              )}

              {activeGuideTab === "simple" && (
                <div className="animate-in fade-in slide-in-from-left-2 duration-300">
                  <div className="flex items-center gap-3 mb-2">
                    <Badge color="slate">Simple Format</Badge>
                    <span className="text-xs text-slate-400">Basic structure for importing new questions.</span>
                  </div>
                  <CodeWindow 
                    filename="import_data.json" 
                    code={`{
  "question": "What is the capital of Brazil?",
  "answer": "Brasília",
  "hints": [
    "It was founded in 1960.",
    "Designed by Oscar Niemeyer."
  ]
}`} 
                  />
                </div>
              )}

              {activeGuideTab === "csv" && (
                <div className="animate-in fade-in slide-in-from-left-2 duration-300">
                  <div className="flex items-center gap-3 mb-2">
                    <Badge color="emerald">Spreadsheet Format</Badge>
                    <span className="text-xs text-slate-400">Columns must match exactly. Order does not matter.</span>
                  </div>
                  <CodeWindow 
                    filename="batch_import.csv" 
                    lang="csv"
                    code={`type,content
question,What is the capital of Brazil?
answer,Brasília
hint,It was founded in 1960.
hint,Designed by Oscar Niemeyer.`} 
                  />
                </div>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}