import React from "react"
import { Shield, Activity, Terminal, Lock, Sliders, Globe } from "lucide-react"

export default function Navbar({ currentView, setCurrentView, isConnected }) {
  const navItems = [
    { id: "landing", label: "Overview", icon: Globe },
    { id: "dashboard", label: "Live Console", icon: Activity },
    { id: "sandbox", label: "Request Sandbox", icon: Terminal },
    { id: "audit", label: "Audit & Forensics", icon: Lock },
    { id: "policies", label: "Policies", icon: Sliders },
  ]

  return (
    <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-950/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        {/* Brand */}
        <button
          onClick={() => setCurrentView("landing")}
          className="flex items-center space-x-3 text-left hover:opacity-90 transition-opacity"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900 border border-slate-800 p-1.5 shadow-sm">
            <img src="/logo.svg" alt="Fuse" className="h-full w-full object-contain" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-base font-bold tracking-tight text-white font-mono">FUSE</span>
              <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-400">
                GATEWAY
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Agent Circuit Breaker</p>
          </div>
        </button>

        {/* User Flow Navigation Tabs */}
        <nav className="hidden md:flex items-center space-x-1 rounded-lg border border-slate-800 bg-slate-900/60 p-1">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = currentView === item.id
            return (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                className={`flex items-center space-x-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  isActive
                    ? "bg-[#74cfd8]/15 text-[#74cfd8] border border-[#74cfd8]/30 shadow-sm font-semibold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                <span>{item.label}</span>
              </button>
            )
          })}
        </nav>

        {/* Live System Badges */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-2 rounded-full border border-slate-800 bg-slate-900/80 px-3 py-1 text-xs">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
            </span>
            <span className="font-mono text-[11px] text-slate-300">Proxy :8000</span>
          </div>
        </div>
      </div>

      {/* Mobile Nav Bar */}
      <div className="md:hidden flex items-center justify-between border-t border-slate-800/80 px-4 py-2 bg-slate-950 overflow-x-auto gap-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = currentView === item.id
          return (
            <button
              key={item.id}
              onClick={() => setCurrentView(item.id)}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded text-xs whitespace-nowrap ${
                isActive ? "bg-[#74cfd8]/15 text-[#74cfd8] font-semibold border border-[#74cfd8]/30" : "text-slate-400"
              }`}
            >
              <Icon className="h-3 w-3" />
              <span>{item.label}</span>
            </button>
          )
        })}
      </div>
    </header>
  )
}
