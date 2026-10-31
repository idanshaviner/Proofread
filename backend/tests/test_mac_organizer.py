"""Explicit archival, never deletion or modification of the working app."""
import importlib.util
from pathlib import Path
import json
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('mac_organizer', ROOT / 'tools/organize-mac-workspace/organize.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture(tmp_path):
    docs = tmp_path / 'Documents'
    active = docs / 'Proofread-Capture-Study'
    project = active / 'ios/CaptureStudy/ProofreadCaptureStudy.xcodeproj'
    project.mkdir(parents=True)
    (project / 'project.pbxproj').write_text('user team and signing')
    (active / 'source.swift').write_text('working source')
    helper = docs / 'Proofread-Organizer'
    update = helper / 'notes-test'
    update.mkdir(parents=True)
    (update / 'apply.command').write_text('do not execute during cleanup')
    (update / 'manifest.json').write_text('[]')
    return docs, active, helper


def test_archives_known_artifacts_preserves_active_project_and_unrelated_items(tmp_path):
    docs, active, helper = fixture(tmp_path)
    (docs / 'Proofread-preview').mkdir()
    (docs / 'Proofread-preview/example.txt').write_text('old demo')
    (docs / 'Proofread-Notes-Test.zip').write_bytes(b'old zip')
    (docs / 'Proofread personal notes.txt').write_text('unrelated')
    (docs / 'GitHub').mkdir()
    (active / 'START-HERE.txt').write_text('old instructions')
    project, archive = module.organize(docs, helper)
    assert project == active
    assert (archive / 'old-downloads/Proofread-preview/example.txt').read_text() == 'old demo'
    assert (archive / 'old-downloads/Proofread-Notes-Test.zip').read_bytes() == b'old zip'
    assert (archive / 'previous-START-HERE.txt').read_text() == 'old instructions'
    assert (archive / 'organizer-used/notes-test/apply.command').is_file()
    assert (active / 'tools/notes-test/apply.command').is_file()
    assert (active / 'source.swift').read_text() == 'working source'
    assert (active / 'ios/CaptureStudy/ProofreadCaptureStudy.xcodeproj/project.pbxproj').read_text() == 'user team and signing'
    assert (docs / 'Proofread personal notes.txt').read_text() == 'unrelated'
    assert (docs / 'GitHub').is_dir()
    assert json.loads((archive / 'MOVED.json').read_text())


def test_refuses_symlink_before_any_move(tmp_path):
    docs, active, helper = fixture(tmp_path)
    (docs / 'Proofread-preview.zip').write_text('leave alone')
    (docs / 'Proofread-preview').symlink_to(active, target_is_directory=True)
    with pytest.raises(ValueError, match='symbolic link'):
        module.organize(docs, helper)
    assert not (docs / 'Proofread Archive').exists()
    assert helper.is_dir()
    assert (docs / 'Proofread-preview.zip').read_text() == 'leave alone'
