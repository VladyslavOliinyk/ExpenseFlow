import json
import os

from app.ai.base import AIProvider, ClaimAnalysisResult

_FIXTURES_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "sample_responses.json")


class MockProvider(AIProvider):
    """Deterministic provider for development and testing. No network calls."""

    def __init__(self):
        with open(_FIXTURES_PATH, encoding="utf-8") as f:
            self._fixtures: list[dict] = json.load(f)

    def analyze_claim(self, amount: float, category: str, description: str) -> ClaimAnalysisResult:
        # Match on category first, then pick by mismatch pattern heuristic
        candidates = [f for f in self._fixtures if f["category"] == category]
        if not candidates:
            candidates = self._fixtures

        # Simple heuristic: pick high-amount fixture if amount > 500, else low-amount
        high_amount = [c for c in candidates if c["response"]["mismatch_flag"]]
        low_amount = [c for c in candidates if not c["response"]["mismatch_flag"]]

        fixture = (high_amount[0] if amount > 500 and high_amount else
                   low_amount[0] if low_amount else
                   candidates[0])

        resp = fixture["response"]
        return ClaimAnalysisResult(
            summary=resp["summary"],
            mismatch_flag=resp["mismatch_flag"],
            mismatch_reason=resp.get("mismatch_reason"),
            provider_used="mock",
        )
