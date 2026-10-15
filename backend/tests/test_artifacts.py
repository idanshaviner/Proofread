"""Paired artifact failures must preserve user files and leave no owned partials."""
import json
import os
from pathlib import Path

import pytest

from evaluation.artifacts import write_review_pair


REVIEW = {"cases": [{"notes": "Invented lunch plan 🙂", "preference": None}]}
KEY = {"systems": {"A": "generic", "B": "synthetic-style"}}


def test_success_writes_both_complete_utf8_json_artifacts(tmp_path):
    review_path, key_path = tmp_path / "review.json", tmp_path / "key.json"
    assert write_review_pair(review_path, REVIEW, key_path, KEY) is None
    assert json.loads(review_path.read_text(encoding="utf-8")) == REVIEW
    assert json.loads(key_path.read_text(encoding="utf-8")) == KEY


@pytest.mark.parametrize("existing_name", ["review.json", "key.json"])
def test_existing_artifact_is_preserved_and_other_output_is_absent(tmp_path, existing_name):
    existing = tmp_path / existing_name
    existing.write_bytes(b"user artifact\x00")
    other = tmp_path / ("key.json" if existing_name == "review.json" else "review.json")
    with pytest.raises(FileExistsError):
        write_review_pair(tmp_path / "review.json", REVIEW, tmp_path / "key.json", KEY)
    assert existing.read_bytes() == b"user artifact\x00"
    assert not other.exists()


def test_missing_second_parent_cleans_first_output(tmp_path):
    review = tmp_path / "review.json"
    key = tmp_path / "missing-parent" / "key.json"
    with pytest.raises(FileNotFoundError):
        write_review_pair(review, REVIEW, key, KEY)
    assert not review.exists()
    assert not key.exists()


def test_same_resolved_destination_rejected_before_creation(tmp_path):
    alias = tmp_path / "alias"
    alias.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match="separate"):
        write_review_pair(tmp_path / "review.json", REVIEW, alias / "review.json", KEY)
    assert not (tmp_path / "review.json").exists()


def test_second_serialization_failure_creates_neither_artifact(tmp_path):
    with pytest.raises(TypeError):
        write_review_pair(tmp_path / "review.json", REVIEW, tmp_path / "key.json", {"bad": object()})
    assert list(tmp_path.iterdir()) == []


def test_second_write_failure_cleans_both_owned_artifacts(tmp_path, monkeypatch):
    from evaluation import artifacts
    real_fdopen = os.fdopen
    opened = 0

    class FailingWriter:
        def __init__(self, handle):
            self.handle = handle

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return self.handle.__exit__(*args)

        def __getattr__(self, name):
            return getattr(self.handle, name)

        def write(self, value):
            raise OSError("synthetic disk write failure")

    def fdopen(*args, **kwargs):
        nonlocal opened
        opened += 1
        handle = real_fdopen(*args, **kwargs)
        return FailingWriter(handle) if opened == 2 else handle

    monkeypatch.setattr(artifacts.os, "fdopen", fdopen)
    with pytest.raises(OSError, match="disk write failure"):
        write_review_pair(tmp_path / "review.json", REVIEW, tmp_path / "key.json", KEY)
    assert list(tmp_path.iterdir()) == []


def test_fsync_failure_cleans_both_owned_artifacts(tmp_path, monkeypatch):
    from evaluation import artifacts
    calls = 0

    def fsync(descriptor):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("synthetic durability failure")

    monkeypatch.setattr(artifacts.os, "fsync", fsync)
    with pytest.raises(OSError, match="durability failure"):
        write_review_pair(tmp_path / "review.json", REVIEW, tmp_path / "key.json", KEY)
    assert list(tmp_path.iterdir()) == []


def test_rollback_preserves_replacement_files(tmp_path, monkeypatch):
    from evaluation import artifacts
    review = tmp_path / "review.json"
    key = tmp_path / "key.json"
    replacement = tmp_path / "replacement.json"
    replacement.write_text("user replacement", encoding="utf-8")
    calls = 0

    def fsync(descriptor):
        nonlocal calls
        calls += 1
        if calls == 2:
            os.replace(replacement, review)
            raise OSError("synthetic failure after user replacement")

    monkeypatch.setattr(artifacts.os, "fsync", fsync)
    with pytest.raises(OSError, match="after user replacement"):
        write_review_pair(review, REVIEW, key, KEY)
    assert review.read_text(encoding="utf-8") == "user replacement"
    assert not key.exists()


def test_racing_second_creator_is_preserved(tmp_path, monkeypatch):
    from evaluation import artifacts
    review = tmp_path / "review.json"
    key = tmp_path / "key.json"
    real_open = os.open

    def racing_open(path, *args, **kwargs):
        if Path(path) == key:
            key.write_text("another writer", encoding="utf-8")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(artifacts.os, "open", racing_open)
    with pytest.raises(FileExistsError):
        write_review_pair(review, REVIEW, key, KEY)
    assert not review.exists()
    assert key.read_text(encoding="utf-8") == "another writer"
