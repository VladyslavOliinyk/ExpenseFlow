import json
import re

import anthropic

from app.ai.base import AIProvider, CategorySuggestion, ClaimAnalysisResult
from app.ai.prompts import build_category_suggestion_prompt, build_claude_messages
from app.config import settings


def _extract_json(text: str) -> str:
    """Extract JSON from text, stripping markdown fences and surrounding prose."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text.strip()


class ClaudeProvider(AIProvider):
    def __init__(self):
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def analyze_claim(self, amount: float, category: str, description: str) -> ClaimAnalysisResult:
        system_prompt, user_message = build_claude_messages(category, amount, description)
        message = self._client.messages.create(
            model=settings.anthropic_model,
            max_tokens=500,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
        )
        raw = _extract_json(message.content[0].text)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Claude returned non-JSON response: {raw[:200]}") from exc

        if "summary" not in data or "mismatch_flag" not in data:
            raise ValueError(f"Claude response missing required fields: {list(data.keys())}")

        return ClaimAnalysisResult(
            summary=data["summary"],
            mismatch_flag=bool(data["mismatch_flag"]),
            mismatch_reason=data.get("mismatch_reason"),
            provider_used="claude",
        )

    def suggest_category(self, description: str, categories: list[str]) -> CategorySuggestion:
        prompt = build_category_suggestion_prompt(description, categories)
        message = self._client.messages.create(
            model=settings.anthropic_model,
            max_tokens=100,
            system="You categorize expense descriptions. Respond only with valid JSON.",
            messages=[{"role": "user", "content": prompt}],
        )
        raw = _extract_json(message.content[0].text)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Claude returned non-JSON: {raw[:200]}") from exc
        return CategorySuggestion(**data)
