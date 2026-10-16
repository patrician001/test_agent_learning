"""Command line: python -m repostats <root>."""

import sys

from repostats.files import count_by_extension
from repostats.lines import lines_by_extension


def main(argv: list[str] | None = None) -> int:
    """Print "<extension> <files> <lines>" for each extension under the root, sorted by extension; return the exit code.

    Without exactly one argument, print a usage line to stderr and return 2. Files with no extension
    have the extension "", so their line starts with a space.

    >>> import tempfile
    >>> from pathlib import Path
    >>> root = Path(tempfile.mkdtemp())
    >>> _ = (root / "a.py").write_bytes(b"a\\nb")
    >>> _ = (root / "b.py").write_bytes(b"c\\r\\n")
    >>> _ = (root / "Makefile").write_bytes(b"x\\ry\\r")
    >>> main([str(root)])
     1 2
    .py 2 3
    0
    """
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) != 1:
        print("usage: python -m repostats <root>", file=sys.stderr)
        return 2
    files = count_by_extension(argv[0])
    lines = lines_by_extension(argv[0])
    for ext in sorted(files):
        print(f"{ext} {files[ext]} {lines[ext]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
