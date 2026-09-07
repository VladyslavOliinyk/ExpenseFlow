import json
import re

import google.generativeai as genai

from app.ai.base import AIProvider, ClaimAnalysisResult
from app.ai.prompts import build_gemini_prompt
from app.config import settings


def _extract_json(text: str) -> str:
    """Extract JSON from text, stripping markdown fences and surrounding prose."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text.strip()


class GeminiProvider(AIProvider):
    def __init__(self):
        genai.configure(api_key=settings.google_ai_api_key)
        self._model = genai.GenerativeModel(
            model_name=settings.google_ai_model,
            generation_config=genai.GenerationConfig(
                temperature=0,
                max_output_tokens=300,
            ),
        )

    def analyze_claim(self, amount: float, category: str, description: str) -> ClaimAnalysisResult:
        prompt = build_gemini_prompt(category, amount, description)
        response = self._model.generate_content(prompt)
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
