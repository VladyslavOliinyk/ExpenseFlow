"""
AI router with fallback chain: Claude → Gemini → (None if all fail).
Each provider gets AI_TIMEOUT_SECONDS. Logs every attempt to AiCallLog.
"""
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from sqlalchemy.orm import Session

from app.ai.base import AIProvider, ClaimAnalysisResult
from app.config import settings
from app.models import AiCallLog


def _get_providers() -> list[AIProvider]:
    """Return providers based on AI_MODE setting."""
    from app.ai.mock_provider import MockProvider
    from app.ai.claude_provider import ClaudeProvider
    from app.ai.gemini_provider import GeminiProvider

    if settings.ai_mode == "mock":
        return [MockProvider()]

    providers: list[AIProvider] = []
    if settings.anthropic_api_key:
        providers.append(ClaudeProvider())
    if settings.google_ai_api_key:
        providers.append(GeminiProvider())

    # Always have mock as final fallback so we never return nothing in dev
    if settings.environment == "development":
        providers.append(MockProvider())

    return providers or [MockProvider()]


def _call_with_timeout(
    provider: AIProvider,
    amount: float,
    category: str,
    description: str,
    timeout: int,
) -> ClaimAnalysisResult:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(provider.analyze_claim, amount, category, description)
        return future.result(timeout=timeout)


def analyze_claim_with_fallback(
    claim_id: int,
    amount: float,
    category: str,
    description: str,
    db: Session,
) -> ClaimAnalysisResult | None:
    """
    Try each provider in order. Log every attempt. Return first success or None.
    Never raises — caller gets None on total failure.
    """
    providers = _get_providers()
    timeout = settings.ai_timeout_seconds

    for provider in providers:
        provider_name = provider.__class__.__name__.replace("Provider", "").lower()
        start = time.monotonic()
        success = False
        error_msg = None
        result = None

        try:
            result = _call_with_timeout(provider, amount, category, description, timeout)
            success = True
        except FuturesTimeoutError:
            error_msg = f"Timeout after {timeout}s"
        except Exception as e:
            error_msg = str(e)[:500]

        latency_ms = int((time.monotonic() - start) * 1000)

        log = AiCallLog(
            claim_id=claim_id,
            provider=provider_name,
            latency_ms=latency_ms,
            success=success,
            error_message=error_msg,
        )
        db.add(log)
        db.commit()

        if success and result:
            return result

    return None
