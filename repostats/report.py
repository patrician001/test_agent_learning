"""Markdown reports built from the file statistics."""

from pathlib import Path

from repostats.files import count_by_extension


def extension_report(root: str | Path) -> str:
    """Return a Markdown table of file counts per extension under root.

    Rows are ordered by file count, most first, then by extension. Files without an extension are
    shown as "(none)" but sort by their real key (""), so they come first among equal counts. The
    header and separator rows are always present, and the result has no trailing newline.

    >>> import tempfile
    >>> from pathlib import Path
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
    for extension, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        label = extension.replace("|", "\\|") if extension else "(none)"
        lines.append(f"| {label} | {count} |")
    return "\n".join(lines)
