import json

import google.generativeai as genai

from app.ai.base import AIProvider, ClaimAnalysisResult
from app.config import settings

_PROMPT_TEMPLATE = """You are a financial compliance assistant reviewing employee expense claims.
Analyze this claim and respond ONLY with valid JSON (no markdown, no explanation):
{{
  "summary": "1-2 sentence plain-English summary",
  "mismatch_flag": true or false,
  "mismatch_reason": "explanation if mismatch_flag is true, null otherwise"
}}

Category: {category}
Amount: ${amount:.2f}
Description: {description}"""


class GeminiProvider(AIProvider):
    def __init__(self):
        genai.configure(api_key=settings.google_ai_api_key)
        self._model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=genai.GenerationConfig(
                temperature=0,
                max_output_tokens=300,
            ),
        )

    def analyze_claim(self, amount: float, category: str, description: str) -> ClaimAnalysisResult:
        prompt = _PROMPT_TEMPLATE.format(
            category=category, amount=amount, description=description
        )
        response = self._model.generate_content(prompt)
        raw = response.text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw.strip())
        return ClaimAnalysisResult(
            summary=data["summary"],
            mismatch_flag=bool(data["mismatch_flag"]),
            mismatch_reason=data.get("mismatch_reason"),
            provider_used="gemini",
        )
