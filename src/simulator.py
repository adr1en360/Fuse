"""Agent traffic pattern simulator for testing and live demonstrations.

Simulates 4 distinct agent behaviors:
1. Parallel Burst: Concurrent RAG search requests with different arguments.
2. Retry Storm: Stuck agent repeatedly retrying a 503 endpoint with identical payload.
3. Unrecognized / Loop Bug: Cyclic alternating tool calls with no state advancement.
4. Catastrophic Burst: Rogue agent exceeding hard ceiling (e.g., 25 calls in 2 seconds).
"""

import asyncio
import sys
import time
from typing import List
import httpx
from rich.console import Console

# Configure UTF-8 for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(force_terminal=True, safe_box=True)


class AgentTrafficSimulator:
    """Generates synthetic agent traffic against the Fuse proxy."""

    def __init__(self, proxy_base_url: str = "http://localhost:8000"):
        self.proxy_base_url = proxy_base_url.rstrip("/")

    async def run_parallel_burst(self, session_id: str = "agent-burst", count: int = 10) -> List[httpx.Response]:
        """Act 1: Generates legitimate concurrent document retrieval calls."""
        console.print("\n[bold cyan]▶ Launching Act 1: Parallel Search Burst (10 concurrent requests)...[/bold cyan]")
        queries = [f"document-section-{i}" for i in range(count)]

        async with httpx.AsyncClient(timeout=10.0) as client:
            tasks = [
                client.get(
                    f"{self.proxy_base_url}/search",
                    params={"query": q},
                    headers={"X-Session-ID": session_id, "X-Fuse-Service": "search"},
                )
                for q in queries
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            valid_responses = [r for r in responses if isinstance(r, httpx.Response)]
            console.print(f"[green]✔ Parallel burst finished: {len(valid_responses)} completed.[/green]")
            return valid_responses

    async def run_retry_storm(self, session_id: str = "agent-retry", count: int = 10) -> List[httpx.Response]:
        """Act 2: Generates an agent stuck in an error loop retrying identical payload."""
        console.print("\n[bold yellow]▶ Launching Act 2: Stuck Retry Storm (10 repeated identical calls to flaky endpoint)...[/bold yellow]")
        responses = []

        async with httpx.AsyncClient(timeout=10.0) as client:
            for i in range(count):
                try:
                    resp = await client.post(
                        f"{self.proxy_base_url}/flaky",
                        json={"action": "fetch_user_data", "user_id": 999},
                        headers={"X-Session-ID": session_id, "X-Fuse-Service": "standard_api"},
                    )
                    responses.append(resp)
                    console.print(f"  Attempt {i+1}: status={resp.status_code}")
                except Exception as e:
                    console.print(f"  Attempt {i+1} error: {e}")
                await asyncio.sleep(0.05)  # Fast repeating without backoff

            console.print(f"[yellow]✔ Retry storm finished: {len(responses)} calls evaluated.[/yellow]")
            return responses

    async def run_loop_or_unrecognized(self, session_id: str = "agent-loop", count: int = 10) -> List[httpx.Response]:
        """Act 3: Generates alternating calls making no progress, tripping escape hatch."""
        console.print("\n[bold magenta]▶ Launching Act 3: Ambiguous Loop Bug / Unrecognized Pattern...[/bold magenta]")
        responses = []

        async with httpx.AsyncClient(timeout=10.0) as client:
            for i in range(count):
                endpoint = "/loop/step-A" if i % 2 == 0 else "/loop/step-B"
                try:
                    resp = await client.get(
                        f"{self.proxy_base_url}{endpoint}",
                        params={"seq": i // 2},
                        headers={"X-Session-ID": session_id, "X-Fuse-Service": "standard_api"},
                    )
                    responses.append(resp)
                    console.print(f"  Step {i+1} ({endpoint}): status={resp.status_code}")
                except Exception as e:
                    console.print(f"  Step {i+1} error: {e}")
                await asyncio.sleep(0.05)

            console.print(f"[magenta]✔ Loop test finished: {len(responses)} calls evaluated.[/magenta]")
            return responses

    async def run_catastrophic_ceiling(self, session_id: str = "agent-rogue", count: int = 25) -> List[httpx.Response]:
        """Act 4: Blasts traffic past the deterministic hard ceiling (20 calls)."""
        console.print("\n[bold red]▶ Launching Act 4: Catastrophic Rogue Burst (25 calls in < 1 second)...[/bold red]")
        responses = []

        async with httpx.AsyncClient(timeout=10.0) as client:
            tasks = [
                client.post(
                    f"{self.proxy_base_url}/search",
                    json={"query": f"blast-{i}"},
                    headers={"X-Session-ID": session_id},
                )
                for i in range(count)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, httpx.Response):
                    responses.append(r)

            blocked = sum(1 for r in responses if r.status_code == 429)
            console.print(f"[red]✔ Catastrophic test finished: {blocked}/{len(responses)} requests blocked by Hard Ceiling.[/red]")
            return responses


simulator = AgentTrafficSimulator()
