import json
import re

from google import genai
from google.genai import types

from app.ai.base import AIProvider, CategorySuggestion, ClaimAnalysisResult
from app.ai.prompts import build_category_suggestion_prompt, build_gemini_prompt
from app.config import settings


def _extract_json(text: str) -> str:
    """Extract JSON from text — handles markdown fences, reasoning preamble, and raw JSON.

    Reasoning models tend to emit thinking text BEFORE the final JSON, so we
    search from the right to find the last complete {...} block.
    """
    # 1. Markdown fences (```json ... ```)
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    # 2. Last complete {...} block — robust against reasoning preamble
    last_open = text.rfind('{')
    if last_open != -1:
        last_close = text.rfind('}')
        if last_close > last_open:
            return text[last_open:last_close + 1].strip()
    return text.strip()


class GeminiProvider(AIProvider):
    def __init__(self):
        # Disable the SDK's built-in retry (attempts=1 = no retry after failure).
        # We handle retries at a higher level via the provider fallback chain in router.py.
        # Without this, a 503 from Gemini triggers an internal backoff retry that can
        # push total response time well beyond our ai_timeout_seconds budget, causing
        # the ThreadPoolExecutor timeout to fire mid-retry and silently discard a
        # successful late response.
        self._client = genai.Client(
            api_key=settings.google_ai_api_key,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )
        self._config = types.GenerateContentConfig(
            temperature=0,
            max_output_tokens=500,
            response_mime_type="application/json",
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

    def analyze_claim(self, amount: float, category: str, description: str) -> ClaimAnalysisResult:
        prompt = build_gemini_prompt(category, amount, description)
        response = self._client.models.generate_content(
            model=settings.google_ai_model,
            contents=prompt,
            config=self._config,
        )
        raw = _extract_json(response.text)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Gemini returned non-JSON response: {raw[:200]}") from exc

        if "summary" not in data or "mismatch_flag" not in data:
            raise ValueError(f"Gemini response missing required fields: {list(data.keys())}")

        return ClaimAnalysisResult(
            summary=data["summary"],
            mismatch_flag=bool(data["mismatch_flag"]),
            mismatch_reason=data.get("mismatch_reason"),
            provider_used="gemini",
        )

    def suggest_category(self, description: str, categories: list[str]) -> CategorySuggestion:
        prompt = build_category_suggestion_prompt(description, categories)
        response = self._client.models.generate_content(
            model=settings.google_ai_model,
            contents=prompt,
            config=self._config,
        )
        raw = _extract_json(response.text)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Gemini returned non-JSON: {raw[:200]}") from exc
        return CategorySuggestion(**data)
