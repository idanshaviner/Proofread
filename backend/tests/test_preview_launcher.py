"""Exercise the real launcher offline with fake interpreters and throwaway trees."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


LAUNCHER = Path(__file__).resolve().parents[2] / "tools/preview/start.command"
FAKE_PYTHON = r'''#!__EXECUTABLE__
import json, os, pathlib, sys
minor = __MINOR__
tag = __TAG__
args = sys.argv[1:]
with open(os.environ["FAKE_EVENTS"], "a") as log:
    log.write(json.dumps({"tag": tag, "args": args}) + "\n")
root = pathlib.Path(sys.argv[0]).resolve().parents[1]
if args[:1] == ["-c"]:
    raise SystemExit(0 if 11 <= minor <= 13 else 1)
if args[:2] == ["-m", "venv"]:
    destination = pathlib.Path(args[2])
    (destination / "bin").mkdir(parents=True)
    target = destination / "bin/python"
    target.write_text(pathlib.Path(sys.argv[0]).read_text())
    target.chmod(0o755)
    (destination / "pip-ready").touch()
    raise SystemExit(0)
if args[:3] == ["-m", "pip", "--version"]:
    raise SystemExit(0 if (root / "pip-ready").exists() else 1)
if args[:3] == ["-m", "ensurepip", "--upgrade"]:
    (root / "pip-ready").touch()
    raise SystemExit(0)
if args[:3] == ["-m", "pip", "check"]:
    raise SystemExit(0 if (root / "deps-ready").exists() else 1)
if args[:3] == ["-m", "pip", "install"]:
    if os.environ.get("FAKE_INSTALL_FAIL"):
        raise SystemExit(9)
    (root / "deps-ready").touch()
    raise SystemExit(0)
if args == ["-"]:
    sys.stdin.read()
    raise SystemExit(0 if (root / "deps-ready").exists() else 1)
if args == ["tools/preview/server.py"]:
    raise SystemExit(0 if (root / "deps-ready").exists() else 7)
raise SystemExit(98)
'''


@pytest.fixture
def preview(tmp_path):
    root = tmp_path / "checkout with spaces"
    (root / "tools/preview").mkdir(parents=True)
    (root / "backend").mkdir()
    shutil.copyfile(LAUNCHER, root / "tools/preview/start.command")
    (root / "backend/requirements.txt").write_text("fastapi>=0.115,<1\n")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    events = tmp_path / "events.jsonl"
    env = {
        "PATH": f"{fake_bin}:/usr/bin:/bin",
        "FAKE_EVENTS": str(events),
    }

    def interpreter(path, minor, tag=None):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(FAKE_PYTHON.replace("__EXECUTABLE__", sys.executable)
                        .replace("__MINOR__", str(minor)).replace("__TAG__", repr(tag or path.name)))
        path.chmod(0o755)
        return path

    # Shadow every executable candidate so tests cannot accidentally create a
    # real environment or invoke pip/network when interpreter selection changes.
    for name in ("python3", "python3.11", "python3.12", "python3.13"):
        interpreter(fake_bin / name, 15)

    def run(**overrides):
        result = subprocess.run(
            ["bash", str(root / "tools/preview/start.command")], cwd=tmp_path,
            env={**env, **overrides}, capture_output=True, text=True, timeout=10,
        )
        calls = [json.loads(line) for line in events.read_text().splitlines()] if events.exists() else []
        return result, calls

    return root, fake_bin, interpreter, run


def test_selects_supported_version_when_default_python_is_unsupported(preview):
    root, fake_bin, interpreter, run = preview
    interpreter(fake_bin / "python3.12", 12)
    result, calls = run()
    assert result.returncode == 0, result.stderr
    assert any(call["tag"] == "python3.12" and call["args"][:2] == ["-m", "venv"] for call in calls)
    assert (root / "backend/.venv/deps-ready").exists()


def test_explicit_interpreter_and_alternative_env_preserve_old_environment(preview, tmp_path):
    root, _, interpreter, run = preview
    old_env = root / "backend/.venv"
    interpreter(old_env / "bin/python", 15, "old")
    marker = old_env / "keep-user-state"
    marker.write_text("preserve")
    selected = interpreter(tmp_path / "Framework Python/bin/python3", 13, "explicit")
    new_env = root / "backend/.venv-supported"
    result, calls = run(PROOFREAD_PYTHON=str(selected), PROOFREAD_VENV=str(new_env))
    assert result.returncode == 0, result.stderr
    assert marker.read_text() == "preserve"
    assert any(call["tag"] == "explicit" and call["args"][:2] == ["-m", "venv"] for call in calls)
    assert not any(call["tag"] == "old" for call in calls)


def test_existing_supported_environment_repairs_missing_dependencies(preview):
    root, _, interpreter, run = preview
    environment = root / "backend/.venv"
    interpreter(environment / "bin/python", 12, "existing")
    result, calls = run()
    assert result.returncode == 0, result.stderr
    assert any(call["args"][:3] == ["-m", "ensurepip", "--upgrade"] for call in calls)
    assert any(call["args"][:3] == ["-m", "pip", "install"] for call in calls)
    assert not any(call["args"][:2] == ["-m", "venv"] for call in calls)


def test_healthy_existing_environment_starts_without_installing(preview):
    root, _, interpreter, run = preview
    environment = root / "backend/.venv"
    interpreter(environment / "bin/python", 11, "existing")
    (environment / "pip-ready").touch()
    (environment / "deps-ready").touch()
    result, calls = run()
    assert result.returncode == 0, result.stderr
    assert not any(call["args"][:3] == ["-m", "pip", "install"] for call in calls)
    assert calls[-1]["args"] == ["tools/preview/server.py"]


@pytest.mark.parametrize("existing", [False, True])
def test_unsupported_interpreter_fails_clearly_without_mutation(preview, existing):
    root, fake_bin, interpreter, run = preview
    environment = root / "backend/.venv"
    if existing:
        selected = interpreter(environment / "bin/python", 15, "unsupported")
    else:
        selected = fake_bin / "python3"
    result, calls = run(**({} if existing else {"PROOFREAD_PYTHON": str(selected)}))
    assert result.returncode != 0
    assert "3.11" in result.stderr and "3.13" in result.stderr
    assert "PROOFREAD_PYTHON" in result.stderr
    if existing:
        assert "PROOFREAD_VENV" in result.stderr
        assert selected.exists()
    assert not any(call["args"][:2] == ["-m", "venv"] for call in calls)
    assert not any(call["args"] == ["tools/preview/server.py"] for call in calls)


def test_failed_dependency_install_never_starts_server_and_next_run_recovers(preview):
    root, fake_bin, interpreter, run = preview
    interpreter(fake_bin / "python3.13", 13)
    failed, calls = run(FAKE_INSTALL_FAIL="1")
    assert failed.returncode != 0
    assert not any(call["args"] == ["tools/preview/server.py"] for call in calls)
    recovered, _ = run()
    assert recovered.returncode == 0, recovered.stderr
    assert (root / "backend/.venv/deps-ready").exists()
