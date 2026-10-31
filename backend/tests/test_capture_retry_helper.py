"""Reversible Mac cleanup behavior, tested without running Xcode or touching home."""
from pathlib import Path
import os
import shutil
import subprocess
import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('build_exit', [0, 9])
def test_retry_preserves_source_and_signing_and_propagates_build_failure(tmp_path, build_exit):
    project = tmp_path / 'project with spaces'
    study = project / 'ios/CaptureStudy'
    xcode = study / 'ProofreadCaptureStudy.xcodeproj'
    xcode.mkdir(parents=True)
    signing = xcode / 'project.pbxproj'
    signing.write_text('user signing settings')
    controller = project / 'ios/Proofread/Views/ScreenCaptureStudyController.swift'
    controller.parent.mkdir(parents=True)
    source = ROOT / 'ios/Proofread/Views/ScreenCaptureStudyController.swift'
    shutil.copyfile(source, controller)
    cache = study / '.build'
    cache.mkdir()
    (cache / 'old-cache').write_text('old generated state')
    helper = tmp_path / 'helper'
    helper.mkdir()
    shutil.copyfile(ROOT / 'tools/capture-study-retry/clean-and-open.command', helper / 'run')
    shutil.copyfile(source, helper / source.name)
    commands = tmp_path / 'commands'
    commands.mkdir()
    marker = tmp_path / 'opened'
    for name, body in {
        'uname': 'echo Darwin',
        'xcodebuild': f'echo synthetic build output; exit {build_exit}',
        'open': 'touch "$OPEN_MARKER"',
    }.items():
        script = commands / name
        script.write_text('#!/bin/sh\n' + body + '\n')
        script.chmod(0o755)
    result = subprocess.run(['bash', str(helper / 'run'), str(project)],
        env={**os.environ, 'PATH': str(commands) + ':' + os.environ['PATH'],
             'OPEN_MARKER': str(marker)}, capture_output=True, text=True)
    assert result.returncode == build_exit, result.stderr
    assert signing.read_text() == 'user signing settings'
    assert controller.read_bytes() == source.read_bytes()
    backup, = project.glob('.capture-retry-backup.*')
    assert (backup / 'generated-2/old-cache').read_text() == 'old generated state'
    assert (backup / source.name).read_bytes() == source.read_bytes()
    assert 'synthetic build output' in (backup / 'build.log').read_text()
    assert marker.exists() == (build_exit == 0)
