"""Listing and counting the files under a directory, skipping the .git directory."""

from collections import Counter
from pathlib import Path


def list_files(root: str | Path) -> list[str]:
    """Return the relative paths of the files under root, sorted, with "/" separators.

    The .git directory is skipped.

    >>> import tempfile
    >>> root = Path(tempfile.mkdtemp())
    >>> (root / "src").mkdir()
    >>> _ = (root / "src" / "app.py").write_text("print(1)\\n")
    >>> _ = (root / "README.md").write_text("# demo\\n")
    >>> list_files(root)
    ['README.md', 'src/app.py']
    """
    base = Path(root)
    return sorted(
        p.relative_to(base).as_posix()
        for p in base.rglob("*")
        if p.is_file() and ".git" not in p.relative_to(base).parts
    )


def count_by_extension(root: str | Path) -> dict[str, int]:
    """Return how many files under root have each extension ("" for none), sorted by extension.

    >>> import tempfile
    >>> root = Path(tempfile.mkdtemp())
    >>> for name in ["a.py", "b.py", "Makefile"]:
    ...     _ = (root / name).write_text("")
    >>> count_by_extension(root)
    {'': 1, '.py': 2}
    """
    counts = Counter(Path(p).suffix for p in list_files(root))
    return dict(sorted(counts.items()))


def count_lines(root: str | Path) -> dict[str, int]:
    """Return the total lines per file extension under root ("" for none), sorted by extension.

    A line is a "\\n"-terminated line, plus a final line without a newline. Files that are
    not valid UTF-8 are skipped.

    >>> import tempfile
    >>> root = Path(tempfile.mkdtemp())
    >>> _ = (root / "a.py").write_bytes(b"x = 1\\ny = 2")
    >>> _ = (root / "b.py").write_bytes(b"z = 3\\n")
    >>> _ = (root / "empty.txt").write_bytes(b"")
    >>> _ = (root / "logo.png").write_bytes(b"\\xff\\xfe")
    >>> count_lines(root)
    {'.py': 3, '.txt': 0}
    """
    base = Path(root)
    counts: Counter[str] = Counter()
    for rel in list_files(base):
        data = (base / rel).read_bytes()
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        counts[Path(rel).suffix] += data.count(b"\n") + int(bool(data) and not data.endswith(b"\n"))
    return dict(sorted(counts.items()))
