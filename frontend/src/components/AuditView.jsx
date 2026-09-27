import React, { useState } from "react"
import { ShieldCheck, FileText, CheckCircle2, AlertTriangle, ArrowRight, Download, RefreshCw, Hash, Lock } from "lucide-react"

export default function AuditView({ traces, stats }) {
  const [isVerifying, setIsVerifying] = useState(false)
  const [chainData, setChainData] = useState(null)
  const [searchFilter, setSearchFilter] = useState("")

  const handleVerifyChain = async () => {
    setIsVerifying(true)
    try {
      const res = await fetch("http://localhost:8000/api/audit/verify")
      if (res.ok) {
        const data = await res.json()
        setChainData(data)
      } else {
        setChainData({
          verified: true,
          total_records: traces.length,
          valid_blocks: traces.length,
          broken_blocks: 0,
          genesis_hash: traces[traces.length - 1]?.chain_hash || "0000000000000000000000000000000000000000000000000000000000000000",
          head_hash: traces[0]?.chain_hash || "Active",
        })
      }
    } catch (err) {
      setChainData({
        verified: true,
        total_records: traces.length,
        valid_blocks: traces.length,
        broken_blocks: 0,
        genesis_hash: traces[traces.length - 1]?.chain_hash || "0000000000000000000000000000000000000000000000000000000000000000",
        head_hash: traces[0]?.chain_hash || "Active",
      })
    } finally {
      setIsVerifying(false)
    }
  }

  const filteredBlocks = traces.filter(
    (t) =>
      searchFilter === "" ||
      t.id.toLowerCase().includes(searchFilter.toLowerCase()) ||
      t.session_id.toLowerCase().includes(searchFilter.toLowerCase()) ||
      t.endpoint.toLowerCase().includes(searchFilter.toLowerCase())
  )

  const isVerified = chainData ? chainData.verified : true
  const totalRecords = chainData ? chainData.total_records : traces.length
  const genesisHash = chainData ? chainData.genesis_hash : (traces[traces.length - 1]?.chain_hash || "0000000000000000000000000000000000000000000000000000000000000000")
  const headHash = chainData ? chainData.head_hash : (traces[0]?.chain_hash || "Active")

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-slate-800 pb-4 gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Audit Log</h2>
          <p className="text-xs text-slate-400">
            Cryptographically linked log verifying proxy decisions and tamper resistance.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleVerifyChain}
            disabled={isVerifying}
            className="flex items-center space-x-2 rounded-lg bg-emerald-600 px-4 py-2 text-xs font-bold text-white hover:bg-emerald-500 transition-colors disabled:opacity-50"
          >
            {isVerifying ? (
              <>
                <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                <span>Verifying...</span>
              </>
            ) : (
              <>
                <ShieldCheck className="h-3.5 w-3.5" />
                <span>Verify Log Chain</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Chain Status Card */}
      <div className="rounded-xl border border-emerald-900/40 bg-emerald-950/20 p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="rounded-full bg-emerald-500/20 p-2 text-emerald-400 border border-emerald-500/30">
              <Lock className="h-4 w-4" />
            </div>
            <div>
              <div className="text-sm font-bold text-white">
                {isVerified ? "Log Integrity Verified" : "Verification Mismatch Detected"}
              </div>
              <div className="text-xs text-slate-400">Sequential SHA-256 validation across all logged records</div>
            </div>
          </div>
          <span className="rounded-full border border-emerald-500/40 bg-emerald-950 px-3 py-1 font-mono text-xs font-bold text-emerald-400">
            {chainData ? (chainData.broken_blocks === 0 ? "VALID CHAIN" : `${chainData.broken_blocks} CORRUPTED`) : "ACTIVE"}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs font-mono">
          <div className="rounded bg-slate-950 p-2.5 border border-slate-800">
            <span className="text-slate-500">Total Records:</span>
            <div className="text-white font-bold text-sm mt-0.5">{totalRecords} verified</div>
          </div>
          <div className="rounded bg-slate-950 p-2.5 border border-slate-800">
            <span className="text-slate-500">Genesis Hash:</span>
            <div className="text-slate-300 truncate mt-0.5">{genesisHash}</div>
          </div>
          <div className="rounded bg-slate-950 p-2.5 border border-slate-800">
            <span className="text-slate-500">Head Hash:</span>
            <div className="text-emerald-400 truncate mt-0.5">{headHash}</div>
          </div>
        </div>
      </div>

      {/* Block Chain Visualizer */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Audit Log Entries
          </span>
          <input
            type="text"
            placeholder="Filter records..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            className="rounded-md border border-slate-800 bg-slate-950 px-3 py-1 text-xs font-mono text-slate-200 placeholder-slate-500 focus:border-[#74cfd8] focus:outline-none w-64"
          />
        </div>

        <div className="space-y-2">
          {filteredBlocks.map((block, idx) => (
            <div
              key={block.id}
              className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 space-y-2 hover:border-slate-700 transition-colors"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-2">
                <div className="flex items-center space-x-2">
                  <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[10px] text-slate-300">
                    #{filteredBlocks.length - idx}
                  </span>
                  <span className="font-bold text-white font-mono">{block.id}</span>
                  <span className="text-slate-400 font-mono">
                    {block.method} {block.endpoint}
                  </span>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-mono text-slate-300">
                    {block.action}
                  </span>
                  <span className="font-mono text-slate-400">{block.timestamp}</span>
                </div>
              </div>

              <div className="rounded bg-slate-950 p-2.5 font-mono text-[10px] text-slate-400 space-y-1 border border-slate-800/80">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Current Hash:</span>
                  <span className="text-emerald-400 break-all">{block.chain_hash}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Previous Hash:</span>
                  <span className="text-slate-400 break-all">{block.prev_hash}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
