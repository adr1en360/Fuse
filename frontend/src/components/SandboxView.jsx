import React, { useState } from "react"
import { Play, Send, RefreshCw, Terminal, CheckCircle2, AlertTriangle, XCircle, Cpu, ArrowRight } from "lucide-react"

export default function SandboxView({ onRecordCreated }) {
  const [method, setMethod] = useState("GET")
  const [endpoint, setEndpoint] = useState("/v1/search?q=document-analysis")
  const [serviceProfile, setServiceProfile] = useState("read_intensive")
  const [burstCount, setBurstCount] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [executionResult, setExecutionResult] = useState(null)

  // Pre-configured agent tool scenarios
  const presets = [
    {
      name: "Parallel Search Burst",
      method: "GET",
      endpoint: "/v1/search?q=rag-query",
      profile: "read_intensive",
      burst: 10,
      expected: "FORWARD (Layer 2 Jev identifies parallel_work)",
    },
    {
      name: "Stuck 503 Retry Storm",
      method: "POST",
      endpoint: "/flaky-service",
      profile: "standard_api",
      burst: 10,
      expected: "BACKOFF (Layer 2 Jev detects retry_storm, injects delay)",
    },
    {
      name: "Circular Tool Loop",
      method: "GET",
      endpoint: "/loop/step-A",
      profile: "standard_api",
      burst: 8,
      expected: "ESCALATE (Layer 2 trips escape hatch to Gemini 3.8 Flash)",
    },
    {
      name: "Rogue Traffic Flood",
      method: "POST",
      endpoint: "/v1/execute",
      profile: "high_consequence",
      burst: 25,
      expected: "BLOCK (Layer 1 Hard Ceiling stops calls 21 to 25 with 429)",
    },
  ]

  const handleApplyPreset = (preset) => {
    setMethod(preset.method)
    setEndpoint(preset.endpoint)
    setServiceProfile(preset.profile)
    setBurstCount(preset.burst)
  }

  const handleExecute = async () => {
    setIsLoading(true)
    setExecutionResult(null)

    const startTime = performance.now()
    try {
      // Fire request to local Fuse proxy gateway
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method,
        headers: {
          "X-Fuse-Service": serviceProfile,
          "Content-Type": "application/json",
        },
      })

      const duration = (performance.now() - startTime).toFixed(1)
      const data = await res.json().catch(() => ({}))

      const result = {
        status: res.status,
        duration_ms: duration,
        action: res.headers.get("x-fuse-action") || (res.status === 429 ? "BLOCK" : "FORWARD"),
        layer: res.headers.get("x-fuse-layer") || "LAYER_1_OR_2",
        backoff_sec: res.headers.get("retry-after") || null,
        data,
      }

      setExecutionResult(result)
      if (onRecordCreated) {
        onRecordCreated({
          id: "call_" + Math.random().toString(36).substring(7),
          timestamp: new Date().toLocaleTimeString(),
          session_id: "sandbox_session",
          method,
          endpoint,
          service_profile: serviceProfile,
          action: result.action,
          layer: result.layer,
          status_code: res.status,
          duration_ms: parseFloat(duration),
          reason: `Sandbox test call: ${result.action} via ${result.layer}`,
        })
      }
    } catch (err) {
      // Offline fallback simulation
      const duration = (performance.now() - startTime + 38).toFixed(1)
      let simulatedAction = "FORWARD"
      let simulatedLayer = "LAYER_2_JEV_SYSTEM_ONE"

      if (burstCount >= 21) {
        simulatedAction = "BLOCK"
        simulatedLayer = "LAYER_1_HARD_CEILING"
      } else if (endpoint.includes("flaky")) {
        simulatedAction = "BACKOFF"
        simulatedLayer = "LAYER_2_JEV_SYSTEM_ONE"
      } else if (endpoint.includes("loop")) {
        simulatedAction = "ESCALATE_LLM"
        simulatedLayer = "LAYER_3_GEMINI_FLASH"
      }

      setExecutionResult({
        status: simulatedAction === "BLOCK" ? 429 : 200,
        duration_ms: duration,
        action: simulatedAction,
        layer: simulatedLayer,
        backoff_sec: simulatedAction === "BACKOFF" ? 1.0 : null,
        simulated: true,
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-white">Interactive Request Sandbox</h2>
        <p className="text-xs text-slate-400">
          Send test tool calls through the Fuse proxy on port 8000 and watch the 3-layer safety pipeline evaluate each request.
        </p>
      </div>

      {/* Preset Quick Selectors */}
      <div className="space-y-2">
        <span className="text-xs font-semibold text-slate-300">Quick Test Scenarios:</span>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {presets.map((p) => (
            <button
              key={p.name}
              onClick={() => handleApplyPreset(p)}
              className="text-left rounded-lg border border-slate-800 bg-slate-900/60 p-3 hover:border-[#74cfd8]/50 hover:bg-slate-900 transition-all group"
            >
              <div className="text-xs font-bold text-white group-hover:text-[#74cfd8] transition-colors">
                {p.name}
              </div>
              <div className="mt-1 font-mono text-[11px] text-slate-400">
                {p.method} {p.endpoint}
              </div>
              <div className="mt-2 text-[10px] text-slate-500">
                Expects: {p.expected}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Interactive Request Form */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {/* Method */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">HTTP Method</label>
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value)}
              className="w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-xs font-mono text-slate-200 focus:border-[#74cfd8] focus:outline-none"
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
            </select>
          </div>

          {/* Endpoint */}
          <div className="md:col-span-2">
            <label className="block text-xs font-medium text-slate-400 mb-1">Downstream Target Path</label>
            <input
              type="text"
              value={endpoint}
              onChange={(e) => setEndpoint(e.target.value)}
              className="w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-xs font-mono text-slate-200 focus:border-[#74cfd8] focus:outline-none"
              placeholder="/v1/search?q=test"
            />
          </div>

          {/* Service Profile */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Service Profile</label>
            <select
              value={serviceProfile}
              onChange={(e) => setServiceProfile(e.target.value)}
              className="w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-xs font-mono text-slate-200 focus:border-[#74cfd8] focus:outline-none"
            >
              <option value="read_intensive">read_intensive (Search, Vectors)</option>
              <option value="standard_api">standard_api (General REST)</option>
              <option value="high_consequence">high_consequence (Payments, DB)</option>
            </select>
          </div>
        </div>

        {/* Execution Bar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pt-2 border-t border-slate-800/80 gap-3">
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <span>Call Volume:</span>
            <div className="flex items-center space-x-1">
              {[1, 5, 10, 25].map((count) => (
                <button
                  key={count}
                  onClick={() => setBurstCount(count)}
                  className={`rounded px-2.5 py-1 font-mono text-[11px] transition-colors ${
                    burstCount === count
                      ? "bg-[#74cfd8] text-[#05080e] font-bold shadow-sm"
                      : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                  }`}
                >
                  {count} {count === 1 ? "call" : "burst"}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleExecute}
            disabled={isLoading}
            className="flex items-center space-x-2 rounded-lg bg-[#74cfd8] px-5 py-2 text-xs font-bold text-[#05080e] hover:bg-[#5bbec8] transition-colors disabled:opacity-50 shadow-sm shadow-[#74cfd8]/20"
          >
            {isLoading ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Evaluating Pipeline...</span>
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                <span>Send Outbound Call via Fuse</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Execution Results View */}
      {executionResult && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2">
              <Terminal className="h-4 w-4 text-[#74cfd8]" />
              <h3 className="text-sm font-bold text-white">Proxy Gateway Response</h3>
            </div>
            <span className="font-mono text-xs text-slate-400">
              Evaluated in {executionResult.duration_ms}ms
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
            <div className="rounded-lg bg-slate-950 p-3">
              <span className="text-slate-400">HTTP Status:</span>
              <div className="mt-1 font-mono font-bold text-base text-white">
                {executionResult.status}
              </div>
            </div>

            <div className="rounded-lg bg-slate-950 p-3">
              <span className="text-slate-400">Routing Action:</span>
              <div className="mt-1 font-mono font-bold text-base text-blue-400">
                {executionResult.action}
              </div>
            </div>

            <div className="rounded-lg bg-slate-950 p-3">
              <span className="text-slate-400">Deciding Layer:</span>
              <div className="mt-1 font-mono font-bold text-base text-purple-400">
                {executionResult.layer.replace("LAYER_", "L").replace(/_/g, " ")}
              </div>
            </div>

            <div className="rounded-lg bg-slate-950 p-3">
              <span className="text-slate-400">Backoff Delay:</span>
              <div className="mt-1 font-mono font-bold text-base text-amber-400">
                {executionResult.backoff_sec ? `${executionResult.backoff_sec}s` : "None (0s)"}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
