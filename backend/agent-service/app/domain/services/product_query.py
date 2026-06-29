import re

# Matches catalog names like "Accessories Product 10" (Category + Product + id)
_CATALOG_PRODUCT_PATTERN = re.compile(
    r"\b([A-Z][a-zA-Z]*\s+Product\s+\d+)\b",
)

_PRICE_QUESTION_PATTERNS = [
    re.compile(r"how much does (?:it )?cost (.+?)\??$", re.IGNORECASE),
    re.compile(r"how much does (.+?) cost\??$", re.IGNORECASE),
    re.compile(r"how much is (?:the )?(.+?)\??$", re.IGNORECASE),
    re.compile(r"what(?:'s| is) the price of (.+?)\??$", re.IGNORECASE),
    re.compile(r"price of (?:the )?(.+?)\??$", re.IGNORECASE),
    re.compile(r"how much for (?:the )?(.+?)\??$", re.IGNORECASE),
]

_FILLER_PREFIX = re.compile(
    r"^(?:how much does|how much is|what is the price of|price of|"
    r"do you have|do you sell|is)\s+",
    re.IGNORECASE,
)
_TRAILING_COST = re.compile(r"\s+cost\??$", re.IGNORECASE)


def extract_product_search_query(message: str) -> str:
    """
    Pull a product name or search phrase out of a natural-language question.

    "how much does it cost Accessories Product 10?"
    → "Accessories Product 10"
    """
    text = message.strip()
    if not text:
        return text

    catalog_match = _CATALOG_PRODUCT_PATTERN.search(text)
    if catalog_match:
        return catalog_match.group(1).strip()

    for pattern in _PRICE_QUESTION_PATTERNS:
        match = pattern.search(text)
        if match:
            candidate = match.group(1).strip(" ?.")
            if candidate and candidate.lower() not in {"it", "this", "that"}:
                return candidate

    cleaned = _FILLER_PREFIX.sub("", text)
    cleaned = _TRAILING_COST.sub("", cleaned)
    cleaned = cleaned.strip(" ?.")

    return cleaned or text
