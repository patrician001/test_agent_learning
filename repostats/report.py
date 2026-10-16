"""A Markdown report of the files under a directory."""

from pathlib import Path

from repostats.files import count_by_extension


def _cell(text: str) -> str:
    """Make text safe to place in one Markdown table cell on one line."""
    return (
        text.replace("\\", "\\\\")
        .replace("|", "&#124;")
        .replace("\r\n", "<br>")
        .replace("\n", "<br>")
        .replace("\r", "<br>")
    )


def extension_report(root: str | Path) -> str:
    """Return a Markdown table of file counts by extension, most files first, then by extension.

    Files without an extension are written as "(none)".

    >>> import tempfile
    >>> root = Path(tempfile.mkdtemp())
    >>> for name in ["a.py", "b.py", "c.md", "Makefile"]:
    ...     _ = (root / name).write_text("")
    >>> print(extension_report(root))
    | Extension | Files |
    | --- | --- |
    | .py | 2 |
    | (none) | 1 |
    | .md | 1 |
    """
    counts = count_by_extension(root)
    lines = ["| Extension | Files |", "| --- | --- |"]
    for ext, n in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {_cell(ext) if ext else '(none)'} | {n} |")
    return "\n".join(lines)
