import React from "react"
import { Shield, Zap, Cpu, ArrowRight, CheckCircle2, AlertTriangle, XCircle, ArrowUpRight } from "lucide-react"

export default function PipelineVisualizer({ activeLayer, activeAction }) {
  const isL1Active = activeLayer === "LAYER_1_HARD_CEILING"
  const isL2Active = activeLayer === "LAYER_2_JEV_SYSTEM_ONE"
  const isL3Active = activeLayer === "LAYER_3_GEMINI_FLASH"

  const actionDetails = {
    FORWARD: { label: "FORWARD (200 OK)", color: "text-emerald-400 bg-emerald-950/60 border-emerald-500/40", icon: CheckCircle2 },
    BACKOFF: { label: "BACKOFF (Retry-After)", color: "text-amber-400 bg-amber-950/60 border-amber-500/40", icon: AlertTriangle },
    BLOCK: { label: "BLOCK (429 Ceiling)", color: "text-rose-400 bg-rose-950/60 border-rose-500/40", icon: XCircle },
    ESCALATE_LLM: { label: "CIRCUIT TRIP (Gemini Diagnosis)", color: "text-purple-400 bg-purple-950/60 border-purple-500/40", icon: Cpu },
  }[activeAction] || { label: "MONITORING", color: "text-slate-400 bg-slate-900 border-slate-800", icon: Shield }

  const OutcomeIcon = actionDetails.icon

  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/30 p-3.5">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        {/* Stages Pipeline */}
        <div className="flex items-center space-x-1.5 sm:space-x-2 text-xs overflow-x-auto py-1">
          {/* Stage: Inbound */}
          <div className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 whitespace-nowrap">
            <span className="h-1.5 w-1.5 rounded-full bg-slate-400" />
            <span className="font-mono text-slate-300">Agent Request</span>
          </div>

          <ArrowRight className="h-3.5 w-3.5 text-slate-600 shrink-0" />

          {/* Stage: L1 Ceiling */}
          <div
            className={`flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg border whitespace-nowrap transition-all ${
              isL1Active
                ? "bg-rose-950/40 border-rose-500 text-rose-300 ring-1 ring-rose-500/30"
                : "bg-slate-950 border-slate-800/80 text-slate-400"
            }`}
          >
            <Shield className={`h-3 w-3 ${isL1Active ? "text-rose-400" : "text-slate-500"}`} />
            <span className="font-mono font-medium">L1 Ceiling</span>
          </div>

          <ArrowRight className="h-3.5 w-3.5 text-slate-600 shrink-0" />

          {/* Stage: L2 Jev System One */}
          <div
            className={`flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg border whitespace-nowrap transition-all ${
              isL2Active
                ? "bg-[#74cfd8]/15 border-[#74cfd8] text-[#74cfd8] ring-1 ring-[#74cfd8]/30 font-semibold"
                : "bg-slate-950 border-slate-800/80 text-slate-400"
            }`}
          >
            <Zap className={`h-3 w-3 ${isL2Active ? "text-[#74cfd8]" : "text-slate-500"}`} />
            <span className="font-mono font-medium">L2 Jev</span>
          </div>

          <ArrowRight className="h-3.5 w-3.5 text-slate-600 shrink-0" />

          {/* Stage: L3 Gemini Flash */}
          <div
            className={`flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg border whitespace-nowrap transition-all ${
              isL3Active
                ? "bg-purple-950/40 border-purple-500 text-purple-300 ring-1 ring-purple-500/30 font-semibold"
                : "bg-slate-950 border-slate-800/80 text-slate-400"
            }`}
          >
            <Cpu className={`h-3 w-3 ${isL3Active ? "text-purple-400" : "text-slate-500"}`} />
            <span className="font-mono font-medium">L3 Gemini</span>
          </div>
        </div>

        {/* Current Decision Outcome */}
        <div className="flex items-center space-x-2 shrink-0">
          <span className="text-[11px] text-slate-500 font-mono">Decision:</span>
          <span className={`inline-flex items-center space-x-1.5 rounded-lg border px-3 py-1 text-xs font-mono font-bold ${actionDetails.color}`}>
            <OutcomeIcon className="h-3.5 w-3.5" />
            <span>{actionDetails.label}</span>
          </span>
        </div>
      </div>
    </div>
  )
}
