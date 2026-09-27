import React from "react"
import { Sliders, Shield, Layers, Zap, Info, Check } from "lucide-react"

export default function PolicyView() {
  const policies = [
    {
      name: "read_intensive",
      tag: "X-Fuse-Service: read_intensive",
      targetTypes: "Vector Databases, Search Indexes, Read Replicas",
      concurrencyRule: "High parallel tolerance. Concurrent read bursts are permitted without tripping the circuit breaker.",
      backoffRule: "Backoff delayed until 5+ consecutive 5xx errors.",
      color: "border-[#74cfd8]/30 bg-[#74cfd8]/10 text-[#74cfd8]",
    },
    {
      name: "standard_api",
      tag: "X-Fuse-Service: standard_api",
      targetTypes: "General REST APIs, Third-Party SaaS Tools",
      concurrencyRule: "Balanced thresholding. Trips anomaly detection after 8 calls in 5 seconds.",
      backoffRule: "Standard exponential backoff (1s, 2s, 4s) on repeated 503 or 429 status codes.",
      color: "border-slate-700 bg-slate-900/40 text-slate-300",
    },
    {
      name: "high_consequence",
      tag: "X-Fuse-Service: high_consequence",
      targetTypes: "Payment Gateways, Mutation Endpoints, SMS & Email Tools",
      concurrencyRule: "Zero unchecked retry tolerance. Immediate backoff after the very first failure.",
      backoffRule: "Immediate circuit trip with safety alerts to protect external budgets and user state.",
      color: "border-rose-500/30 bg-rose-950/20 text-rose-300",
    },
  ]

  const thresholdSettings = [
    { label: "Hard Ceiling Limit", value: "20 calls", env: "HARD_CEILING_CALLS", desc: "Layer 1 maximum calls before 429 is enforced." },
    { label: "Hard Ceiling Window", value: "10 seconds", env: "HARD_CEILING_WINDOW_SECONDS", desc: "Sliding window duration for arithmetic counting." },
    { label: "Anomaly Spike Trigger", value: "8 calls", env: "ANOMALY_THRESHOLD_CALLS", desc: "Call velocity that activates Layer 2 Jev evaluation." },
    { label: "Anomaly Time Window", value: "5 seconds", env: "ANOMALY_THRESHOLD_WINDOW_SECONDS", desc: "Window for measuring call velocity surges." },
    { label: "High Confidence Threshold", value: "0.70", env: "CONFIDENCE_HIGH", desc: "Jev confidence required to act directly without Layer 3." },
    { label: "Low Confidence Threshold", value: "0.40", env: "CONFIDENCE_LOW", desc: "Confidence floor below which Gemini 3.8 Flash escalation is mandatory." },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-white">Service Profiles and Threshold Policies</h2>
        <p className="text-xs text-slate-400">
          Fuse adjusts risk classification based on downstream endpoint sensitivity and sliding-window rate thresholds.
        </p>
      </div>

      {/* Threshold Grid */}
      <div className="space-y-3">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
          Deterministic Runtime Thresholds
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {thresholdSettings.map((t) => (
            <div key={t.env} className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">{t.label}</span>
                <span className="font-mono text-[10px] text-[#74cfd8] bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                  {t.value}
                </span>
              </div>
              <div className="font-mono text-[10px] text-slate-500">{t.env}</div>
              <p className="text-xs text-slate-400 pt-1">{t.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Service Profiles */}
      <div className="space-y-3 pt-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
          Downstream Service Context Profiles
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {policies.map((p) => (
            <div key={p.name} className={`rounded-xl border p-5 space-y-3 ${p.color}`}>
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-white uppercase font-mono">{p.name}</h4>
                <Shield className="h-4 w-4" />
              </div>
              <div className="font-mono text-[10px] bg-slate-950/80 p-2 rounded border border-slate-800 text-slate-300">
                {p.tag}
              </div>
              <div className="text-xs space-y-2 pt-1 text-slate-300">
                <div>
                  <strong className="text-white block mb-0.5">Typical Targets:</strong>
                  {p.targetTypes}
                </div>
                <div>
                  <strong className="text-white block mb-0.5">Concurrency Rule:</strong>
                  {p.concurrencyRule}
                </div>
                <div>
                  <strong className="text-white block mb-0.5">Backoff Rule:</strong>
                  {p.backoffRule}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
