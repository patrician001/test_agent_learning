import re

import pytest

import repostats
from repostats import extension_report

HEADER = "| Extension | Files |\n| --- | --- |"


def cells(line):
    """Split a table row on pipes not preceded by a backslash."""

    return re.split(r"(?<!\\)\|", line)


def write_or_skip(path, text=""):
    try:
        path.write_text(text)
    except OSError:
        pytest.skip("filesystem rejects this file name")


def test_exact_table(sample_repo):
    assert extension_report(sample_repo) == f"{HEADER}\n| .md | 2 |\n| .py | 2 |\n| (none) | 1 |"


def test_ordering_by_count(sample_repo):
    (sample_repo / "src" / "extra.py").write_text("")
    lines = extension_report(sample_repo).splitlines()
    assert lines[2:] == ["| .py | 3 |", "| .md | 2 |", "| (none) | 1 |"]


def test_empty_directory(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    assert extension_report(empty) == HEADER


def test_exported():
    assert "extension_report" in repostats.__all__


def test_pipe_in_extension(sample_repo):
    write_or_skip(sample_repo / "example.a|b")
    out = extension_report(sample_repo)
    assert "| .a&#124;b | 1 |" in out.splitlines()
    assert all(len(cells(line)) == 4 for line in out.splitlines())


@pytest.mark.parametrize("sep", ["\n", "\r"])
def test_line_break_in_extension(sample_repo, sep):
    write_or_skip(sample_repo / f"x.a{sep}b")
    out = extension_report(sample_repo)
    assert "| .a<br>b | 1 |" in out.splitlines()
    assert len(out.splitlines()) == 2 + 4
    assert all(len(cells(line)) == 4 for line in out.splitlines())


def test_backslash_before_pipe(sample_repo):
    write_or_skip(sample_repo / "x.a\\|b")
    out = extension_report(sample_repo)
    assert "| .a\\\\&#124;b | 1 |" in out.splitlines()


def test_plain_rows_unchanged(sample_repo):
    write_or_skip(sample_repo / "x.a|b")
    lines = extension_report(sample_repo).splitlines()
    assert "| .py | 2 |" in lines
    assert "| (none) | 1 |" in lines
