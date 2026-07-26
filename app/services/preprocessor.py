import re


PRICE_PATTERN = re.compile(r"(?:₹|Rs\.?)\s*[\d,]+", re.IGNORECASE)
PRODUCT_WORDS = re.compile(
    r"\b(linen|cotton|polo|shirt|t-shirt|tee|track pant|jeans|size|rating|review)\b",
    re.IGNORECASE,
)


def extract_product_evidence(markdown: str, max_chars: int = 6000) -> str:
    """
    Pull useful product-related sections from noisy retailer markdown.
    This is generic; later you can create store-specific parsers.
    """
    lines = [
        line.strip()
        for line in markdown.splitlines()
        if line.strip()
    ]

    evidence_blocks = []
    seen_blocks = set()

    # Find every price and keep the surrounding lines.
    # Usually titles and product links appear near the price in listing markdown.
    for index, line in enumerate(lines):
        if PRICE_PATTERN.search(line):
            start = max(0, index - 4)
            end = min(len(lines), index + 5)

            block = "\n".join(lines[start:end])

            if block not in seen_blocks:
                seen_blocks.add(block)
                evidence_blocks.append(block)

    # If there are no price sections, retain useful product-description lines.
    if not evidence_blocks:
        useful_lines = [
            line for line in lines
            if PRODUCT_WORDS.search(line)
        ]
        evidence_blocks.append("\n".join(useful_lines[:80]))

    result = "\n\n--- PRODUCT EVIDENCE ---\n\n".join(evidence_blocks)

    return result[:max_chars]