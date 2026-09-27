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
  const [isRunningScenario, setIsRunningScenario] = useState(false)

  // Polling for live proxy metrics and decision traces
  useEffect(() => {
    let isMounted = true

    const fetchLiveData = async () => {
      try {
        const [metricsRes, tracesRes] = await Promise.allSettled([
          fetch("http://localhost:8000/api/metrics"),
          fetch("http://localhost:8000/api/traces?limit=50"),
        ])

        if (metricsRes.status === "fulfilled" && metricsRes.value.ok && isMounted) {
          const data = await metricsRes.value.json()
          const s = data.stats || data
          if (s) {
            setStats({
              total_calls: s.total_calls ?? 0,
              forwarded: s.forwarded ?? 0,
              backoff_applied: s.backoff_applied ?? 0,
              blocked: s.blocked ?? 0,
              escaped_to_llm: s.escaped_to_llm ?? 0,
              layer1_trips: s.layer1_trips ?? 0,
              layer2_jev_trips: s.layer2_jev_trips ?? 0,
              layer3_gemini_trips: s.layer3_gemini_trips ?? 0,
            })
            setIsConnected(true)
          }
        }

        if (tracesRes.status === "fulfilled" && tracesRes.value.ok && isMounted) {
          const liveTraces = await tracesRes.value.json()
          if (Array.isArray(liveTraces) && liveTraces.length > 0) {
            setTraces(liveTraces)
          }
        }
      } catch (err) {
        if (isMounted) setIsConnected(false)
      }
    }

    fetchLiveData()
    const interval = setInterval(fetchLiveData, 1000)
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

  const fallbackSimulate = (sc) => {
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

  const handleRunScenario = async (sc) => {
    setActiveState(sc.id)
    setIsRunningScenario(true)

    try {
      const res = await fetch("http://localhost:8000/api/scenarios/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario_id: sc.id }),
      })

      if (res.ok) {
        const [tracesRes, metricsRes] = await Promise.all([
          fetch("http://localhost:8000/api/traces?limit=50"),
          fetch("http://localhost:8000/api/metrics"),
        ])
        if (tracesRes.ok) {
          const newTraces = await tracesRes.json()
          if (Array.isArray(newTraces) && newTraces.length > 0) {
            setTraces(newTraces)
          }
        }
        if (metricsRes.ok) {
          const data = await metricsRes.json()
          const s = data.stats || data
          if (s) {
            setStats({
              total_calls: s.total_calls ?? 0,
              forwarded: s.forwarded ?? 0,
              backoff_applied: s.backoff_applied ?? 0,
              blocked: s.blocked ?? 0,
              escaped_to_llm: s.escaped_to_llm ?? 0,
              layer1_trips: s.layer1_trips ?? 0,
              layer2_jev_trips: s.layer2_jev_trips ?? 0,
              layer3_gemini_trips: s.layer3_gemini_trips ?? 0,
            })
          }
        }
      } else {
        fallbackSimulate(sc)
      }
    } catch (err) {
      fallbackSimulate(sc)
    } finally {
      setIsRunningScenario(false)
    }
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
            isRunningScenario={isRunningScenario}
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
