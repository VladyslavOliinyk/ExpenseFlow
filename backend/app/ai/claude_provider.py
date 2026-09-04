import json

import anthropic

from app.ai.base import AIProvider, ClaimAnalysisResult
from app.config import settings

_SYSTEM_PROMPT = """You are a financial compliance assistant reviewing employee expense claims.
Analyze the claim and return a JSON object with exactly these fields:
- summary: 1-2 sentence plain-English summary of the expense
- mismatch_flag: true if the expense seems suspicious, unusual for the category, or policy-violating; false otherwise
- mismatch_reason: short explanation if mismatch_flag is true, null otherwise

Respond ONLY with valid JSON. No markdown, no explanation outside JSON."""

_USER_TEMPLATE = """Category: {category}
Amount: ${amount:.2f}
Description: {description}"""


class ClaudeProvider(AIProvider):
    def __init__(self):
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def analyze_claim(self, amount: float, category: str, description: str) -> ClaimAnalysisResult:
        message = self._client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            temperature=0,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": _USER_TEMPLATE.format(
                        category=category, amount=amount, description=description
                    ),
                }
            ],
        )
        raw = message.content[0].text.strip()
        data = json.loads(raw)
        return ClaimAnalysisResult(
            summary=data["summary"],
            mismatch_flag=bool(data["mismatch_flag"]),
            mismatch_reason=data.get("mismatch_reason"),
            provider_used="claude",
        )
