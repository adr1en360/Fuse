"""Live Agent Traffic Simulator for Fuse Web Dashboard.

Runs live synthetic traffic through the Fuse proxy on :8000 so the
web dashboard on :5173 updates in real time without clicking buttons.

Usage:
    .venv\\Scripts\\python demo/simulate_live.py
    .venv\\Scripts\\python demo/simulate_live.py --act 1
    .venv\\Scripts\\python demo/simulate_live.py --continuous
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

# Windows UTF-8 stdout configuration
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console(force_terminal=True, safe_box=True)
PROXY_URL = "http://localhost:8000"


async def check_proxy_health():
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{PROXY_URL}/health")
            return resp.status_code == 200
    except Exception:
        return False


async def act1_parallel_burst(client: httpx.AsyncClient, count: int = 10):
    console.print("\n[bold cyan]▶ Act 1: Search Fanout (10 Parallel Queries)[/bold cyan]")
    console.print("[dim]Simulates an agent issuing concurrent vector / document search calls.[/dim]")
    console.print("[dim]Watch your dashboard at http://localhost:5173 for 10 green FORWARD records...[/dim]")

    queries = [f"document-chunk-{i}" for i in range(count)]
    tasks = [
        client.get(
            f"{PROXY_URL}/search",
            params={"query": q},
            headers={"X-Session-ID": "live-act1-fanout", "X-Fuse-Service": "read_intensive"},
        )
        for q in queries
    ]

    responses = await asyncio.gather(*tasks, return_exceptions=True)
    success = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
    console.print(f"[green]✔ Act 1 completed: {success}/{count} calls forwarded instantly with zero false-positive blocks.[/green]")


async def act2_retry_storm(client: httpx.AsyncClient, count: int = 8):
    console.print("\n[bold yellow]▶ Act 2: Stuck 503 Retry Storm (8 Repeated Requests)[/bold yellow]")
    console.print("[dim]Simulates an agent hammering a flaky downstream endpoint.[/dim]")
    console.print("[dim]Watch your dashboard for amber BACKOFF records with injected delay...[/dim]")

    for i in range(count):
        t0 = time.time()
        try:
            resp = await client.post(
                f"{PROXY_URL}/flaky",
                json={"action": "fetch_user", "id": 404},
                headers={"X-Session-ID": "live-act2-retry", "X-Fuse-Service": "standard_api"},
            )
            elapsed = round((time.time() - t0) * 1000, 1)
            backoff = resp.headers.get("retry-after")
            action = resp.headers.get("x-fuse-action", "FORWARD")
            console.print(f"  [{i+1}/{count}] Status: {resp.status_code} | Action: {action} | Retry-After: {backoff}s ({elapsed}ms)")
        except Exception as e:
            console.print(f"  [{i+1}/{count}] Error: {e}")
        await asyncio.sleep(0.35)

    console.print("[yellow]✔ Act 2 completed: Jev detected retry storm and applied backoff delays.[/yellow]")


async def act3_tool_loop(client: httpx.AsyncClient, count: int = 6):
    console.print("\n[bold magenta]▶ Act 3: Tool Loop Anomaly (Cyclic Tool Execution)[/bold magenta]")
    console.print("[dim]Simulates alternating cyclical tool calls making zero forward state progress.[/dim]")
    console.print("[dim]Watch your dashboard for purple GEMINI escalation records with root-cause analysis...[/dim]")

    for i in range(count):
        endpoint = "/loop/step-A" if i % 2 == 0 else "/loop/step-B"
        t0 = time.time()
        try:
            resp = await client.get(
                f"{PROXY_URL}{endpoint}",
                params={"iter": i},
                headers={"X-Session-ID": "live-act3-loop", "X-Fuse-Service": "standard_api"},
            )
            elapsed = round((time.time() - t0) * 1000, 1)
            action = resp.headers.get("x-fuse-action", "FORWARD")
            layer = resp.headers.get("x-fuse-layer", "LAYER_1_NORMAL")
            console.print(f"  [{i+1}/{count}] {endpoint} -> Action: {action} ({layer}) in {elapsed}ms")
        except Exception as e:
            console.print(f"  [{i+1}/{count}] Error: {e}")
        await asyncio.sleep(0.4)

    console.print("[magenta]✔ Act 3 completed: Escape hatch triggered to Gemini Flash for diagnosis.[/magenta]")


async def act4_traffic_flood(client: httpx.AsyncClient, count: int = 25):
    console.print("\n[bold red]▶ Act 4: Traffic Flood (25 Rapid Requests Exceeding Ceiling)[/bold red]")
    console.print("[dim]Simulates a rogue agent bursting past the 20-call limit.[/dim]")
    console.print("[dim]Watch your dashboard for red BLOCK (HTTP 429) records enforced by Layer 1...[/dim]")

    tasks = [
        client.post(
            f"{PROXY_URL}/search",
            json={"query": f"flood-item-{i}"},
            headers={"X-Session-ID": "live-act4-flood", "X-Fuse-Service": "high_consequence"},
        )
        for i in range(count)
    ]

    responses = await asyncio.gather(*tasks, return_exceptions=True)
    blocked = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 429)
    forwarded = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)

    console.print(f"[red]✔ Act 4 completed: {forwarded} forwarded, {blocked} hard-blocked with HTTP 429 (ceiling limit: 20 calls).[/red]")


async def print_live_summary(client: httpx.AsyncClient):
    try:
        resp = await client.get(f"{PROXY_URL}/api/metrics")
        if resp.status_code == 200:
            data = resp.json()
            stats = data.get("stats", data)
            table = Table(title="Fuse Proxy Live Status", border_style="cyan")
            table.add_column("Metric", style="bold white")
            table.add_column("Value", style="bold green", justify="right")
            table.add_row("Total Intercepted Calls", str(stats.get("total_calls", 0)))
            table.add_row("Forwarded Calls", str(stats.get("forwarded", 0)))
            table.add_row("Backoff Applied", str(stats.get("backoff_applied", 0)))
            table.add_row("Blocked Calls (HTTP 429)", str(stats.get("blocked", 0)))
            table.add_row("Escaped to Gemini Flash", str(stats.get("escaped_to_llm", 0)))
            table.add_row("Layer 1 Ceiling Trips", str(stats.get("layer1_trips", 0)))
            table.add_row("Layer 2 Jev Trips", str(stats.get("layer2_jev_trips", 0)))
            table.add_row("Layer 3 Gemini Trips", str(stats.get("layer3_gemini_trips", 0)))
            console.print("\n")
            console.print(table)
    except Exception:
        pass


async def main():
    parser = argparse.ArgumentParser(description="Live traffic generator for Fuse web console")
    parser.add_argument("--act", type=int, choices=[1, 2, 3, 4], help="Run a specific act (1 to 4)")
    parser.add_argument("--continuous", action="store_true", help="Run traffic continuously in a loop")
    parser.add_argument("--interval", type=float, default=2.5, help="Pause between acts in seconds")
    args = parser.parse_args()

    console.print(
        Panel.fit(
            "[bold white]Fuse Live Traffic Generator[/bold white]\n"
            "[cyan]Streaming real agent traffic to web console at http://localhost:5173[/cyan]",
            border_style="cyan",
        )
    )

    is_healthy = await check_proxy_health()
    if not is_healthy:
        console.print("[bold red]Error: Could not connect to Fuse proxy at http://localhost:8000/health[/bold red]")
        console.print("Please start the proxy first: .venv\\Scripts\\python -m uvicorn src.proxy:app --port 8000")
        return

    console.print("[green]✔ Proxy connected on http://localhost:8000[/green]")
    console.print("[dim]Open http://localhost:5173 in your browser to watch real-time updates.[/dim]")

    async with httpx.AsyncClient(timeout=15.0) as client:
        while True:
            if args.act == 1:
                await act1_parallel_burst(client)
            elif args.act == 2:
                await act2_retry_storm(client)
            elif args.act == 3:
                await act3_tool_loop(client)
            elif args.act == 4:
                await act4_traffic_flood(client)
            else:
                await act1_parallel_burst(client)
                await asyncio.sleep(args.interval)

                await act2_retry_storm(client)
                await asyncio.sleep(args.interval)

                await act3_tool_loop(client)
                await asyncio.sleep(args.interval)

                await act4_traffic_flood(client)

            await print_live_summary(client)

            if not args.continuous:
                break

            console.print(f"\n[dim]Waiting {args.interval}s before next cycle... Press Ctrl+C to stop.[/dim]")
            await asyncio.sleep(args.interval)

    console.print("\n[bold green]Traffic simulation complete. Check your browser to inspect decision traces.[/bold green]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Simulation stopped by user.[/yellow]")
