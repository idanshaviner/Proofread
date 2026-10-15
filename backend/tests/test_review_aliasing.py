import copy

import pytest

from app.provider import MockProvider
from evaluation.runner import blind_comparison, evaluate, verify_report


@pytest.mark.asyncio
async def test_editing_review_and_key_does_not_corrupt_source_reports():
    left = await evaluate(MockProvider(), system_name="left")
    right = await evaluate(MockProvider(), system_name="right")
    original = copy.deepcopy(left)
    review, key = blind_comparison(left, right)
    left_option = next(label for label in ("A", "B") if key["cases"][0][label] == "left")
    review["cases"][0]["options"][left_option][0]["text"] = "edited"
    key["systems"]["left"]["name"] = "edited"
    assert left == original
    assert verify_report(left) == original


@pytest.mark.asyncio
async def test_source_edits_do_not_change_prepared_review_or_key():
    left = await evaluate(MockProvider())
    right = await evaluate(MockProvider())
    review, key = blind_comparison(left, right)
    original = copy.deepcopy((review, key))
    left["records"][0]["response"]["candidates"][0]["text"] = "edited"
    left["system"]["name"] = "edited"
    assert (review, key) == original
