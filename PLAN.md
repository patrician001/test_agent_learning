# Plan: `count_lines(root)`

## Behaviour
`count_lines(root) -> dict[str, int]`: total lines per file extension (`Path.suffix`, `""` for none) under `root`, sorted by extension, `.git` skipped. A file whose bytes are not valid UTF-8 is skipped (contributes nothing, and its extension gets no key unless other files have it).

Decisions (the goal leaves these open; chosen for least surprise):
- Line = a `\n`-terminated line, plus a final unterminated line if the file does not end in `\n`. So `""` → 0, `"a"` → 1, `"a\n"` → 1, `"a\nb"` → 2. Count with `data.count(b"\n") + int(bool(data) and not data.endswith(b"\n"))` (an explicit int final-line term; the bare `data and ...` form yields `b""` for an empty file and raises `TypeError` on int + bytes) after a strict `data.decode("utf-8")` check. Do not use `str.splitlines()` (it also splits on `\x0b`, `\x0c`, ` `, etc.).
- Files are read as bytes (no newline translation, no locale dependence). `\r\n` counts as one line; a lone `\r` is not a line break.
- An extension whose only files are skipped or empty: skipped-only → no key; empty valid file → key with 0.
- Other I/O errors (e.g. `PermissionError`) propagate; only the UTF-8 failure is swallowed.

## Files to change
1. `repostats/files.py` — add `count_lines`, reusing `list_files(root)` for the walk and `.git` skipping (same pattern as `count_by_extension`: `Counter`, then `dict(sorted(...))`). Read each file with `(Path(root) / rel).read_bytes()`, `try: decode("utf-8") except UnicodeDecodeError: continue`. Docstring with a doctest (CONTRIBUTING rule 2; `tests/test_conventions.py` enforces it), built like the existing ones with `tempfile.mkdtemp()`; include a final-line-without-newline case. Update the module docstring only if needed ("Listing and counting" already fits).
2. `repostats/__init__.py` — import `count_lines` and add it to `__all__` (keep alphabetical: `count_by_extension`, `count_lines`, `list_files`).
3. `tests/test_files.py` — import `count_lines` and add tests, all using the `sample_repo` fixture (rule 1):
   - `test_count_lines`: on the unmodified fixture expect `{"": 2, ".md": 4, ".py": 4}` (Makefile 2; README 3 + guide 1; app 3 + util 1). `.git/config` must not be counted (would add a line to `""`... it has no suffix, so a leak would show as `"": 3`).
   - `test_count_lines_skips_invalid_utf8`: write `sample_repo / "logo.png"` with `b"\xff\xfe\x00"` and `sample_repo / "bad.py"` with `b"x = 1\n\xff\n"` inside the test, then assert the result equals the baseline (no `.png` key, `.py` unchanged).
   - `test_count_lines_final_line_without_newline_and_empty_file`: add `notes.txt` (`"a\nb"`) and `empty.txt` (`""`), expect `".txt": 2`.
   - Assert key order: `list(result) == sorted(result)`.
   Writing extra files inside tests (rather than extending `conftest.py`) is deliberate: adding a non-UTF-8 file to `SAMPLE_FILES` would change the expected output of the existing `list_files` and `count_by_extension` tests. (Also, `SAMPLE_FILES` is written with `write_text`, which can't produce invalid bytes.)
4. `CHANGELOG.md` — under `## Unreleased` add `- Added \`count_lines\`.` (rule 3).
5. `README.md` — it has an API example block; add `count_lines` to the import and one line `count_lines(".")  # {'': 2, '.md': 40, ...}`.

No change to `pyproject.toml` (rule 4: stdlib only).

## Objection resolution
- O1 (empty file `TypeError`): resolved by the `int(bool(data) and not data.endswith(b"\n"))` term above, which is always 0 or 1 (0 for empty data). The empty-file regression test (`empty.txt` in `test_count_lines_final_line_without_newline_and_empty_file`) is retained and must also assert `count_lines` does not raise and that the empty file contributes 0. Add an empty-file case to the doctest too.

## Verification
`ruff check .`, `ruff format --check .`, `pytest --doctest-modules` (the three CI checks); this also runs `test_conventions.py`, which confirms the doctest and no-dependency rules.

## Risks
- Line-count definition is a judgment call (see above); documented in the docstring so it is explicit.
- Reads every file fully into memory; fine for repo checkouts, but a huge file (or large binaries in the tree) costs memory/time. Could stream in chunks later; not worth the complexity now.
- `list_files` follows `rglob` semantics: symlinks to files are counted, and a broken symlink is excluded by `is_file()`. Unreadable files raise. Both inherited, unchanged behaviour.
- Binary files that happen to be valid UTF-8 (e.g. all-ASCII, NUL bytes) are counted; the goal only specifies UTF-8 validity.
- Doctest temp dirs are not cleaned up, matching existing doctests.
