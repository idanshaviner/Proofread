"""Completed ratings are synthetic; no inference or private text is used."""
import asyncio
import copy
import importlib

import pytest

from app.provider import MockProvider, ProviderFailure
from evaluation.runner import blind_comparison, evaluate


@pytest.fixture
def comparison():
    left = asyncio.run(evaluate(MockProvider(), "synthetic-left"))
    right = asyncio.run(evaluate(MockProvider(), "synthetic-right"))
    review, key = blind_comparison(left, right, seed=42)
    # Match separately loaded JSON artifacts, without generation-time aliases.
    return left, right, copy.deepcopy(review), copy.deepcopy(key)


def summarize(*args, **kwargs):
    return importlib.import_module("evaluation.reviews").summarize_review(*args, **kwargs)


def test_unrated_template_keeps_missing_separate_and_does_not_unblind(comparison):
    left, right, review, key = comparison
    summary = summarize(review, left, right, seed=42)
    assert summary["status"] == "unrated"
    assert summary["included_cases"] == 4 and summary["excluded_cases"] == 0
    assert all(counts == {"A": 0, "B": 0, "tie": 0, "missing": 4}
               for counts in summary["dimensions"].values())
    assert "system_preferences" not in summary and "systems" not in summary
    assert summary["authenticity_superiority"] == "not_established"


def test_partial_ratings_count_votes_and_validated_underlying_systems(comparison):
    left, right, review, key = comparison
    votes = [("A", "B", "tie"), ("B", None, "A"), ("tie", "A", None), (None, "tie", "B")]
    for case, ratings in zip(review["cases"], votes):
        case["preferences"] = dict(zip(("authenticity", "helpfulness", "intent_preservation"), ratings))
        case["notes"] = "Invented reviewer note."
    summary = summarize(review, left, right, seed=42, key=key)
    assert summary["status"] == "partially_rated"
    assert all(counts == {"A": 1, "B": 1, "tie": 1, "missing": 1}
               for counts in summary["dimensions"].values())
    assert summary["system_preferences"]["helpfulness"] == {"left": 2, "right": 0, "tie": 1, "missing": 1}
    assert summary["systems"] == {"left": left["system"], "right": right["system"]}
    assert summary["reports"] == {"left": left["report_sha256"], "right": right["report_sha256"]}
    assert "Invented reviewer note" not in str(summary)


def test_complete_ratings_status_does_not_imply_quality_or_superiority(comparison):
    left, right, review, key = comparison
    for case in review["cases"]:
        case["preferences"] = {dimension: "tie" for dimension in case["preferences"]}
    summary = summarize(review, left, right, seed=42)
    assert summary["status"] == "complete"
    assert all(counts == {"A": 0, "B": 0, "tie": 4, "missing": 0}
               for counts in summary["dimensions"].values())
    assert summary["authenticity_superiority"] == "not_established"


@pytest.mark.parametrize("rating", ["left", "Tie", "", True, 1, [], {}])
def test_invalid_ratings_are_rejected(comparison, rating):
    left, right, review, key = comparison
    review["cases"][0]["preferences"]["authenticity"] = rating
    with pytest.raises(ValueError):
        summarize(review, left, right, seed=42)


@pytest.mark.parametrize("field,value", [
    ("id", "unknown-case"),
    ("request", {"mode": "rewrite"}),
    ("options", {}),
    ("style_examples", ["edited example"]),
    ("review_guidance", "edited rubric"),
    ("notes", None),
    ("preferences", {"authenticity": "A"}),
])
def test_immutable_review_content_and_shape_cannot_change(comparison, field, value):
    left, right, review, key = comparison
    review["cases"][0][field] = value
    with pytest.raises(ValueError):
        summarize(review, left, right, seed=42)


@pytest.mark.parametrize("change", ["dataset", "duplicate", "missing", "reordered", "extra"])
def test_review_dataset_and_case_coverage_are_exact(comparison, change):
    left, right, review, key = comparison
    if change == "dataset":
        review["dataset_sha256"] = "other-dataset"
    elif change == "duplicate":
        review["cases"][1] = copy.deepcopy(review["cases"][0])
    elif change == "missing":
        review["cases"].pop()
    elif change == "reordered":
        review["cases"].reverse()
    else:
        review["unexpected"] = True
    with pytest.raises(ValueError):
        summarize(review, left, right, seed=42)


@pytest.mark.parametrize("change", ["seed", "mapping", "reports", "systems", "excluded", "malformed"])
def test_unblinding_key_must_match_exact_original_reports_and_seed(comparison, change):
    left, right, review, key = comparison
    if change == "seed":
        key["seed"] = 0
    elif change == "mapping":
        entry = key["cases"][0]
        entry["A"], entry["B"] = entry["B"], entry["A"]
    elif change == "reports":
        key["reports"]["left"] = "other-report"
    elif change == "systems":
        key["systems"]["left"]["name"] = "other-system"
    elif change == "excluded":
        key["cases"][0] = {"case_id": key["cases"][0]["case_id"], "excluded": "fabricated"}
    else:
        key = []
    with pytest.raises(ValueError):
        summarize(review, left, right, seed=42, key=key)


def test_empty_review_from_provider_failures_is_not_positive_success():
    class FailingProvider:
        async def generate(self, request):
            raise ProviderFailure("synthetic failure")
    failed = asyncio.run(evaluate(FailingProvider(), "synthetic-failure"))
    review, key = blind_comparison(failed, failed, seed=42)
    summary = summarize(review, failed, failed, seed=42, key=key)
    assert summary["status"] == "no_comparable_cases"
    assert summary["included_cases"] == 0 and summary["excluded_cases"] == 4
    assert all(counts == {"A": 0, "B": 0, "tie": 0, "missing": 0}
               for counts in summary["dimensions"].values())


@pytest.mark.parametrize("review", [None, [], {}, {"dataset_sha256": "x", "cases": [None]}])
def test_malformed_reviews_raise_value_error(comparison, review):
    left, right, _, _ = comparison
    with pytest.raises(ValueError):
        summarize(review, left, right, seed=42)


def test_candidate_text_edit_is_rejected(comparison):
    left, right, review, key = comparison
    review["cases"][0]["options"]["A"][0]["text"] = "An edited invented candidate."
    with pytest.raises(ValueError, match="immutable"):
        summarize(review, left, right, seed=42)


def test_mixed_failed_cases_are_excluded_instead_of_missing_votes():
    class RewriteFailingProvider:
        async def generate(self, request):
            if request.mode == "rewrite":
                raise ProviderFailure("synthetic failure")
            return await MockProvider().generate(request)
    left = asyncio.run(evaluate(RewriteFailingProvider(), "synthetic-partial"))
    right = asyncio.run(evaluate(MockProvider(), "synthetic-other"))
    review, key = blind_comparison(left, right, seed=42)
    summary = summarize(review, left, right, seed=42, key=key)
    assert summary["included_cases"] == 2 and summary["excluded_cases"] == 2
    assert all(counts["missing"] == 2 for counts in summary["dimensions"].values())


def test_summary_does_not_mutate_review_or_key(comparison):
    left, right, review, key = comparison
    original = copy.deepcopy((left, right, review, key))
    summarize(review, left, right, seed=42, key=key)
    assert (left, right, review, key) == original


def test_modified_source_report_is_rejected(comparison):
    left, right, review, key = comparison
    left["records"][0]["response"]["candidates"][0]["text"] = "Changed report content."
    with pytest.raises(ValueError):
        summarize(review, left, right, seed=42)
