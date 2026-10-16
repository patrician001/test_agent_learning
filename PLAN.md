# Plan: `count_lines(root)`

## Behaviour
`count_lines(root) -> dict[str, int]`: total lines per file extension (`""` for none) under `root`, sorted by extension, skipping `.git`. A file whose bytes are not valid UTF-8 is skipped (contributes nothing, and does not create a key for its extension).

Line definition (chosen to match `wc -l` plus a final unterminated line): `text.count("\n")`, plus 1 if the text is non-empty and does not end in `"\n"`. An empty file counts 0 lines. (Not `str.splitlines()`, which also splits on `\x0c`, ` `, etc.) A file that decodes but has 0 lines still yields its extension key with 0 — consistent with `count_by_extension`, which lists every file's extension.

## Files to change
- `repostats/files.py`: add `count_lines`. Reuse `list_files(root)` for the file set and `.git` skipping; for each relative path read `(Path(root) / p).read_bytes()`, `.decode("utf-8")` inside `try/except UnicodeDecodeError: continue`, add the line count to a `Counter` keyed by `Path(p).suffix`, return `dict(sorted(...))`. Docstring includes a passing `>>>` doctest in the same style as `count_by_extension` (tempdir with e.g. `a.py` = `"x\ny\n"`, `b.py` = `"z"`, `Makefile` = `"m\n"` → `{'': 1, '.py': 3}`), per CONTRIBUTING rule 2.
- `repostats/__init__.py`: import `count_lines` and add it to `__all__` (kept sorted).
- `tests/test_files.py`: import `count_lines` from `repostats`; tests use the `sample_repo` fixture (rule 1), no own temp trees.
  - `test_count_lines`: `sample_repo` → `{"": 2, ".md": 4, ".py": 4}` (README 3 + guide 1; app 3 + util 1; Makefile 2; `.git/config` ignored).
  - `test_count_lines_skips_invalid_utf8`: write `sample_repo / "bad.py"` with `write_bytes(b"\xff\xfe\n")` inside the test, assert the result is unchanged from the base case.
  - `test_count_lines_unterminated_and_empty`: write `no_newline.txt` = `"a\nb"` (2) and `empty.txt` = `""` (0); assert `".txt": 2`, and that keys stay sorted.
  - The fixture in `tests/conftest.py` stays unchanged, so existing tests' expectations are unaffected.
- `CHANGELOG.md`: under `## Unreleased` add `- Added \`count_lines\`.` (rule 3).
- `README.md`: add `count_lines(".")  # {'.md': 120, '.py': 340, ...}` to the usage snippet and import line.

No changes to `pyproject.toml` (rule 4; stdlib only).

## Testing
`ruff check .`, `ruff format --check .`, `pytest --doctest-modules` (the three CI checks); `tests/test_conventions.py` should also pass, as it presumably enforces the doctest/changelog rules.

## Risks
- Line-count definition is a judgement call (unterminated last line counts; `\r\n` counts once, a lone `\r` is not a line break). Documented in the docstring.
- Reads whole files into memory; fine for a repo checkout, large files could be heavy. Not worth streaming for this PR.
- Unreadable files (permissions, broken symlinks passing `is_file()` are excluded already) would raise `OSError`; the spec only asks to skip non-UTF-8, so these propagate rather than being silently hidden.
- A UTF-8 BOM decodes as `utf-8` to `﻿` without affecting line counts; fine.
