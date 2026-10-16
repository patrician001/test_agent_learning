"""Listing and counting the files under a directory, skipping the .git directory."""

import re
from collections import Counter
from pathlib import Path

_Pattern = tuple[re.Pattern[str], bool, bool]  # (regex, negated, dir_only)


def _escaped(line: str, index: int) -> bool:
    """Return True if the character at index is preceded by an odd number of backslashes."""
    count = 0
    while index - count > 0 and line[index - count - 1] == "\\":
        count += 1
    return count % 2 == 1


def _class(seg: str, start: int) -> tuple[str, int] | None:
    """Translate the character class opening at seg[start] to (regex, next index), or None."""
    i = start + 1
    negated = i < len(seg) and seg[i] in "!^"
    if negated:
        i += 1
    body = ""
    first = True
    while i < len(seg):
        c = seg[i]
        if c == "]" and not first:
            regex = f"[^/{body}]" if negated else f"(?!/)[{body}]"
            try:
                re.compile(regex)
            except re.error:
                return None
            return regex, i + 1
        first = False
        if c == "\\" and i + 1 < len(seg):
            i += 1
            body += re.escape(seg[i])
        elif c == "-":
            body += "-"
        else:
            body += re.escape(c)
        i += 1
    return None


def _segment(seg: str) -> str:
    """Translate one "/"-free pattern segment to a regex."""
    out = ""
    i = 0
    while i < len(seg):
        c = seg[i]
        if c == "\\":
            if i + 1 < len(seg):
                out += re.escape(seg[i + 1])
            i += 2
            continue
        if c == "*":
            out += "[^/]*"
        elif c == "?":
            out += "[^/]"
        elif c == "[":
            translated = _class(seg, i)
            if translated is not None:
                out += translated[0]
                i = translated[1]
                continue
            out += re.escape(c)
        else:
            out += re.escape(c)
        i += 1
    return out


def _compile(line: str) -> _Pattern | None:
    """Compile one gitignore-style line to (regex, negated, dir_only); None if it has no pattern.

    >>> regex, negated, dir_only = _compile("docs/*.md")
    >>> bool(regex.fullmatch("docs/a.md")), bool(regex.fullmatch("docs/x/a.md"))
    (True, False)
    """
    if _escaped(line, len(line)):  # a lone trailing backslash makes the pattern invalid, as in git
        return None
    negated = line.startswith("!")
    if negated:
        line = line[1:]
    dir_only = line.endswith("/") and not _escaped(line, len(line) - 1)
    if dir_only:
        line = line[:-1]
    anchored = "/" in line
    line = line.removeprefix("/")
    if not line:
        return None
    segments = []
    current = ""
    i = 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            current += line[i : i + 2]
            i += 2
            continue
        if line[i] == "/":
            segments.append(current)
            current = ""
        else:
            current += line[i]
        i += 1
    segments.append(current)
    regex = "" if anchored else "(?:.*/)?"
    for n, seg in enumerate(segments):
        last = n == len(segments) - 1
        if seg == "**":
            regex += ".+" if last else "(?:.*/)?"
        else:
            regex += _segment(seg) + ("" if last else "/")
    return re.compile(regex), negated, dir_only


def _load_patterns(base: Path) -> list[_Pattern]:
    """Read the patterns of base/.statsignore; empty if there is no such file."""
    path = base / ".statsignore"
    if not path.is_file():
        return []
    patterns = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        while line.endswith(" ") and not _escaped(line, len(line) - 1):
            line = line[:-1]
        if not line or line.startswith("#"):
            continue
        compiled = _compile(line)
        if compiled is not None:
            patterns.append(compiled)
    return patterns


def _matches(path: str, is_dir: bool, patterns: list[_Pattern]) -> bool:
    """Return whether the last pattern matching path ignores it."""
    ignored = False
    for regex, negated, dir_only in patterns:
        if (is_dir or not dir_only) and regex.fullmatch(path):
            ignored = not negated
    return ignored


def _is_ignored(parts: tuple[str, ...], patterns: list[_Pattern]) -> bool:
    """Return whether the file at parts is ignored; nothing under an ignored directory is re-included."""
    for n in range(1, len(parts)):
        if _matches("/".join(parts[:n]), True, patterns):
            return True
    return _matches("/".join(parts), False, patterns)


def list_files(root: str | Path) -> list[str]:
    """Return the relative paths of the files under root, sorted, with "/" separators.

    The .git directory is skipped, and so are the paths matched by the .statsignore file at root,
    if any: one gitignore-style pattern per line (``*.log``, ``build/``, ``docs/*.md``,
    ``!keep.md``, ``**``), blank lines and lines starting with "#" ignored. Only root's own
    .statsignore is read, and it is listed like any other file.

    >>> import tempfile
    >>> root = Path(tempfile.mkdtemp())
    >>> (root / "src").mkdir()
    >>> _ = (root / "src" / "app.py").write_text("print(1)\\n")
    >>> _ = (root / "README.md").write_text("# demo\\n")
    >>> list_files(root)
    ['README.md', 'src/app.py']
    >>> _ = (root / ".statsignore").write_text("*.md\\n")
    >>> list_files(root)
    ['.statsignore', 'src/app.py']
    """
    base = Path(root)
    patterns = _load_patterns(base)
    return sorted(
        rel.as_posix()
        for p in base.rglob("*")
        if p.is_file()
        and ".git" not in (rel := p.relative_to(base)).parts
        and not _is_ignored(rel.parts, patterns)
    )


def count_by_extension(root: str | Path) -> dict[str, int]:
    """Return how many files under root have each extension ("" for none), sorted by extension.

    Files ignored by root's .statsignore (see list_files) are not counted.

    >>> import tempfile
    >>> root = Path(tempfile.mkdtemp())
    >>> for name in ["a.py", "b.py", "Makefile"]:
    ...     _ = (root / name).write_text("")
    >>> count_by_extension(root)
    {'': 1, '.py': 2}
    """
    counts = Counter(Path(p).suffix for p in list_files(root))
    return dict(sorted(counts.items()))
