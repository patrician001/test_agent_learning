"""Listing and counting the files under a directory, skipping .git and .statsignore matches."""

import re
from collections import Counter
from pathlib import Path

IGNORE_FILE = ".statsignore"

_Rule = tuple[re.Pattern[str], bool, bool]


def _strip_trailing_spaces(line: str) -> str:
    """Drop trailing spaces from a pattern line, keeping one that is escaped with a backslash.

    >>> _strip_trailing_spaces("a b  ")
    'a b'
    >>> _strip_trailing_spaces("a\\\\ ")
    'a\\\\ '
    """
    stripped = line.rstrip(" ")
    if stripped.endswith("\\") and len(stripped) < len(line):
        stripped += " "
    return stripped


def _class_to_regex(pattern: str, start: int) -> tuple[str, int] | None:
    """Translate the "[...]" class at pattern[start]; return (regex, next index) or None."""
    i = start + 1
    negate = i < len(pattern) and pattern[i] in "!^"
    if negate:
        i += 1
    members = []
    first = True
    while i < len(pattern):
        char = pattern[i]
        if char == "]" and not first:
            body = "".join(members)
            if not body:
                return None
            return f"[{'^' if negate else ''}{body}]", i + 1
        if char == "\\" and i + 1 < len(pattern):
            i += 1
            char = pattern[i]
        literal = char in "\\]^[-" and not _is_range_dash(pattern, i, char)
        members.append(re.escape(char) if literal else char)
        first = False
        i += 1
    return None


def _is_range_dash(pattern: str, i: int, char: str) -> bool:
    return char == "-" and pattern[i - 1] != "[" and i + 1 < len(pattern) and pattern[i + 1] != "]"


def _compile(pattern: str) -> _Rule:
    """Translate a gitignore-style pattern into (regex, negated, dir_only).

    >>> regex, negated, dir_only = _compile("build/")
    >>> bool(regex.match("src/build")), negated, dir_only
    (True, False, True)
    >>> bool(_compile("docs/*.md")[0].match("docs/sub/a.md"))
    False
    """
    negated = pattern.startswith("!")
    if negated:
        pattern = pattern[1:]
    dir_only = pattern.endswith("/")
    pattern = pattern.rstrip("/")
    anchored = "/" in pattern
    pattern = pattern.lstrip("/")

    out = []
    i = 0
    while i < len(pattern):
        char = pattern[i]
        at_segment_start = i == 0 or pattern[i - 1] == "/"
        double_star = pattern.startswith("**", i) and pattern[i + 2 : i + 3] in ("/", "")
        if double_star and at_segment_start:
            if pattern[i + 2 :] == "":
                out.append(".*")
                i += 2
            else:
                out.append("(?:.*/)?")
                i += 3
        elif char == "*":
            out.append("[^/]*")
            while pattern.startswith("*", i):
                i += 1
        elif char == "?":
            out.append("[^/]")
            i += 1
        elif char == "[":
            translated = _class_to_regex(pattern, i)
            if translated is None:
                out.append(re.escape(char))
                i += 1
            else:
                out.append(translated[0])
                i = translated[1]
        elif char == "\\" and i + 1 < len(pattern):
            out.append(re.escape(pattern[i + 1]))
            i += 2
        else:
            out.append(re.escape(char))
            i += 1
    prefix = "" if anchored else "(?:.*/)?"
    return re.compile(f"^{prefix}{''.join(out)}$", re.DOTALL), negated, dir_only


def _load_rules(base: Path) -> list[_Rule]:
    """Read the rules of base/.statsignore; no file (or no readable file) means no rules.

    >>> import tempfile
    >>> _load_rules(Path(tempfile.mkdtemp()))
    []
    """
    path = base / IGNORE_FILE
    if not path.is_file():
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    rules = []
    for line in text.split("\n"):
        line = _strip_trailing_spaces(line.removesuffix("\r"))
        if line and not line.startswith("#"):
            rules.append(_compile(line))
    return rules


def _matches(path: str, is_dir: bool, rules: list[_Rule]) -> bool:
    """Whether the last rule matching path says to ignore it."""
    ignored = False
    for regex, negated, dir_only in rules:
        if (is_dir or not dir_only) and regex.match(path):
            ignored = not negated
    return ignored


def _is_ignored(rel_parts: tuple[str, ...], rules: list[_Rule]) -> bool:
    """Whether the file at rel_parts is ignored itself or sits under an ignored directory.

    >>> _is_ignored(("build", "x.o"), [_compile("build/")])
    True
    """
    for end in range(1, len(rel_parts)):
        if _matches("/".join(rel_parts[:end]), True, rules):
            return True
    return _matches("/".join(rel_parts), False, rules)


def list_files(root: str | Path) -> list[str]:
    """Return the relative paths of the files under root, sorted, with "/" separators.

    The .git directory is skipped. So are the paths matched by the .statsignore file at root, if
    there is one: one gitignore-style pattern per line, blank lines and lines starting with "#"
    ignored. Nested .statsignore files are not read, and the .statsignore file itself is listed
    like any other file.

    >>> import tempfile
    >>> root = Path(tempfile.mkdtemp())
    >>> (root / "src").mkdir()
    >>> _ = (root / "src" / "app.py").write_text("print(1)\\n")
    >>> _ = (root / "README.md").write_text("# demo\\n")
    >>> list_files(root)
    ['README.md', 'src/app.py']
    >>> _ = (root / "debug.log").write_text("")
    >>> _ = (root / ".statsignore").write_text("*.log\\n")
    >>> list_files(root)
    ['.statsignore', 'README.md', 'src/app.py']
    """
    base = Path(root)
    rules = _load_rules(base)
    found = []
    for p in base.rglob("*"):
        rel = p.relative_to(base)
        if p.is_file() and ".git" not in rel.parts and not _is_ignored(rel.parts, rules):
            found.append(rel.as_posix())
    return sorted(found)


def count_by_extension(root: str | Path) -> dict[str, int]:
    """Return how many files under root have each extension ("" for none), sorted by extension.

    Files ignored by the .statsignore at root are not counted (see list_files).

    >>> import tempfile
    >>> root = Path(tempfile.mkdtemp())
    >>> for name in ["a.py", "b.py", "Makefile"]:
    ...     _ = (root / name).write_text("")
    >>> count_by_extension(root)
    {'': 1, '.py': 2}
    """
    counts = Counter(Path(p).suffix for p in list_files(root))
    return dict(sorted(counts.items()))
