"""Automated 4-Act Live Demonstration Script for Fuse.

Usage:
1. Start mock server: python demo/mock_server.py
2. Start Fuse proxy:  python -m uvicorn src.proxy:app --port 8000
3. Run this demo:     python demo/run_demo.py
"""

import asyncio
import sys
from pathlib import Path
import time

# Configure UTF-8 for Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

from src.dashboard import dashboard
from src.simulator import simulator

console = Console(force_terminal=True, safe_box=True)


async def main():
    console.print(
        Panel.fit(
            "[bold white]🛡️ FUSE — Intelligent Circuit Breaker for Autonomous Agents[/bold white]\n"
            "[italic cyan]Powered by Jev (TypeSafe AI System One) & Gemini 3.8 Flash[/italic cyan]\n"
            "[dim]Engineering Excellence & Breakthrough Innovation Demo[/dim]",
            border_style="cyan",
        )
    )

    console.print("[dim]Checking connection to Fuse proxy at http://localhost:8000/health...[/dim]")
    import httpx
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get("http://localhost:8000/health")
            if resp.status_code == 200:
                console.print("[green]✔ Connected to Fuse proxy successfully.[/green]\n")
            else:
                console.print(f"[yellow]Proxy returned status {resp.status_code}. Proceeding...[/yellow]\n")
    except Exception:
        console.print(
            "[bold red]✖ Could not connect to Fuse proxy at http://localhost:8000.\n"
            "Please ensure the proxy is running: python -m uvicorn src.proxy:app --port 8000[/bold red]\n"
        )
        return

    # ACT 1: Parallel Burst
    console.print("[bold white underline]ACT 1: Parallel Work Burst[/bold white underline]")
    console.print("[dim]Agent issues 10 simultaneous searches across distinct documents.[/dim]")
    await simulator.run_parallel_burst(session_id="agent-act1", count=10)
    await asyncio.sleep(2.0)

    # ACT 2: Retry Storm
    console.print("\n[bold white underline]ACT 2: Stuck Retry Storm[/bold white underline]")
    console.print("[dim]Agent repeatedly hammers a failing 503 endpoint with the exact same payload.[/dim]")
    await simulator.run_retry_storm(session_id="agent-act2", count=10)
    await asyncio.sleep(2.0)

    # ACT 3: Loop Bug / Unrecognized Pattern
    console.print("\n[bold white underline]ACT 3: Loop Bug & Unrecognized Escape Hatch[/bold white underline]")
    console.print("[dim]Agent cycles between alternating steps. Jev triggers 'unrecognized' escape to Gemini 3.8 Flash.[/dim]")
    await simulator.run_loop_or_unrecognized(session_id="agent-act3", count=10)
    await asyncio.sleep(2.0)

    # ACT 4: Catastrophic Hard Ceiling
    console.print("\n[bold white underline]ACT 4: Deterministic Hard Ceiling (Layer 1 Inviolable)[/bold white underline]")
    console.print("[dim]Agent goes completely rogue with 25 rapid calls. Pure counting blocks it with zero AI bypass.[/dim]")
    await simulator.run_catastrophic_ceiling(session_id="agent-act4", count=25)
    await asyncio.sleep(1.0)

    # Final Summary Table fetched live from the proxy
    console.print("\n")
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            m_resp = await client.get("http://localhost:8000/metrics")
            if m_resp.status_code == 200:
                stats = m_resp.json()
                from rich.table import Table
                table = Table(title="🛡️ Fuse Intelligent Circuit Breaker — Real-Time Live Metrics", border_style="cyan")
                table.add_column("Metric", style="bold white")
                table.add_column("Value", style="bold green", justify="right")
                table.add_row("Total Intercepted Calls", str(stats.get("total_calls", 0)))
                table.add_row("Forwarded (Safe / Burst)", str(stats.get("forwarded", 0)))
                table.add_row("Backoff Applied (Retry Storm)", str(stats.get("backoff_applied", 0)))
                table.add_row("Blocked (Hard Ceiling / Loop)", str(stats.get("blocked", 0)))
                table.add_row("Escaped to Gemini 3.8 Flash", str(stats.get("escaped_to_llm", 0)))
                table.add_row("Human Escalations", str(stats.get("escalated_human", 0)))
                table.add_row("Layer 1 Deterministic Trips", str(stats.get("layer1_trips", 0)))
                table.add_row("Layer 2 Jev System One Trips", str(stats.get("layer2_jev_trips", 0)))
                table.add_row("Layer 3 Gemini Flash Trips", str(stats.get("layer3_gemini_trips", 0)))
                console.print(table)
            else:
                dashboard.render_summary_table()
    except Exception:
        dashboard.render_summary_table()

    console.print("\n[bold green]✔ 4-Act Demo sequence completed. All records preserved in audit.jsonl.[/bold green]")


if __name__ == "__main__":
    asyncio.run(main())
