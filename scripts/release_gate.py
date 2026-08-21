"""Build and smoke-test the exact artifacts intended for release."""

import json
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_DIRECTORY = PROJECT_ROOT / "dist"
RELEASE_ENVIRONMENT = PROJECT_ROOT / ".release-venv"


def run(*command: str) -> None:
    print(f"$ {subprocess.list2cmdline(command)}", flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def clean_generated_directory(path: Path) -> None:
    if path.resolve().parent != PROJECT_ROOT:
        raise RuntimeError(f"refusing to clean path outside the project: {path}")
    if path.exists():
        shutil.rmtree(path)


def main() -> None:
    run(sys.executable, "-m", "ruff", "check", ".")
    run(sys.executable, "-m", "ruff", "format", "--check", ".")
    run(sys.executable, "-m", "mypy", "src")
    run(
        sys.executable,
        "-m",
        "pytest",
        "--cov=recall_match",
        "--cov-report=term-missing",
        "--cov-fail-under=90",
    )

    clean_generated_directory(DIST_DIRECTORY)
    run(sys.executable, "-m", "build")
    wheels = list(DIST_DIRECTORY.glob("*.whl"))
    source_distributions = list(DIST_DIRECTORY.glob("*.tar.gz"))
    if len(wheels) != 1 or len(source_distributions) != 1:
        raise RuntimeError("build must produce exactly one wheel and one source distribution")

    clean_generated_directory(RELEASE_ENVIRONMENT)
    venv.EnvBuilder(with_pip=True).create(RELEASE_ENVIRONMENT)
    binary_directory = RELEASE_ENVIRONMENT / ("Scripts" if os.name == "nt" else "bin")
    environment_python = binary_directory / ("python.exe" if os.name == "nt" else "python")
    installed_command = binary_directory / (
        "recall-match.exe" if os.name == "nt" else "recall-match"
    )
    run(
        str(environment_python),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-deps",
        str(wheels[0]),
    )
    run(str(installed_command), "--version")

    smoke_directory = RELEASE_ENVIRONMENT / "smoke"
    smoke_directory.mkdir()
    smoke_json = smoke_directory / "report.json"
    run(
        str(installed_command),
        "audit",
        str(PROJECT_ROOT / "examples" / "inventory.csv"),
        "--recalls",
        str(PROJECT_ROOT / "examples" / "cpsc-recalls.json"),
        "--json-out",
        str(smoke_json),
        "--markdown-out",
        str(smoke_directory / "report.md"),
        "--as-of",
        "2026-08-21",
        "--fail-on",
        "never",
    )
    summary = json.loads(smoke_json.read_text(encoding="utf-8"))["summary"]
    if summary != {
        "items_with_identifier_match": 1,
        "items_with_review_candidate": 1,
        "items_without_candidates": 1,
    }:
        raise RuntimeError(f"installed-wheel smoke result changed: {summary}")

    print(
        f"Release gate passed: {wheels[0].name}, {source_distributions[0].name}",
        flush=True,
    )


if __name__ == "__main__":
    main()
