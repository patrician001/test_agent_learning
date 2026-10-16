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
