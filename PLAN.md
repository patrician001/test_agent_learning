# Plan: add `lines_by_extension`

## Files
- repostats/lines.py
- repostats/__init__.py
- tests/test_lines.py
- CHANGELOG.md

## Changes
- `repostats/lines.py`: add `lines_by_extension(root: str | Path) -> dict[str, int]`. Import `Counter`-free
  logic: for each `p` in `list_files(root)` (import from `repostats.files`), key is `Path(p).suffix` (same
  grouping as `count_by_extension`, "" for none), add `count_lines(Path(root) / p)` to a running total.
  Return `dict(sorted(totals.items()))`, sorted by extension like `count_by_extension`. Because it reuses
  `count_lines`, line semantics are unchanged: CR, LF and CRLF each one break, unterminated last line counts
  (lesson L1). Extensions with only empty files appear with 0. Docstring has a doctest in the `files.py`
  style (temp dir, files written with `write_bytes` and `\\n` / `\\r` escaped), e.g. `a.py` = `b"a\\nb"`,
  `b.py` = `b"c\\r\\n"`, `Makefile` = `b"x\\ry\\r"` giving `{'': 2, '.py': 3}`.
- `repostats/__init__.py`: import `lines_by_extension`; `__all__` sorted:
  `["count_by_extension", "count_lines", "lines_by_extension", "list_files"]`.
- `tests/test_lines.py`: tests on `sample_repo`, importing from `repostats`.
  - Sample result: `.md` = README 3 + docs/guide 1 = 4, `.py` = app 3 + util 1 = 4, `""` (Makefile) = 2;
    `.git/config` excluded. Expect `{'': 2, '.md': 4, '.py': 4}`, and keys equal those of `count_by_extension`.
  - Extra files written into the fixture dir with `write_bytes`: CR-only, CRLF and mixed files, with and
    without final terminator, summed within one extension (e.g. `.txt`); an empty file giving 0 for its
    extension; a file with a CRLF straddling the 8192-byte buffer (`b"a" * 8191 + b"\r\n" + b"b"`) counted
    as 2 in the total; a file with no extension and a dotfile/multi-dot name (`archive.tar.gz` -> `.gz`)
    grouped as `count_by_extension` does.
  - A root with no files gives `{}` (use a fresh empty `tmp_path` subdir derived from the fixture, not a new tree
    helper; or skip if awkward).
- `CHANGELOG.md`: under `## Unreleased` add
  `- Added \`lines_by_extension\`, which totals the lines in the files under a directory for each extension.`
- `tests/conftest.py` is not changed: new SAMPLE_FILES would alter existing tests' expectations.

## Testing
`ruff check .`, `ruff format --check .`, `pytest --doctest-modules`; `tests/test_conventions.py` enforces
doctest and no-dependency rules.

## Risks
- Dotfiles: `Path(".env").suffix` is "" — identical to `count_by_extension`, deliberately kept consistent.
- Unreadable file or broken symlink: `list_files` uses `is_file()` so broken links are skipped; a permission
  error propagates from `count_lines`, unspecified by the goal and left as is.
- Doctest escaping of `\\r`/`\\n` in the non-raw docstring must be doubled backslashes.
- Reads every file fully; cost is linear in repo size, acceptable.
