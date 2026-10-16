# Plan: `find_todos(root)`

## Files to change

1. **`repostats/files.py`**: add `find_todos(root: str | Path) -> list[tuple[str, int, str]]`.
   - Iterate `list_files(root)`. It already skips `.git`, returns "/" separated relative paths and sorts them, so path order comes for free.
   - Read each file with `(base / rel).read_text(encoding="utf-8")`. Catch **only `UnicodeDecodeError`** and skip that file. Every other error, including `OSError` (`PermissionError`, I/O errors), propagates. (Resolves O1.)
   - Split with `text.split("\n")`, not `str.splitlines()`. `read_text` already normalizes `\r\n` and `\r` to `\n` (universal newlines), so `\n` is the only line boundary. Form feed, vertical tab, `\x1c`-`\x1e`, `\x85`, U+2028 and U+2029 stay inside their line. (Resolves O2.) A trailing newline yields a final empty string, which cannot match.
   - For each `(lineno, line)` from `enumerate(..., start=1)` that matches the module-level `re.compile(r"\bTODO\b")`, append `(rel, lineno, line.strip())`. Lines are visited in order, so the ordering is path, then line number.
   - Docstring with a doctest in the style of `list_files`, and a mention of TODO search in the module docstring. The docstring states that unreadable files raise `OSError` and non-UTF-8 files are skipped.
2. **`repostats/__init__.py`**: import `find_todos` and add it to `__all__`, alphabetical.
3. **`tests/conftest.py`**: leave `SAMPLE_FILES` untouched so the existing `list_files` and `count_by_extension` tests keep passing. Add a second fixture `todo_repo(sample_repo)` that adds files on top of `sample_repo` (CONTRIBUTING rule 1: extend the fixtures, no ad-hoc trees):
   - `.git/notes.txt` containing `TODO` (must be skipped);
   - `docs/notes.md` with a TODO on lines 1 and 3 (ordering, 1-based numbers; sorts before `src/`);
   - `docs/indented.md` with `    TODO: indented   \n` (strip);
   - `docs/words.md` with `TODOS`, `AUTODOC` and `todo` (not matched);
   - `docs/ff.txt` written as `"header\x0cTODO: fix\nsecond TODO\n"` (O2 regression);
   - `docs/crlf.txt` written with `newline=""` / bytes as `"a\r\nTODO: b\rTODO: c\r\n"` (universal newlines);
   - `docs/binary.bin` written as bytes `b"TODO \xff\n"` (invalid UTF-8, must be skipped).
4. **`tests/test_files.py`**: tests using these fixtures:
   - `test_find_todos_sample_repo`: with `sample_repo`, returns `[("src/app.py", 2, "# TODO: handle errors")]`.
   - `test_find_todos_order_and_content` with `todo_repo`: the full expected list, so path and line order, 1-based numbers, stripping, `.git` skipped, invalid UTF-8 skipped and non-word matches excluded are all asserted at once.
   - `test_find_todos_form_feed_is_not_a_line_break` (O2): asserts `("docs/ff.txt", 1, "header\x0cTODO: fix")` is in the result and `("docs/ff.txt", 2, "second TODO")` has the right number, i.e. both content and line numbers.
   - `test_find_todos_universal_newlines`: `docs/crlf.txt` gives `("docs/crlf.txt", 2, "TODO: b")` and `("docs/crlf.txt", 3, "TODO: c")`.
   - `test_find_todos_propagates_oserror` (O1): `monkeypatch` `Path.read_text` to raise `PermissionError` for one file of `sample_repo` and assert `pytest.raises(PermissionError)`. A chmod-based test is avoided because it does not fail when the tests run as root.
5. **`CHANGELOG.md`**: under `## Unreleased` add `- Added \`find_todos\`.` (rule 3).

No `pyproject.toml` change (rule 4). Stdlib only (`re`, `pathlib`).

## Testing

- `pytest --doctest-modules` (new doctest, new tests, and `test_conventions.py`, which requires a doctest on every public function).
- `ruff check .` and `ruff format --check .` (line length 100).

## Risks / decisions

- **O1, errors propagate.** A scan that hits an unreadable file raises instead of returning a quietly incomplete list. Only invalid UTF-8 is skipped, as the goal allows. If the owner later wants partial results, that would be a deliberate API addition (e.g. an `on_error` argument), not part of this change.
- **O2, line boundaries.** Only `\n` (after universal-newline normalization) ends a line. A lone `\r` is treated as a line break by `read_text`, as in any Python text read. This matches "ordinary text-file lines".
- **"The word TODO"**: case-sensitive whole-word match (`\bTODO\b`). `TODO:` and `(TODO)` match, but `TODOS`, `todo`, `AUTODOC` and `TODO_x` do not. If a plain substring match is wanted, drop the `\b`. Tests pin the chosen behaviour.
- **Ordering**: `list_files` sorts the posix path strings (`a.py` before `a/b.py`, since `.` < `/`). This is consistent with the existing function.
- **Valid-UTF-8 binary files** (e.g. containing NUL) are scanned. Acceptable per the goal.
- **Memory**: each file is read whole. Fine for a checkout. Streaming would complicate the UTF-8 skip, since a partly-read file would have to be discarded.
- **BOM**: a UTF-8 BOM stays as `﻿` at the start of line 1; `str.strip()` does not remove it. Not handled.
- **Symlinks**: `list_files` uses `is_file()`, so symlinks to files are followed, and broken symlinks are not listed. Unchanged behaviour.
