import React, { useState } from "react"
import {
  ShieldCheck,
  Zap,
  Search,
  Play,
  X,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Cpu,
  ArrowRight
} from "lucide-react"
import PipelineVisualizer from "./PipelineVisualizer"

export default function DashboardView({ stats, traces, activeState, setActiveState, onRunScenario }) {
  const [selectedTrace, setSelectedTrace] = useState(null)
  const [filterAction, setFilterAction] = useState("ALL")
  const [searchQuery, setSearchQuery] = useState("")

  const scenarios = [
    {
      id: "green",
      act: "Act 1",
      name: "Search Fanout",
      target: "/v1/search?q=rag-query",
      expectedAction: "FORWARD",
      layer: "LAYER_2_JEV_SYSTEM_ONE",
      description: "10 parallel queries. Jev identifies parallel work and passes calls with zero false-positive blocks.",
    },
    {
      id: "yellow",
      act: "Act 2",
      name: "503 Retry Storm",
      target: "/flaky-service",
      expectedAction: "BACKOFF",
      layer: "LAYER_2_JEV_SYSTEM_ONE",
      description: "Downstream 503 errors. Jev detects retry storm and injects exponential backoff delay.",
    },
    {
      id: "blue",
      act: "Act 3",
      name: "Tool Loop",
      target: "/loop/cyclical",
      expectedAction: "ESCALATE_LLM",
      layer: "LAYER_3_GEMINI_FLASH",
      description: "Cyclic tool loop. Jev trips escape hatch; Gemini 3.8 Flash diagnoses root cause.",
    },
    {
      id: "red",
      act: "Act 4",
      name: "Traffic Flood",
      target: "/v1/execute",
      expectedAction: "BLOCK",
      layer: "LAYER_1_HARD_CEILING",
      description: "25 rapid calls. Layer 1 deterministic arithmetic ceiling hard-blocks calls 21 to 25 with 429.",
    },
  ]

  const activeScenario = scenarios.find((s) => s.id === activeState) || scenarios[0]

  const handleRun = (sc) => {
    setActiveState(sc.id)
    if (onRunScenario) {
      onRunScenario(sc)
    }
  }

  const filteredTraces = traces.filter((t) => {
    const matchesFilter = filterAction === "ALL" || t.action === filterAction
    const matchesSearch =
      searchQuery === "" ||
      t.endpoint.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.session_id.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesFilter && matchesSearch
  })

  const actionBadge = (action) => {
    switch (action) {
      case "FORWARD":
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">FORWARD</span>
      case "BACKOFF":
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">BACKOFF</span>
      case "BLOCK":
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">BLOCK</span>
      case "ESCALATE_LLM":
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-500/10 text-purple-400 border border-purple-500/30">GEMINI</span>
      default:
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-slate-300">{action}</span>
    }
  }

  return (
    <div className="space-y-5">
      {/* 1. Distilled Scenario Toolbar */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/30 p-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          {/* Act Pills */}
          <div className="flex items-center space-x-1.5 overflow-x-auto">
            {scenarios.map((sc) => {
              const isSelected = activeState === sc.id
              return (
                <button
                  key={sc.id}
                  onClick={() => handleRun(sc)}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-mono transition-all whitespace-nowrap ${
                    isSelected
                      ? "bg-[#74cfd8] text-[#05080e] font-bold shadow-sm"
                      : "bg-slate-950 text-slate-400 border border-slate-800 hover:text-white hover:bg-slate-900"
                  }`}
                >
                  <Play className={`h-3 w-3 ${isSelected ? "text-[#05080e] fill-current" : "text-slate-500"}`} />
                  <span>{sc.act}: {sc.name}</span>
                </button>
              )
            })}
          </div>

          {/* Quick Act Description */}
          <div className="text-xs text-slate-400 flex items-center space-x-2">
            <span className="hidden lg:inline text-slate-500">Active Test:</span>
            <span className="text-slate-300 truncate">{activeScenario.description}</span>
          </div>
        </div>
      </div>

      {/* 2. Sleek Pipeline Visualizer */}
      <PipelineVisualizer
        activeLayer={selectedTrace?.layer || activeScenario.layer}
        activeAction={selectedTrace?.action || activeScenario.expectedAction}
      />

      {/* 3. Quiet Operational Metrics Strip */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="rounded-xl border border-slate-800/80 bg-slate-900/20 p-3.5">
          <div className="text-[11px] text-slate-500 uppercase font-mono tracking-wider">Total Calls</div>
          <div className="mt-1 text-2xl font-bold font-mono text-white tabular-nums">{stats.total_calls}</div>
          <div className="text-[11px] text-slate-400 mt-1 font-mono">Proxy Gateway :8000</div>
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-slate-900/20 p-3.5">
          <div className="text-[11px] text-slate-500 uppercase font-mono tracking-wider">Forwarded</div>
          <div className="mt-1 text-2xl font-bold font-mono text-emerald-400 tabular-nums">{stats.forwarded}</div>
          <div className="text-[11px] text-emerald-400/80 mt-1 font-mono">0% false positives</div>
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-slate-900/20 p-3.5">
          <div className="text-[11px] text-slate-500 uppercase font-mono tracking-wider">Throttled</div>
          <div className="mt-1 text-2xl font-bold font-mono text-amber-400 tabular-nums">{stats.backoff_applied}</div>
          <div className="text-[11px] text-amber-400/80 mt-1 font-mono">Backoff injected</div>
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-slate-900/20 p-3.5">
          <div className="text-[11px] text-slate-500 uppercase font-mono tracking-wider">Blocked (429)</div>
          <div className="mt-1 text-2xl font-bold font-mono text-rose-400 tabular-nums">{stats.blocked}</div>
          <div className="text-[11px] text-rose-400/80 mt-1 font-mono">L1 Ceiling limit</div>
        </div>
      </div>

      {/* 4. Streamlined Decision Log Table */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/20 overflow-hidden">
        {/* Table Filter Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between px-4 py-2.5 border-b border-slate-800/80 gap-2">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-white font-mono uppercase tracking-wider">Decision Stream</span>
            <span className="text-[11px] text-slate-500">({filteredTraces.length} events)</span>
          </div>

          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-slate-500" />
              <input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-36 sm:w-44 rounded-md border border-slate-800 bg-slate-950 py-1 pl-8 pr-2.5 text-xs text-slate-200 placeholder-slate-500 focus:border-[#74cfd8] focus:outline-none"
              />
            </div>

            <div className="flex rounded-md border border-slate-800 bg-slate-950 p-0.5 text-xs">
              {["ALL", "FORWARD", "BACKOFF", "BLOCK"].map((act) => (
                <button
                  key={act}
                  onClick={() => setFilterAction(act)}
                  className={`rounded px-2 py-0.5 text-[10px] font-mono transition-colors ${
                    filterAction === act
                      ? "bg-[#74cfd8] text-[#05080e] font-bold"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {act}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Clean, Scannable Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/40 text-[10px] font-mono uppercase tracking-wider text-slate-500 border-b border-slate-800/60">
              <tr>
                <th className="py-2 px-4">Time</th>
                <th className="py-2 px-4">Method & Target</th>
                <th className="py-2 px-4">Decision</th>
                <th className="py-2 px-4">Layer</th>
                <th className="py-2 px-4 text-right">Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40 font-mono">
              {filteredTraces.slice(0, 10).map((t) => {
                const isSelected = selectedTrace?.id === t.id
                return (
                  <tr
                    key={t.id}
                    onClick={() => setSelectedTrace(isSelected ? null : t)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? "bg-[#74cfd8]/10 ring-1 ring-inset ring-[#74cfd8]/40"
                        : "hover:bg-slate-800/30"
                    }`}
                  >
                    <td className="py-2.5 px-4 text-slate-400 whitespace-nowrap text-[11px]">{t.timestamp}</td>
                    <td className="py-2.5 px-4">
                      <span className="text-slate-400 font-bold mr-1.5">{t.method}</span>
                      <span className="text-slate-200">{t.endpoint}</span>
                    </td>
                    <td className="py-2.5 px-4">{actionBadge(t.action)}</td>
                    <td className="py-2.5 px-4 text-slate-400 text-[11px]">
                      {t.layer.replace("LAYER_", "L").replace(/_/g, " ")}
                    </td>
                    <td className="py-2.5 px-4 text-right text-slate-400 text-[11px] tabular-nums">
                      {t.duration_ms}ms
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Progressive Disclosure: Trace Inspector (Only visible when user clicks a row) */}
      {selectedTrace && (
        <div className="rounded-xl border border-[#74cfd8]/30 bg-slate-900/60 p-4 space-y-3 shadow-lg">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="h-4 w-4 text-[#74cfd8]" />
              <span className="text-xs font-bold text-white font-mono uppercase">
                Trace Inspection: {selectedTrace.id}
              </span>
            </div>
            <button
              onClick={() => setSelectedTrace(null)}
              className="text-slate-400 hover:text-white rounded p-1 hover:bg-slate-800"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="rounded-lg bg-slate-950 p-3 space-y-1 font-mono text-[11px] border border-slate-800">
              <div className="text-slate-500 uppercase text-[10px]">Request Signature</div>
              <div><span className="text-slate-500">Endpoint:</span> {selectedTrace.method} {selectedTrace.endpoint}</div>
              <div><span className="text-slate-500">Session ID:</span> {selectedTrace.session_id}</div>
              <div><span className="text-slate-500">Profile:</span> {selectedTrace.service_profile}</div>
              <div><span className="text-slate-500">Action:</span> {selectedTrace.action} ({selectedTrace.status_code})</div>
            </div>

            <div className="rounded-lg bg-slate-950 p-3 space-y-1 font-mono text-[11px] border border-slate-800">
              <div className="text-slate-500 uppercase text-[10px]">Reasoning & Diagnostics</div>
              <div className="text-slate-300">{selectedTrace.reason}</div>
              {selectedTrace.llm && (
                <div className="pt-1 text-purple-300">
                  <div><strong className="text-purple-400">Gemini Root Cause:</strong> {selectedTrace.llm.root_cause}</div>
                  <div><strong className="text-purple-400">Remediation:</strong> {selectedTrace.llm.remediation_advice}</div>
                </div>
              )}
            </div>
          </div>

          {selectedTrace.chain_hash && (
            <div className="rounded bg-slate-950 px-3 py-2 font-mono text-[10px] text-slate-400 border border-slate-800 flex items-center justify-between">
              <span className="text-slate-500">SHA-256 Audit Hash:</span>
              <span className="text-emerald-400 truncate ml-2">{selectedTrace.chain_hash}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
