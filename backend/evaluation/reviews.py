"""Validate invented-case human ratings and report counts without quality claims."""

from .runner import blind_comparison, fingerprint

DIMENSIONS = ("authenticity", "helpfulness", "intent_preservation")


def _digest(value):
    try:
        return fingerprint(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Review material must contain valid JSON values") from exc


def summarize_review(review, left, right, *, seed=0, key=None):
    """Validate against regenerated material; count A/B/tie/null preferences.

    Only preferences and string notes may change from the generated review.
    Original reports are verified by blind_comparison. Supplying its exact key
    additionally enables left/right counts. No key means blinded-only results.
    Digests detect changes and support reproducibility; they are not signatures
    or proof of reviewer identity. No notes or candidate text enter the summary.
    """
    if type(seed) is not int:
        raise ValueError("Review seed must be an integer")
    expected_review, expected_key = blind_comparison(left, right, seed)
    if not isinstance(review, dict) or set(review) != set(expected_review):
        raise ValueError("Review must match the generated review shape")
    cases = review.get("cases")
    if not isinstance(cases, list) or len(cases) != len(expected_review["cases"]):
        raise ValueError("Review must include exactly the comparable cases")
    normalized_cases = []
    for case, expected in zip(cases, expected_review["cases"]):
        if not isinstance(case, dict) or set(case) != set(expected):
            raise ValueError("Review case must match the generated case shape")
        preferences = case["preferences"]
        if not isinstance(preferences, dict) or set(preferences) != set(DIMENSIONS):
            raise ValueError("Every review requires all three preference dimensions")
        if any(value is not None and (type(value) is not str or value not in ("A", "B", "tie"))
               for value in preferences.values()):
            raise ValueError("Preferences must be A, B, tie or null")
        if not isinstance(case["notes"], str):
            raise ValueError("Review notes must be text")
        normalized_cases.append({**case, "preferences": dict.fromkeys(DIMENSIONS), "notes": ""})
    normalized = {**review, "cases": normalized_cases}
    if _digest(normalized) != _digest(expected_review):
        raise ValueError("Review dataset, cases, options or other immutable material was changed")
    if key is not None and (not isinstance(key, dict) or _digest(key) != _digest(expected_key)):
        raise ValueError("Unblinding key does not match the original reports and seed")

    dimensions = {dimension: {"A": 0, "B": 0, "tie": 0, "missing": 0} for dimension in DIMENSIONS}
    system_preferences = {dimension: {"left": 0, "right": 0, "tie": 0, "missing": 0}
                          for dimension in DIMENSIONS}
    mappings = {entry["case_id"]: entry for entry in expected_key["cases"] if "excluded" not in entry}
    for case in cases:
        for dimension, vote in case["preferences"].items():
            label = "missing" if vote is None else vote
            dimensions[dimension][label] += 1
            if key is not None:
                side = mappings[case["id"]][vote] if vote in ("A", "B") else label
                system_preferences[dimension][side] += 1
    missing = sum(counts["missing"] for counts in dimensions.values())
    if not cases:
        status = "no_comparable_cases"
    elif missing == len(cases) * len(DIMENSIONS):
        status = "unrated"
    elif missing:
        status = "partially_rated"
    else:
        status = "complete"
    summary = {
        "schema_version": 1, "status": status,
        "dataset_sha256": expected_review["dataset_sha256"],
        "reports": expected_key["reports"], "review_sha256": _digest(review), "seed": seed,
        "included_cases": len(cases), "excluded_cases": len(left["records"]) - len(cases),
        "dimensions": dimensions, "authenticity_superiority": "not_established",
    }
    if key is not None:
        summary.update(system_preferences=system_preferences, systems=expected_key["systems"])
    return summary
