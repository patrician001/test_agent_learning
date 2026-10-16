import json
import subprocess
import sys
from pathlib import Path

import pytest

from repostats.cli import main

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_lists_files(sample_repo, capsys):
    assert main([str(sample_repo)]) == 0
    out = capsys.readouterr().out
    assert out.splitlines() == [
        "Makefile",
        "README.md",
        "docs/guide.md",
        "src/app.py",
        "src/util.py",
    ]


def test_counts(sample_repo, capsys):
    assert main(["--counts", str(sample_repo)]) == 0
    assert json.loads(capsys.readouterr().out) == {"": 1, ".md": 2, ".py": 2}


@pytest.mark.parametrize("name", ["missing", "Makefile"])
def test_not_a_directory(sample_repo, capsys, name):
    target = sample_repo / name
    assert main([str(target)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert str(target) in captured.err


def test_missing_root_is_usage_error():
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_module_invocation(sample_repo):
    ok = subprocess.run(
        [sys.executable, "-m", "repostats", "--counts", str(sample_repo)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert ok.returncode == 0
    assert json.loads(ok.stdout) == {"": 1, ".md": 2, ".py": 2}
    bad = subprocess.run(
        [sys.executable, "-m", "repostats", str(sample_repo / "missing")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert bad.returncode == 2
    assert bad.stdout == ""
