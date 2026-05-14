"""Shared pytest helpers for running Pied as a command-line program."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[1]
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pied  # noqa: E402


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the directory containing small files used by file-input tests."""
    return FIXTURES_DIR


@pytest.fixture
def run_pied(monkeypatch):
    """Run pied.main() with isolated argv and stdin for each test call."""

    def _run(argv: list[str], stdin: str = "") -> None:
        monkeypatch.setattr(sys, "argv", ["pied.py", *argv])
        monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
        pied.main()

    return _run
