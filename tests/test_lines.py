import pytest

from repostats import count_lines


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
