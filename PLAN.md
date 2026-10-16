# Plan: `extension_report(root)`

## Design
`extension_report(root: str | Path) -> str` returns a Markdown table built from `count_by_extension(root)`:

```
| Extension | Files |
| --- | --- |
| .md | 2 |
| .py | 2 |
| (none) | 1 |
```

- Rows are sorted by file count descending, then by raw extension ascending (`""` sorts first among ties; only
  visible on a tie). Sorting uses the raw key, before escaping.
- Extensions keep the leading dot, as `count_by_extension` returns them. An empty extension is written `(none)`.
- An empty tree gives just the header and separator rows.
- Lines are joined with `"\n"`, no trailing newline.
- The function reuses `count_by_extension`, so it also skips `.git`.

### Escaping (resolves objection O1)
`Path.suffix` is arbitrary file-name text, so being a `str` does not make it safe in a table. A private helper
`_cell(text)` is applied to each extension when its row is built, so every extension stays in one cell on one line:
- `\` becomes `\\` (done first, so a backslash cannot combine with the output of the next rules);
- `|` becomes `&#124;` (an HTML entity that renders as a pipe). Chosen over `\|` because GFM splits cells before
  handling backslash escapes, so a name like `.a\|b` is ambiguous with `\|`; the entity is not;
- `\r\n`, `\n` and `\r` each become `<br>`, so a line break in a name cannot end the row.

`(none)` is used only for the empty string. The `Files` cell is an `int` and needs no escaping. Other inline
Markdown characters (`*`, backtick, `_`) do not change the table structure, so they are left as is. No owner
decision is needed.

## Files to change
1. `repostats/report.py` (new): `extension_report` and private `_cell`. The public docstring has a doctest in the
   style of `files.py` (`tempfile.mkdtemp` tree, then the expected table); `tests/test_conventions.py` requires
   `>>>` on public functions only, so `_cell` needs none.
2. `repostats/__init__.py`: import `extension_report` from `repostats.report` and add it to `__all__`.
3. `tests/test_report.py` (new), using only the `sample_repo` fixture (CONTRIBUTING rule 1):
   - Exact table for `sample_repo`: `.md` 2, `.py` 2, `(none)` 1.
   - Ordering: add a third `.py` inside the test so `.py` (3) moves ahead of `.md` (2). Do not change the shared
     fixture.
   - Empty directory (`tmp_path / "empty"`) gives only header and separator.
   - `extension_report` is importable from `repostats`.
   - O1 regression tests, writing extra files into the `sample_repo` directory inside each test, asserting exact
     output plus a structural check that every line has exactly two cells (a helper splits on `|` not preceded
     by a backslash, expecting 4 parts including the empty outer ones):
     - `example.a|b` gives `| .a&#124;b | 1 |`;
     - a name with `\n` (`x.a\nb`) and one with `\r` give `.a<br>b` rows, and `output.splitlines()` has exactly
       header + separator + one line per extension;
     - a backslash before a pipe (`x.a\|b`) gives `.a\\&#124;b`;
     - plain `.py` and `(none)` rows are unchanged by escaping.
     These tests `pytest.skip` if the filesystem rejects the name (`OSError`).
4. `CHANGELOG.md`: under `## Unreleased` add `- Added \`extension_report\`, a Markdown table of file counts by extension.`
5. `README.md` (optional, small): one usage line for `extension_report(".")`.

## Testing
`ruff check .`, `ruff format --check .` and `pytest --doctest-modules` (the CI checks, including the conventions
tests for doctests and no dependencies).

## Risks
- Escaping choices (`&#124;`, `<br>`) depend on the renderer: GFM renders both; a plain-text viewer shows the raw
  entity. `\|` is more common but ambiguous as described. Easy to change in `_cell`.
- File names with newlines may not be creatable on some filesystems (hence the skip).
- Format choices (dot kept, no trailing newline) are not specified by the goal; both are easy to change.
- Changing the shared `sample_repo` fixture could break `test_files.py`; avoided by adding files in each test.
- No new dependencies (rule 4).
