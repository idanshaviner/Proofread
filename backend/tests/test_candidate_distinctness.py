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
