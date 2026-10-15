"""Privacy-preserving, deterministic style signals from user-authored examples.

No examples are stored here. Callers must obtain appropriate consent.
"""
from collections import Counter
from pydantic import BaseModel, Field
import re

class StyleProfile(BaseModel):
    example_count: int = Field(ge=0)
    average_words: float = Field(ge=0)
    lowercase_start_ratio: float = Field(ge=0, le=1)
    emoji_message_ratio: float = Field(ge=0, le=1)
    exclamation_message_ratio: float = Field(ge=0, le=1)
    question_message_ratio: float = Field(ge=0, le=1)
    common_markers: list[str]

MARKERS = ("lol", "haha", "lmao", "ngl", "fr", "tbh", "idk", "brb", "btw")
EMOJI = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")
WORDS = re.compile(r"\b[\w']+\b", re.UNICODE)

def extract_style_profile(examples: list[str]) -> StyleProfile:
    """Derive aggregate signals from explicitly supplied user-authored text."""
    if len(examples) > 500:
        raise ValueError("At most 500 examples are allowed")
    if any(not isinstance(s, str) or not s.strip() or len(s) > 5000 for s in examples):
        raise ValueError("Each example must be nonblank text up to 5000 characters")
    if not examples:
        return StyleProfile(example_count=0, average_words=0, lowercase_start_ratio=0,
                            emoji_message_ratio=0, exclamation_message_ratio=0,
                            question_message_ratio=0, common_markers=[])
    cleaned = [s.strip() for s in examples]
    tokens = [WORDS.findall(s) for s in cleaned]
    marker_counts = Counter(token.lower() for sentence in tokens for token in sentence if token.lower() in MARKERS)
    n = len(cleaned)
    return StyleProfile(
        example_count=n,
        average_words=round(sum(len(t) for t in tokens) / n, 2),
        lowercase_start_ratio=round(sum(s[0].isalpha() and s[0].islower() for s in cleaned) / n, 3),
        emoji_message_ratio=round(sum(bool(EMOJI.search(s)) for s in cleaned) / n, 3),
        exclamation_message_ratio=round(sum("!" in s for s in cleaned) / n, 3),
        question_message_ratio=round(sum("?" in s for s in cleaned) / n, 3),
        common_markers=[token for token, _ in sorted(marker_counts.items(), key=lambda pair: (-pair[1], pair[0]))][:5],
    )
