# Plan: `python -m repostats <root>` command line

## Files
- repostats/__main__.py
- tests/test_main.py
- CHANGELOG.md

## Changes
- `repostats/__main__.py` (stdlib only: `sys`, `pathlib` via the package):
  - `main(argv: list[str] | None = None) -> int`. `argv` defaults to `sys.argv[1:]`. If `len(argv) != 1`, print
    `usage: python -m repostats <root>` to `sys.stderr` and return 2. Otherwise get
    `files = count_by_extension(root)` and `lines = lines_by_extension(root)`; for each extension in sorted order
    print `f"{ext} {files[ext]} {lines[ext]}"` and return 0. Both dicts have identical keys (same `list_files`
    grouping); iterate `sorted(files)`. Files with no extension have key `""`, so their line starts with a space
    (`" 1 2"`); this follows the goal's format literally and is documented in the docstring.
  - Docstring doctest in the `files.py` style: temp dir with `a.py` = `b"a\\nb"`, `b.py` = `b"c\\r\\n"`,
    `Makefile` = `b"x\\ry\\r"`; `main([str(root)])` prints ` 1 2` and `.py 2 3`, returns 0. The doctest must satisfy
    `tests/test_conventions.py` (public function needs `>>>`).
  - Bottom: `if __name__ == "__main__": raise SystemExit(main())`. The guard keeps `pytest --doctest-modules` and
    `pkgutil.walk_packages` imports side-effect free.
  - Line semantics come entirely from `count_lines` (CR, LF, CRLF each a break; unterminated last line counts), so
    lesson L1 is honoured with no new counting code.
  - `repostats/__init__.py` is unchanged (no new exported API).
- `tests/test_main.py`, using the `sample_repo` fixture (CONTRIBUTING rule 1), `capsys` for `main`, plus
  `subprocess.run([sys.executable, "-m", "repostats", ...])` with `cwd` set to the repo root for the real entry point:
  - Sample repo: stdout lines exactly `[" 2 2"... ]` computed from the fixture: `""` files 1 lines 2, `.md` 2 files
    4 lines, `.py` 2 files 4 lines → `" 1 2"`, `".md 2 4"`, `".py 2 4"`; `.git/config` excluded; exit 0; empty stderr.
  - Output is sorted by extension (extra files such as `.txt`, `.gz`, `archive.tar.gz`).
  - Line-ending cases written into the fixture with `write_bytes`: CR-only, CRLF, mixed, with and without final
    terminator, and a CRLF straddling the 8192-byte boundary (`b"a" * 8191 + b"\r\n" + b"b"` = 2), checked through the
    CLI output.
  - No argument: `main([])` returns 2, stderr contains `usage`, stdout empty; subprocess run exits 2. Two arguments
    also returns 2.
  - Empty directory (a fresh subdir of the fixture) prints nothing and exits 0.
- `CHANGELOG.md`: under `## Unreleased` add
  `- Added \`python -m repostats <root>\`, which prints the number of files and lines for each extension.`

## Testing
`ruff check .`, `ruff format --check .`, `pytest --doctest-modules` (includes `tests/test_conventions.py`).

## Risks
- Extensionless files give a line beginning with a space; consumers splitting on whitespace may mis-parse. Kept per
  the goal's literal format; noted in the docstring.
- Nonexistent root: `list_files` uses `rglob`, which yields nothing, so the output is empty with exit 0; the goal
  specifies no error handling, so this is left as is.
- Unreadable file raises from `count_lines`, giving a traceback and exit 1; unspecified, left as is.
- Subprocess tests depend on the package being importable from the repo root (`cwd`); running from the repo root is
  the norm for pytest here, and `cwd` is set explicitly.
- Doctest escaping of `\\r`/`\\n` in the non-raw docstring must use doubled backslashes.
