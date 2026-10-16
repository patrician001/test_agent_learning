"""Counting the lines in text files."""

from pathlib import Path

from repostats.files import list_files


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


def lines_by_extension(root: str | Path) -> dict[str, int]:
    """Return the total lines of the files under root for each extension ("" for none), sorted by extension.

    Files are those list_files returns and lines are counted as count_lines does.

    >>> import tempfile
    >>> root = Path(tempfile.mkdtemp())
    >>> _ = (root / "a.py").write_bytes(b"a\\nb")
    >>> _ = (root / "b.py").write_bytes(b"c\\r\\n")
    >>> _ = (root / "Makefile").write_bytes(b"x\\ry\\r")
    >>> lines_by_extension(root)
    {'': 2, '.py': 3}
    """
    base = Path(root)
    totals: dict[str, int] = {}
    for p in list_files(base):
        ext = Path(p).suffix
        totals[ext] = totals.get(ext, 0) + count_lines(base / p)
    return dict(sorted(totals.items()))
