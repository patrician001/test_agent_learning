"""Counting the lines in a text file."""

from pathlib import Path


def count_lines(path: str | Path) -> int:
    """Return the number of lines in the text file at path.

    CR, LF and CRLF each end a line. A last line without a terminator still counts,
    and an empty file has 0 lines.

    >>> import tempfile
    >>> root = Path(tempfile.mkdtemp())
    >>> _ = (root / "a.txt").write_bytes(b"a\\nb")
    >>> count_lines(root / "a.txt")
    2
    >>> _ = (root / "b.txt").write_bytes(b"a\\rb")
    >>> count_lines(root / "b.txt")
    2
    >>> _ = (root / "c.txt").write_bytes(b"")
    >>> count_lines(root / "c.txt")
    0
    """
    with open(path, encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)
