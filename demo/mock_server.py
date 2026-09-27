"""Mock downstream target server running on port 9000.

Provides endpoints for the 4 demonstration acts:
- /search: normal & parallel search queries
- /flaky: returns 503 to trigger retry storms
- /charge: payment endpoint for high-risk mutating calls
- /loop: tool endpoints for cyclical loop demonstrations
"""

import time
from fastapi import FastAPI, Response
from pydantic import BaseModel

app = FastAPI(title="Mock Downstream Target Service", version="1.0.0")


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


class PaymentRequest(BaseModel):
    amount: float
    currency: str = "USD"
    account_id: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "mock_downstream", "port": 9000}


@app.api_route("/search", methods=["GET", "POST"])
def search(query: str = "ai agents"):
    time.sleep(0.02)  # 20ms simulated latency
    return {
        "status": "success",
        "query": query,
        "results": [
            {"id": "doc-1", "title": "Understanding Circuit Breakers"},
            {"id": "doc-2", "title": "TypeSafe System One Models"},
        ],
    }


@app.api_route("/flaky", methods=["GET", "POST"])
def flaky_endpoint():
    # Returns 503 to induce agent retry loop
    return Response(
        status_code=503,
        content='{"error": "Service Temporarily Unavailable", "code": 503}',
        media_type="application/json",
    )


@app.post("/charge")
def charge(payment: PaymentRequest):
    return {
        "status": "charged",
        "amount": payment.amount,
        "tx_id": f"tx_{int(time.time()*1000)}",
    }


@app.api_route("/loop/{step}", methods=["GET", "POST"])
def loop_step(step: str):
    return {"step": step, "progress": "none", "state": "pending"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9000)
