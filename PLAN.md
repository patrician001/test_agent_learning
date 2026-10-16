# Plan: add `count_lines`

## Files
- repostats/lines.py
- repostats/__init__.py
- tests/test_lines.py
- CHANGELOG.md

## Changes
- `repostats/lines.py` (new): module docstring plus `count_lines(path: str | Path) -> int`, stdlib only.
  It opens the file in text mode with universal newlines (`newline=None`, the default), `encoding="utf-8"` and
  `errors="replace"`, and returns `sum(1 for _ in f)`. Universal newlines turn CR, LF and CRLF each into one
  line break, so `"a\rb"` gives 2 and `"a\r\nb"` gives 2 (CRLF is one break, not two). A final line without a
  terminator is yielded by iteration, so it counts. An empty file yields nothing, giving 0. The file is streamed
  line by line, so memory stays bounded for long files. Python's text layer handles a CRLF that straddles an
  internal buffer boundary itself, so no chunking code of our own is needed. `errors="replace"` keeps
  undecodable bytes from raising, and the bytes 0x0A and 0x0D never occur inside a UTF-8 multibyte sequence, so
  replacement cannot change the count. The docstring has doctests in the style of `files.py` (temp file):
  `"a\nb"` gives 2, `"a\rb"` gives 2 and an empty file gives 0. It states that CR, LF and CRLF all end a line.
- `repostats/__init__.py`: import `count_lines` from `repostats.lines` and add it to `__all__`, keeping the list
  sorted: `["count_by_extension", "count_lines", "list_files"]`.
- `tests/test_lines.py` (new): use the `sample_repo` fixture. Files are written with `write_bytes` so that
  Python does not translate the line endings the test is checking.
  - `README.md` has 3 lines, `src/util.py` has 1, `Makefile` has 2.
  - Edge cases write extra files into the `sample_repo` directory inside the test:
    - empty file gives 0;
    - `b"a\nb"` (no final newline) gives 2;
    - `b"\n"` gives 1;
    - LF-only: `b"a\nb\n"` gives 2;
    - CR-only: `b"a\rb\r"` gives 2, and `b"a\rb"` (final line unterminated) gives 2;
    - CRLF: `b"a\r\nb\r\n"` gives 2, and `b"a\r\nb"` (final line unterminated) gives 2;
    - mixed `b"a\rb\nc\r\nd"` gives 4;
    - CRLF straddling a read-buffer boundary: `b"a" * 8191 + b"\r\n" + b"b"` (the CR is the last byte of
      the default 8192-byte text buffer) gives 2, and a long variant with many lines of varied lengths around
      the boundary checks that no CRLF is counted twice;
    - non-UTF-8 bytes such as `b"\xff\n\xfe"` give 2 without raising.
  - Import `count_lines` from `repostats`, which also checks the export.
  - `tests/conftest.py` is deliberately not changed. Adding files to `SAMPLE_FILES` would change the expected
    output of the existing `list_files` and `count_by_extension` tests.
- `CHANGELOG.md`: under `## Unreleased` add `- Added \`count_lines\`, which counts the lines in a text file.`

## Resolution of O1
The earlier LF-only binary algorithm is dropped. `count_lines` now uses standard-library text iteration with
universal newlines, so all three line endings (CR, LF, CRLF) count as one line break and the meaning of
"lines" is not narrowed. The tests listed above cover CR-only and CRLF files, each with and without a final
terminator, plus a CRLF split across a buffer boundary. The risk of a mid-boundary split is covered by the
test even though the implementation relies on Python's own handling and has no chunking of its own.

## Testing
Run `ruff check .`, `ruff format --check .` and `pytest --doctest-modules`. `tests/test_conventions.py`
enforces the doctest and no-dependencies rules automatically.

## Risks
- Line definition: Python universal newlines do not treat other Unicode separators (form feed, `\x85`, U+2028)
  as breaks, because file iteration splits only on CR, LF and CRLF. That matches the goal's three endings.
- Doctest escaping: `files.py` writes `\\n` inside a non-raw docstring; the same care is needed for `\\r` so the
  doctest sees an escape rather than a literal control character.
- The boundary test depends on the default buffer size (8192). If that were to change the test would still pass
  but cover less; it is a regression guard, not a proof.
- `pyproject.toml` is not touched, so there are no dependency changes.
- A missing path raises `FileNotFoundError` from `open`. This is unspecified by the goal and is left as is.
