from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel


class ClaimAnalysisResult(BaseModel):
    summary: str
    mismatch_flag: bool
    mismatch_reason: str | None
    provider_used: Literal["claude", "gemini", "mock"]


class CategorySuggestion(BaseModel):
    suggested_category: Literal["Office", "Travel", "Client Entertainment", "Software/Subscriptions", "Other"]
    confidence: Literal["high", "medium", "low"]


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

    def suggest_category(
        self,
        description: str,
        categories: list[str],
    ) -> CategorySuggestion:
        """Suggest the most appropriate category for a description. Raises on failure."""
        raise NotImplementedError
