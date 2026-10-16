import pytest

from repostats import count_by_extension, count_lines, lines_by_extension


def test_sample_files(sample_repo):
    assert count_lines(sample_repo / "README.md") == 3
    assert count_lines(sample_repo / "src" / "util.py") == 1
    assert count_lines(sample_repo / "Makefile") == 2


LONG = b"".join(b"x" * n + b"\r\n" for n in range(1, 400)) + b"end"

CASES = [
    (b"", 0),
    (b"a\nb", 2),
    (b"\n", 1),
    (b"a\nb\n", 2),
    (b"a\rb\r", 2),
    (b"a\rb", 2),
    (b"a\r\nb\r\n", 2),
    (b"a\r\nb", 2),
    (b"a\rb\nc\r\nd", 4),
    (b"a" * 8191 + b"\r\n" + b"b", 2),
    (LONG, 400),
    (b"\xff\n\xfe", 2),
]


@pytest.mark.parametrize(("data", "expected"), CASES)
def test_line_endings(sample_repo, data, expected):
    path = sample_repo / "extra.txt"
    path.write_bytes(data)
    assert count_lines(path) == expected


def test_lines_by_extension_sample(sample_repo):
    result = lines_by_extension(sample_repo)
    assert result == {"": 2, ".md": 4, ".py": 4}
    assert list(result) == list(count_by_extension(sample_repo))


def test_lines_by_extension_endings(sample_repo):
    files = {
        "cr.txt": b"a\rb\r",
        "cr2.txt": b"a\rb",
        "crlf.txt": b"a\r\nb\r\n",
        "crlf2.txt": b"a\r\nb",
        "mixed.txt": b"a\rb\nc\r\nd",
        "edge.txt": b"a" * 8191 + b"\r\n" + b"b",
        "empty.log": b"",
        "noext": b"1\n2\n3",
        "archive.tar.gz": b"z\n",
    }
    for name, data in files.items():
        (sample_repo / name).write_bytes(data)
    result = lines_by_extension(sample_repo)
    assert result[".txt"] == 2 + 2 + 2 + 2 + 4 + 2
    assert result[".log"] == 0
    assert result[""] == 2 + 3
    assert result[".gz"] == 1
    assert list(result) == list(count_by_extension(sample_repo))


def test_lines_by_extension_no_files(sample_repo):
    empty = sample_repo / "empty"
    empty.mkdir()
    assert lines_by_extension(empty) == {}
