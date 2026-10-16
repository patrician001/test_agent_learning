import json
import subprocess
import sys
from pathlib import Path

import pytest

from repostats.cli import main

REPO_ROOT = Path(__file__).resolve().parent.parent
LISTING = "Makefile\nREADME.md\ndocs/guide.md\nsrc/app.py\nsrc/util.py\n"


def test_lists_files(sample_repo, capsys):
    assert main([str(sample_repo)]) == 0
    assert capsys.readouterr().out == LISTING


def test_counts_as_json(sample_repo, capsys):
    assert main(["--counts", str(sample_repo)]) == 0
    assert json.loads(capsys.readouterr().out) == {"": 1, ".md": 2, ".py": 2}


@pytest.mark.parametrize("flags", [[], ["--counts"]])
@pytest.mark.parametrize("bad", ["missing", "README.md"])
def test_not_a_directory(sample_repo, capsys, flags, bad):
    assert main([*flags, str(sample_repo / bad)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "not a directory" in captured.err


def test_module_entry_point(sample_repo):
    run = [sys.executable, "-m", "repostats"]
    kwargs = {"cwd": REPO_ROOT, "capture_output": True, "text": True}
    ok = subprocess.run([*run, str(sample_repo)], **kwargs)
    assert ok.returncode == 0
    assert ok.stdout == LISTING
    bad = subprocess.run([*run, str(sample_repo / "missing")], **kwargs)
    assert bad.returncode == 2
    assert bad.stdout == ""
