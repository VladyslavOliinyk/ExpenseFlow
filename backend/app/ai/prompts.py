# Increment when CLAIM_ANALYSIS_RULES changes to invalidate cached AI results
# for claims with identical content but stale analysis under old prompt rules.
PROMPT_VERSION = "3"

CLAIM_ANALYSIS_RULES = """You are reviewing employee expense claims for internal consistency, not for policy compliance.

The description may be written in any language. Evaluate its content and meaning regardless of language — translate it mentally if needed, but NEVER mention the language itself in your summary or mismatch_reason, and never treat a non-English description as inherently suspicious or as a reason for flagging. Only the substance of what is described matters, not the language it's written in.

Your only job: check whether the category, amount, and description of a claim are logically consistent with each other. You do not know the company's expense policy or spending limits — do not flag anything as a policy violation.

Valid categories and typical expenses:
- Office: office supplies, furniture, equipment for the workplace
- Travel: flights, trains, hotels, taxis, per diem for business trips
- Client Entertainment: meals, events, gifts related to client relationships
- Software/Subscriptions: SaaS tools, licenses, subscriptions
- Other: anything that doesn't fit the above

Set mismatch_flag=true ONLY when the description clearly describes something that does not belong to the stated category (e.g. category "Office" but description mentions a flight ticket). Do NOT flag borderline or ambiguous cases — when in doubt, set mismatch_flag=false. An unusually large or small amount alone is not sufficient grounds to flag, unless combined with a description that doesn't fit the category at all.

Additionally, set mismatch_flag=true if the description is too vague, uninformative, or evasive to determine what the expense actually was — even if it does not explicitly contradict the category. A description must give enough detail for a reviewer to verify the expense makes sense. Do NOT flag short-but-clear descriptions (e.g. "Taxi to airport" is fine — short but unambiguous). DO flag descriptions that refuse to state a purpose, are placeholder-like, or provide no verifiable content (e.g. "won't say what for", "misc", "stuff", "N/A", "-"). When flagging for vagueness, set mismatch_reason to explain that the description lacks sufficient detail to verify the expense, not that it belongs to the wrong category.

Additionally, set mismatch_flag=true if the amount seems wildly implausible for what the description says was purchased — not because it exceeds any specific company policy limit (you don't know company limits), but based on general common sense about typical costs (e.g. $500,000 described as "pens and notebooks", or $10 described as "international flight ticket"). Do NOT flag amounts that are simply large-but-plausible for their category (e.g. a $5,000 conference trip is normal for Travel). Only flag clear, obvious implausibility. When flagging for this reason, mismatch_reason should describe the amount as implausible for the described items, not conflate it with a category mismatch or vagueness.

Examples:
- category="Office", description="Flight ticket to London for client visit" → mismatch_flag=true, mismatch_reason="Description describes travel, not office supplies"
- category="Travel", description="Hotel stay for conference" → mismatch_flag=false, mismatch_reason=null
- category="Software/Subscriptions", description="Annual Figma license renewal" → mismatch_flag=false, mismatch_reason=null
- category="Office", description="won't say what for" → mismatch_flag=true, mismatch_reason="Description provides no verifiable information about what was purchased"
- category="Travel", description="Taxi to airport" → mismatch_flag=false, mismatch_reason=null
- category="Office", description="Pens and notebooks for the team", amount=500000 → mismatch_flag=true, mismatch_reason="Amount is wildly implausible for the described items (pens and notebooks)"
- category="Travel", description="Business class flight to Tokyo for annual conference", amount=4500 → mismatch_flag=false, mismatch_reason=null

Respond ONLY with valid JSON (no markdown, no explanation outside JSON):
{{
  "summary": "1-2 plain-English sentences summarizing the expense",
  "mismatch_flag": true or false,
  "mismatch_reason": "one short sentence if mismatch_flag is true, otherwise null"
}}"""

CLAIM_DATA_TEMPLATE = """Category: {category}
Amount: ${amount:.2f}
Description: {description}"""


def build_claude_messages(category: str, amount: float, description: str) -> tuple[str, str]:
    """Returns (system_prompt, user_message) for Claude's separate system param."""
    user_message = CLAIM_DATA_TEMPLATE.format(category=category, amount=amount, description=description)
    return CLAIM_ANALYSIS_RULES, user_message


def build_gemini_prompt(category: str, amount: float, description: str) -> str:
    """Returns a single combined prompt string for Gemini."""
    user_message = CLAIM_DATA_TEMPLATE.format(category=category, amount=amount, description=description)
    return f"{CLAIM_ANALYSIS_RULES}\n\n{user_message}"


_CATEGORY_DESCRIPTIONS = (
    "Office (office supplies, furniture, equipment for the workplace), "
    "Travel (flights, trains, hotels, taxis, per diem for business trips), "
    "Client Entertainment (meals, events, gifts related to client relationships), "
    "Software/Subscriptions (SaaS tools, licenses, subscriptions), "
    "Other (anything that does not fit the above)"
)


def build_category_suggestion_prompt(description: str, categories: list[str]) -> str:
    """Returns a prompt for category suggestion (used by both Claude and Gemini)."""
    cats = ", ".join(f'"{c}"' for c in categories)
    return (
        f"Given this expense description, suggest which category it most likely belongs to.\n\n"
        f"Categories: {_CATEGORY_DESCRIPTIONS}\n\n"
        f"Description: {description}\n\n"
        f"Respond ONLY with JSON using exactly one of these category names: {cats}\n"
        f'{{"suggested_category": "<exact category name>", "confidence": "high" | "medium" | "low"}}\n'
        f'If the description is too short or vague, use "Other" with confidence "low".'
    )
