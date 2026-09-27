import React, { useState, useEffect } from "react"
import Navbar from "./components/Navbar"
import DashboardView from "./components/DashboardView"
import SandboxView from "./components/SandboxView"
import AuditView from "./components/AuditView"
import PolicyView from "./components/PolicyView"
import LandingView from "./components/LandingView"
import { initialStats, initialDecisionTraces } from "./data/mockData"

export default function App() {
  const [currentView, setCurrentView] = useState("landing")
  const [stats, setStats] = useState(initialStats)
  const [traces, setTraces] = useState(initialDecisionTraces)
  const [activeState, setActiveState] = useState("green")
  const [isConnected, setIsConnected] = useState(true)

  // Polling for live proxy metrics if proxy is running on :8000
  useEffect(() => {
    let isMounted = true

    const fetchLiveMetrics = async () => {
      try {
        const res = await fetch("http://localhost:8000/metrics")
        if (res.ok && isMounted) {
          const data = await res.json()
          if (data && data.stats) {
            setStats((prev) => ({
              ...prev,
              total_calls: data.stats.total_calls || prev.total_calls,
              forwarded: data.stats.forwarded || prev.forwarded,
              backoff_applied: data.stats.backoff_applied || prev.backoff_applied,
              blocked: data.stats.blocked || prev.blocked,
              escaped_to_llm: data.stats.escaped_to_llm || prev.escaped_to_llm,
              layer1_trips: data.stats.layer1_trips || prev.layer1_trips,
              layer2_jev_trips: data.stats.layer2_jev_trips || prev.layer2_jev_trips,
              layer3_gemini_trips: data.stats.layer3_gemini_trips || prev.layer3_gemini_trips,
            }))
            setIsConnected(true)
          }
        }
      } catch (err) {
        // Fallback to local state if proxy is offline
      }
    }

    fetchLiveMetrics()
    const interval = setInterval(fetchLiveMetrics, 2000)
    return () => {
      isMounted = false
      clearInterval(interval)
    }
  }, [])

  const handleRecordCreated = (newRecord) => {
    setTraces((prev) => [newRecord, ...prev])
    setStats((prev) => ({
      ...prev,
      total_calls: prev.total_calls + 1,
      forwarded: newRecord.action === "FORWARD" ? prev.forwarded + 1 : prev.forwarded,
      backoff_applied: newRecord.action === "BACKOFF" ? prev.backoff_applied + 1 : prev.backoff_applied,
      blocked: newRecord.action === "BLOCK" ? prev.blocked + 1 : prev.blocked,
      escaped_to_llm: newRecord.action === "ESCALATE_LLM" ? prev.escaped_to_llm + 1 : prev.escaped_to_llm,
    }))
  }

  const handleRunScenario = (sc) => {
    setActiveState(sc.id)
    const newRecord = {
      id: "sc_" + Math.random().toString(36).substring(7),
      timestamp: new Date().toLocaleTimeString(),
      session_id: `agent_${sc.id}_demo`,
      method: sc.id === "yellow" || sc.id === "red" ? "POST" : "GET",
      endpoint: sc.target,
      service_profile: sc.id === "red" ? "high_consequence" : (sc.id === "green" ? "read_intensive" : "standard_api"),
      action: sc.expectedAction,
      layer: sc.layer,
      status_code: sc.expectedAction === "BLOCK" ? 429 : 200,
      duration_ms: sc.id === "blue" ? 850.4 : (sc.id === "green" ? 42.1 : (sc.id === "yellow" ? 64.2 : 0.8)),
      reason: sc.description,
      chain_hash: "hash_" + Math.random().toString(36).substring(2) + Math.random().toString(36).substring(2),
      prev_hash: traces[0]?.chain_hash || "00000000000000000000000000000000",
    }
    handleRecordCreated(newRecord)
  }

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans">
      <Navbar
        currentView={currentView}
        setCurrentView={setCurrentView}
        isConnected={isConnected}
      />

      <main className="flex-1 mx-auto max-w-7xl w-full px-4 py-6 sm:px-6 lg:px-8">
        {currentView === "dashboard" && (
          <DashboardView
            stats={stats}
            traces={traces}
            activeState={activeState}
            setActiveState={setActiveState}
            onRunScenario={handleRunScenario}
          />
        )}

        {currentView === "sandbox" && (
          <SandboxView onRecordCreated={handleRecordCreated} />
        )}

        {currentView === "audit" && (
          <AuditView traces={traces} stats={stats} />
        )}

        {currentView === "policies" && (
          <PolicyView />
        )}

        {currentView === "landing" && (
          <LandingView onNavigateToDashboard={() => setCurrentView("dashboard")} />
        )}
      </main>

      <footer className="border-t border-slate-800 bg-slate-950 py-4 text-xs text-slate-500">
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Fuse: Confidence-gated circuit breaker for autonomous agents</span>
          <span className="font-mono text-[11px] text-slate-400">
            Proxy Gateway :8000 • Mock API :9000 • SHA-256 Audit Trail
          </span>
        </div>
      </footer>
    </div>
  )
}
