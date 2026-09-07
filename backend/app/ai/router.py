"""
AI router with fallback chain: Claude → Gemini → (None if all fail).
Each provider gets AI_TIMEOUT_SECONDS. Logs every attempt to AiCallLog.
"""
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from sqlalchemy.orm import Session

from app.ai.base import AIProvider, CategorySuggestion, ClaimAnalysisResult
from app.config import settings
from app.models import AiCallLog

logger = logging.getLogger(__name__)


def _get_providers() -> list[AIProvider]:
    """Return providers based on AI_MODE setting."""
    from app.ai.mock_provider import MockProvider
    from app.ai.claude_provider import ClaudeProvider
    from app.ai.gemini_provider import GeminiProvider

    if settings.ai_mode == "mock":
        logger.info("Building AI providers: mode=mock → [MockProvider]")
        return [MockProvider()]

    providers: list[AIProvider] = []
    if settings.anthropic_api_key:
        providers.append(ClaudeProvider())
    if settings.google_ai_api_key:
        providers.append(GeminiProvider())

    logger.info(
        "Building AI providers: mode=%s → %s",
        settings.ai_mode,
        [p.__class__.__name__ for p in providers],
    )
    return providers


def _call_with_timeout(
    provider: AIProvider,
    amount: float,
    category: str,
    description: str,
    timeout: int,
) -> ClaimAnalysisResult:
    # Do NOT use the context-manager form of ThreadPoolExecutor here.
    # `with executor:` calls shutdown(wait=True) on exit, which blocks until the
    # underlying thread finishes — even after future.result() raises TimeoutError.
    # That caused observed latency of ~24s for a 5s timeout (the thread ran to
    # completion before the caller could log and move on to the next provider).
    # shutdown(wait=False) lets the thread finish in the background; we simply
    # discard its result. Note: the HTTP request to the provider is already in
    # flight and cannot be cancelled mid-stream — this is a known limitation of
    # synchronous HTTP clients in threads.
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(provider.analyze_claim, amount, category, description)
    try:
        return future.result(timeout=timeout)
    finally:
        executor.shutdown(wait=False)


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
            logger.warning("Provider %s timed out after %ss", provider_name, timeout)
        except Exception as e:
            error_msg = str(e)[:500]
            logger.warning("Provider %s failed: %s", provider_name, error_msg)

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


def suggest_category_with_fallback(
    description: str,
    categories: list[str],
) -> CategorySuggestion | None:
    """Try each provider for a category suggestion. No logging/DB. Returns None on total failure."""
    providers = _get_providers()
    timeout = settings.ai_timeout_seconds

    for provider in providers:
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(provider.suggest_category, description, categories)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            logger.warning("Provider %s timed out on suggest_category", provider.__class__.__name__)
        except Exception as e:
            logger.warning("Provider %s failed on suggest_category: %s", provider.__class__.__name__, e)
        finally:
            executor.shutdown(wait=False)

    return None
