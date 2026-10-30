import pytest
from pydantic import ValidationError

from app.provider import ReplyResponse


def response(texts):
    return {"provider": "synthetic", "candidates": [
        {"id": i, "text": text, "label": label}
        for i, (text, label) in enumerate(zip(texts, ("Natural", "Direct", "Playful")), 1)
    ]}


@pytest.mark.parametrize("first,second", [
    ("Meet  here", "meet here"),
    ("Meet\there", "meet here"),
    ("Meet\nhere", "meet here"),
    ("Meet\u00a0here", "meet here"),
])
def test_candidate_distinctness_matches_swift_whitespace_normalization(first, second):
    with pytest.raises(ValidationError, match="distinct"):
        ReplyResponse.model_validate(response([first, second, "Another suggestion"]))


def test_normalization_preserves_meaningful_punctuation_and_word_differences():
    answer = ReplyResponse.model_validate(response(["Are you free?", "Are you free!", "When are you free?"]))
    assert len(answer.candidates) == 3


@pytest.mark.parametrize("first,second", [
    ("Café?", "Cafe\u0301?"),
    ("Åre plans?", "A\u030are plans?"),
    ("가", "\u1100\u1161"),
    ("CAFÉ  plans?", "cafe\u0301 plans?"),
])
def test_canonically_equivalent_unicode_candidates_are_duplicates(first, second):
    with pytest.raises(ValidationError, match="distinct"):
        ReplyResponse.model_validate(response([first, second, "Another suggestion"]))


def test_unicode_normalization_preserves_different_accents():
    answer = ReplyResponse.model_validate(response(["resume", "résumé", "Another suggestion"]))
    assert len(answer.candidates) == 3
