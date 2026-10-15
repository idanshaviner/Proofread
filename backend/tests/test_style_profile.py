import pytest
from app.style_profile import extract_style_profile

def test_empty_input():
    result = extract_style_profile([])
    assert result.example_count == 0
    assert result.common_markers == []

def test_synthetic_style_signals():
    result = extract_style_profile(["haha you free? 😄", "lol yeah!", "Sounds good."])
    assert result.example_count == 3
    assert result.lowercase_start_ratio == pytest.approx(0.667, abs=0.001)
    assert result.emoji_message_ratio == pytest.approx(0.333, abs=0.001)
    assert result.question_message_ratio == pytest.approx(0.333, abs=0.001)
    assert result.common_markers == ["haha", "lol"]

def test_rejects_blank_example():
    with pytest.raises(ValueError):
        extract_style_profile(["hello", "   "])

def test_rejects_large_batch():
    with pytest.raises(ValueError):
        extract_style_profile(["hi"] * 501)

def test_no_raw_messages_in_output():
    text = "private secret phrase"
    result = extract_style_profile([text])
    assert text not in result.model_dump_json()
