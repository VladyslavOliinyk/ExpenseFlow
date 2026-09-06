"""
Tests for the AI router (fallback chain, deduplication, error handling).
Uses fake providers — no real API calls.
"""
import pytest
from unittest.mock import MagicMock, patch

from app.ai.base import AIProvider, ClaimAnalysisResult
from app.ai.router import analyze_claim_with_fallback


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(provider: str = "mock") -> ClaimAnalysisResult:
    return ClaimAnalysisResult(
        summary="Test summary",
        mismatch_flag=False,
        mismatch_reason=None,
        provider_used=provider,  # type: ignore[arg-type]
    )


class _OKProvider(AIProvider):
    def __init__(self, provider_name: str = "mock"):
        self._name = provider_name

    def analyze_claim(self, amount, category, description) -> ClaimAnalysisResult:
        return _make_result(self._name)


class _FailProvider(AIProvider):
    def __init__(self, exc: Exception):
        self._exc = exc

    def analyze_claim(self, amount, category, description) -> ClaimAnalysisResult:
        raise self._exc


def _fake_db():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    return db


# ---------------------------------------------------------------------------
# Test 1: 401 from first provider → falls back to second
# ---------------------------------------------------------------------------

def test_401_from_first_provider_falls_back_to_second():
    auth_error = Exception("401 Unauthorized: invalid api key")
    providers = [_FailProvider(auth_error), _OKProvider("mock")]

    with patch("app.ai.router._get_providers", return_value=providers):
        result = analyze_claim_with_fallback(
            claim_id=1,
            amount=100.0,
            category="Travel",
            description="Flight ticket",
            db=_fake_db(),
        )

    assert result is not None
    assert result.provider_used == "mock"


# ---------------------------------------------------------------------------
# Test 2: all providers fail → returns None, never raises
# ---------------------------------------------------------------------------

def test_all_providers_fail_returns_none():
    providers = [
        _FailProvider(Exception("401 Unauthorized")),
        _FailProvider(Exception("503 Service Unavailable")),
    ]

    with patch("app.ai.router._get_providers", return_value=providers):
        result = analyze_claim_with_fallback(
            claim_id=2,
            amount=50.0,
            category="Office",
            description="Printer paper",
            db=_fake_db(),
        )

    assert result is None


# ---------------------------------------------------------------------------
# Test 3: invalid JSON from provider → handled as provider error, no crash
# ---------------------------------------------------------------------------

def test_invalid_json_from_provider_handled_gracefully():
    providers = [
        _FailProvider(ValueError("Claude returned non-JSON response: Вот анализ:")),
        _OKProvider("mock"),
    ]

    with patch("app.ai.router._get_providers", return_value=providers):
        result = analyze_claim_with_fallback(
            claim_id=3,
            amount=200.0,
            category="Software",
            description="License renewal",
            db=_fake_db(),
        )

    assert result is not None
    assert result.provider_used == "mock"


# ---------------------------------------------------------------------------
# Test 4: deduplication — duplicate content_hash skips provider call
# ---------------------------------------------------------------------------

def test_deduplication_skips_provider_on_matching_hash():
    from app.models.claim import Claim
    from app.routers.claims import _run_ai_analysis

    existing_claim = MagicMock(spec=Claim)
    existing_claim.ai_summary = "Cached summary"
    existing_claim.ai_mismatch_flag = False
    existing_claim.ai_mismatch_reason = None
    existing_claim.ai_provider_used = "mock"

    new_claim = MagicMock(spec=Claim)
    new_claim.id = 10
    new_claim.content_hash = "abc123"
    new_claim.category = MagicMock()
    new_claim.category.name = "Travel"
    new_claim.amount = 100.0
    new_claim.description = "Same trip"

    db = _fake_db()
    # First DB query (load claim with joinedload): returns new_claim
    db.query.return_value.options.return_value.filter.return_value.first.return_value = new_claim
    # Second DB query (dedup lookup): returns existing cached claim
    db.query.return_value.filter.return_value.filter.return_value.filter.return_value.first.return_value = existing_claim

    # analyze_claim_with_fallback is imported inside _run_ai_analysis at call time,
    # so we patch the source module directly.
    with patch("app.ai.router.analyze_claim_with_fallback") as mock_analyze, \
         patch("app.routers.claims.SessionLocal_bg", return_value=db):
        _run_ai_analysis(10)
        mock_analyze.assert_not_called()
