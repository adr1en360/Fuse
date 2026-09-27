import React from "react"
import {
  Shield,
  Layers,
  Zap,
  Cpu,
  ArrowRight,
  CheckCircle2,
  XCircle,
  Clock,
  Terminal,
  FileCode,
  Lock,
  ExternalLink
} from "lucide-react"

export default function LandingView({ onNavigateToDashboard }) {
  return (
    <div className="space-y-16 py-6">
      {/* Hero Section */}
      <section className="text-center space-y-6 max-w-3xl mx-auto">
        <div className="inline-flex items-center space-x-2 rounded-full border border-[#74cfd8]/30 bg-[#74cfd8]/10 px-3 py-1 text-xs text-[#74cfd8]">
          <span className="flex h-1.5 w-1.5 rounded-full bg-[#74cfd8]" />
          <span>Reverse proxy middleware for autonomous agents</span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
          Intelligent Circuit Breaker for Autonomous AI Agents
        </h1>

        <p className="text-base sm:text-lg text-slate-300 leading-relaxed">
          Protects downstream APIs, databases, and budgets from agent retry storms, runaway tool loops, and rate limit exhaustion, without stopping valid parallel work.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <button
            onClick={onNavigateToDashboard}
            className="flex items-center justify-center space-x-2 rounded-lg bg-[#74cfd8] px-5 py-2.5 text-sm font-bold text-[#05080e] hover:bg-[#5bbec8] transition-colors w-full sm:w-auto shadow-lg shadow-[#74cfd8]/20"
          >
            <span>Launch Live Dashboard</span>
            <ArrowRight className="h-4 w-4" />
          </button>

          <a
            href="https://github.com/adr1en360/Fuse"
            target="_blank"
            rel="noreferrer"
            className="flex items-center justify-center space-x-2 rounded-lg border border-slate-700 bg-slate-900 px-5 py-2.5 text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition-colors w-full sm:w-auto"
          >
            <span>View Source on GitHub</span>
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>
      </section>

      {/* The Problem Comparison Grid */}
      <section className="space-y-6">
        <div className="text-center max-w-xl mx-auto space-y-2">
          <h2 className="text-2xl font-bold text-white">Why standard rate limiters fail agents</h2>
          <p className="text-xs text-slate-400">
            Standard limiters only count requests. They cannot distinguish legitimate parallel bursts from fatal retry storms.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
          {/* Traditional Limiter Card */}
          <div className="rounded-xl border border-rose-900/30 bg-rose-950/10 p-5 space-y-4">
            <div className="flex items-center space-x-2 text-rose-400">
              <XCircle className="h-5 w-5" />
              <h3 className="font-semibold text-white">Standard Rate Limiter</h3>
            </div>
            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-start">
                <span className="text-rose-400 mr-2">✕</span>
                <span>Blocks valid 10-document parallel RAG search requests as a flood spike.</span>
              </li>
              <li className="flex items-start">
                <span className="text-rose-400 mr-2">✕</span>
                <span>Allows slow circular tool loops that quietly burn API budgets.</span>
              </li>
              <li className="flex items-start">
                <span className="text-rose-400 mr-2">✕</span>
                <span>Forces agents into hard-coded sleep delays that stall real work.</span>
              </li>
              <li className="flex items-start">
                <span className="text-rose-400 mr-2">✕</span>
                <span>Provides zero context on why a downstream service rejected calls.</span>
              </li>
            </ul>
          </div>

          {/* Fuse Card */}
          <div className="rounded-xl border border-emerald-900/30 bg-emerald-950/10 p-5 space-y-4">
            <div className="flex items-center space-x-2 text-emerald-400">
              <CheckCircle2 className="h-5 w-5" />
              <h3 className="font-semibold text-white">Fuse Intelligent Proxy</h3>
            </div>
            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-start">
                <span className="text-emerald-400 mr-2">✓</span>
                <span>Recognizes parallel read fanouts and forwards them instantly.</span>
              </li>
              <li className="flex items-start">
                <span className="text-emerald-400 mr-2">✓</span>
                <span>Identifies 503 retry storms and injects exponential backoff.</span>
              </li>
              <li className="flex items-start">
                <span className="text-emerald-400 mr-2">✓</span>
                <span>Detects circular tool loops and diagnoses the root cause using Gemini 3.8 Flash.</span>
              </li>
              <li className="flex items-start">
                <span className="text-emerald-400 mr-2">✓</span>
                <span>Guards every call with a deterministic arithmetic ceiling that cannot be bypassed.</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* 3-Layer Defense Architecture */}
      <section className="space-y-6">
        <div className="text-center max-w-xl mx-auto space-y-2">
          <h2 className="text-2xl font-bold text-white">Three-Layer Inspection Hierarchy</h2>
          <p className="text-xs text-slate-400">
            A staged defense architecture designed for speed and safety.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-5xl mx-auto">
          {/* Layer 1 */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-mono text-slate-300">
                LAYER 1
              </span>
              <span className="text-xs font-mono text-slate-400">&lt;1 ms</span>
            </div>
            <h3 className="text-base font-bold text-white">Deterministic Hard Ceiling</h3>
            <p className="text-xs text-slate-400">
              Pure sliding-window count limits. Pure arithmetic execution ensures no model outage or network delay can allow a rogue flood through.
            </p>
          </div>

          {/* Layer 2 */}
          <div className="rounded-xl border border-[#74cfd8]/30 bg-[#74cfd8]/10 p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="rounded bg-[#74cfd8]/20 px-2 py-0.5 text-[10px] font-mono text-[#74cfd8] font-bold">
                LAYER 2
              </span>
              <span className="text-xs font-mono text-[#74cfd8]">~60 ms</span>
            </div>
            <h3 className="text-base font-bold text-white">Jev System One Classifier</h3>
            <p className="text-xs text-slate-300">
              Fast typed evaluation returning Choice, Score, and Noul with calibrated confidence values and an escape hatch for unmodeled patterns.
            </p>
          </div>

          {/* Layer 3 */}
          <div className="rounded-xl border border-purple-900/40 bg-purple-950/20 p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="rounded bg-purple-900/60 px-2 py-0.5 text-[10px] font-mono text-purple-300">
                LAYER 3
              </span>
              <span className="text-xs font-mono text-purple-400">~900 ms</span>
            </div>
            <h3 className="text-base font-bold text-white">Gemini 3.8 Flash Diagnosis</h3>
            <p className="text-xs text-slate-400">
              Invoked only when Jev flags an unclassified pattern or low confidence. Analyzes recent history and produces concrete remediation advice.
            </p>
          </div>
        </div>
      </section>

      {/* Integration Code Snippet */}
      <section className="rounded-xl border border-slate-800 bg-slate-900/30 p-6 max-w-4xl mx-auto space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Terminal className="h-5 w-5 text-[#74cfd8]" />
            <h3 className="text-sm font-semibold text-white">Zero-Code Agent Integration</h3>
          </div>
          <span className="text-xs font-mono text-slate-400">Standard HTTP Proxy</span>
        </div>

        <p className="text-xs text-slate-400">
          Point your agent environment to Fuse. No SDK or code changes needed for existing tool-calling pipelines.
        </p>

        <div className="rounded-lg bg-slate-950 p-4 font-mono text-xs text-slate-200 overflow-x-auto border border-slate-800">
          <div className="text-slate-500 mb-2"># In your terminal or container environment:</div>
          <div>export HTTP_PROXY="http://localhost:8000"</div>
          <div>export HTTPS_PROXY="http://localhost:8000"</div>
          <div className="mt-4 text-slate-500 mb-2"># Or configure target base URL directly:</div>
          <div>export TARGET_BASE_URL="http://your-downstream-api.com"</div>
        </div>
      </section>
    </div>
  )
}
