from pydantic import BaseModel


class AiMetrics(BaseModel):
    total_analyzed: int
    mismatch_count: int
    mismatch_rate: float
    avg_latency_ms: float | None
    provider_breakdown: dict[str, int]
