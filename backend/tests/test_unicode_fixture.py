"""Python and the actual Swift client must reject the same duplicate fixture."""
import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.provider import ReplyResponse


def test_canonical_unicode_fixture_is_not_three_distinct_replies():
    path = Path(__file__).resolve().parents[2] / 'ios/Tests/ProofreadNetworkingTests/Fixtures/unicode-duplicate.json'
    with pytest.raises(ValidationError, match='distinct'):
        ReplyResponse.model_validate(json.loads(path.read_text()))
