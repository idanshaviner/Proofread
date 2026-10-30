"""Keep the distributable mock preview separate from development/auth tooling."""
from pathlib import Path

from packaging.requirements import Requirement


BACKEND = Path(__file__).resolve().parents[1]


def requirements(path):
    result = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-r "):
            result.update(requirements(path.parent / line[3:].strip()))
        else:
            requirement = Requirement(line)
            result[requirement.name.lower().replace("_", "-")] = requirement
    return result


def test_preview_runtime_manifest_has_no_test_or_auth_dependencies():
    runtime = requirements(BACKEND / "requirements-runtime.txt")
    assert set(runtime) == {"fastapi", "uvicorn", "pydantic", "httpx", "packaging"}
    assert all(requirement.specifier for requirement in runtime.values())


def test_full_development_manifest_includes_runtime_and_preserves_auth_and_tests():
    manifest = (BACKEND / "requirements.txt").read_text().splitlines()
    assert "-r requirements-runtime.txt" in manifest
    full = requirements(BACKEND / "requirements.txt")
    assert {"fastapi", "uvicorn", "pydantic", "httpx", "packaging", "pytest", "pytest-asyncio", "pyjwt", "cryptography"} <= full.keys()
    assert full["pyjwt"].extras == {"crypto"}
    assert "2.15.0" not in full["pyjwt"].specifier
    assert "50.0.1" not in full["cryptography"].specifier
