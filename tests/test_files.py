from pathlib import Path

import pytest

from repostats import count_by_extension, find_todos, list_files


def test_list_files_skips_git(sample_repo):
    assert list_files(sample_repo) == [
        "Makefile",
        "README.md",
        "docs/guide.md",
        "src/app.py",
        "src/util.py",
    ]


def test_count_by_extension(sample_repo):
    assert count_by_extension(sample_repo) == {"": 1, ".md": 2, ".py": 2}


def test_find_todos_sample_repo(sample_repo):
    assert find_todos(sample_repo) == [("src/app.py", 2, "# TODO: handle errors")]


def test_find_todos_order_and_content(todo_repo):
    assert find_todos(todo_repo) == [
        ("docs/crlf.txt", 2, "TODO: b"),
        ("docs/crlf.txt", 3, "TODO: c"),
        ("docs/ff.txt", 1, "header\x0cTODO: fix"),
        ("docs/ff.txt", 2, "second TODO"),
        ("docs/indented.md", 1, "TODO: indented"),
        ("docs/notes.md", 1, "TODO one"),
        ("docs/notes.md", 3, "TODO two"),
        ("src/app.py", 2, "# TODO: handle errors"),
    ]


def test_find_todos_form_feed_is_not_a_line_break(todo_repo):
    result = find_todos(todo_repo)
    assert ("docs/ff.txt", 1, "header\x0cTODO: fix") in result
    assert ("docs/ff.txt", 2, "second TODO") in result


def test_find_todos_universal_newlines(todo_repo):
    result = find_todos(todo_repo)
    assert ("docs/crlf.txt", 2, "TODO: b") in result
    assert ("docs/crlf.txt", 3, "TODO: c") in result


def test_find_todos_propagates_oserror(sample_repo, monkeypatch):
    def fail(self, *args, **kwargs):
        raise PermissionError(str(self))

    monkeypatch.setattr(Path, "read_text", fail)
    with pytest.raises(PermissionError):
        find_todos(sample_repo)
