import re


def preprocess_transcript(text: str) -> str:
    """
    Strips timestamps, filler words, extra blank lines, and normalizes spacing.
    """
    if not text:
        return ""

    # Remove timestamps like [00:12], [01:24:30], 00:12 Speaker:
    text = re.sub(r"\[\d{1,2}:\d{2}(?::\d{2})?\]", "", text)
    text = re.sub(r"^\s*\d{1,2}:\d{2}(?::\d{2})?\s*", "", text, flags=re.MULTILINE)

    # Remove filler words
    filler_patterns = [
        r"\bum+\b",
        r"\bumm+\b",
        r"\buh+\b",
        r"\bah+\b",
        r"\byou know\b"
    ]
    for pattern in filler_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Remove excessive spaces & tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove unnecessary blank lines
    text = re.sub(r"\n\s*\n+", "\n", text)

    # Clean spaces before punctuation
    text = re.sub(r"\s+([,.!?])", r"\1", text)

    return text.strip()
