import subprocess
import sys
from pathlib import Path

import pytest

from repostats.__main__ import main

REPO = Path(__file__).resolve().parent.parent


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "repostats", *args], cwd=REPO, capture_output=True, text=True
    )


def test_sample_repo_cli(sample_repo):
    result = run_cli(str(sample_repo))
    assert result.returncode == 0
    assert result.stdout.splitlines() == [" 1 2", ".md 2 4", ".py 2 4"]
    assert result.stderr == ""


def test_sample_repo_main(sample_repo, capsys):
    assert main([str(sample_repo)]) == 0
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [" 1 2", ".md 2 4", ".py 2 4"]
    assert captured.err == ""


def test_sorted_by_extension(sample_repo, capsys):
    for name in ["z.txt", "a.gz", "archive.tar.gz"]:
        (sample_repo / name).write_bytes(b"x\n")
    assert main([str(sample_repo)]) == 0
    exts = [line.split(" ")[0] for line in capsys.readouterr().out.splitlines()]
    assert exts == sorted(exts)
    assert exts == ["", ".gz", ".md", ".py", ".txt"]
    assert main([str(sample_repo)]) == 0
    assert ".gz 2 2" in capsys.readouterr().out.splitlines()


LINE_CASES = [
    (b"a\rb\r", 2),
    (b"a\rb", 2),
    (b"a\r\nb\r\n", 2),
    (b"a\r\nb", 2),
    (b"a\rb\nc\r\nd", 4),
    (b"a\rb\nc\r\nd\r", 4),
    (b"a" * 8191 + b"\r\n" + b"b", 2),
    (b"a" * 8191 + b"\r\n", 1),
]


@pytest.mark.parametrize(("data", "expected"), LINE_CASES)
def test_line_endings(sample_repo, data, expected):
    sub = sample_repo / "case"
    sub.mkdir()
    (sub / "f.dat").write_bytes(data)
    result = run_cli(str(sub))
    assert result.returncode == 0
    assert result.stdout == f".dat 1 {expected}\n"


def test_no_argument(capsys):
    assert main([]) == 2
    captured = capsys.readouterr()
    assert "usage" in captured.err
    assert captured.out == ""
    result = run_cli()
    assert result.returncode == 2
    assert "usage" in result.stderr
    assert result.stdout == ""


def test_two_arguments(sample_repo, capsys):
    assert main([str(sample_repo), str(sample_repo)]) == 2
    assert "usage" in capsys.readouterr().err


def test_empty_directory(sample_repo, capsys):
    empty = sample_repo / "empty"
    empty.mkdir()
    assert main([str(empty)]) == 0
    assert capsys.readouterr().out == ""
