from abc import ABC, abstractmethod
from pydantic import BaseModel


class ClaimAnalysisResult(BaseModel):
    summary: str
    mismatch_flag: bool
    mismatch_reason: str | None
    provider_used: str


class AIProvider(ABC):
    @abstractmethod
    def analyze_claim(
        self,
        amount: float,
        category: str,
        description: str,
    ) -> ClaimAnalysisResult:
        """Analyze a claim and return structured result. Raises on failure."""
        ...
