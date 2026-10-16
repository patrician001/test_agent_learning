# Plan: `extension_report(root)`

## Files to change

1. **`repostats/report.py`** (new): `extension_report(root: str | Path) -> str`.
   - Calls `count_by_extension(root)`, sorts items by `(-count, extension)`, and renders Markdown:
     ```
     | Extension | Files |
     | --- | --- |
     | .md | 2 |
     | .py | 2 |
     | (none) | 1 |
     ```
   - The empty extension `""` is shown as `(none)`. The sort uses the real key (`""`), so "then by extension" applies to the raw value. A no-extension file with the same count as others therefore sorts first among ties (`""` < `.md`).
   - Header and separator rows are always emitted. An empty tree gives just those two rows.
   - Lines are joined with `"\n"`, with no trailing newline (decision to state in the docstring).
   - Docstring includes a `>>>` doctest (CONTRIBUTING rule 2; `tests/test_conventions.py` enforces it). The doctest builds its tree in a temp dir, like the existing ones in `files.py`.
   - Standard library only.
2. **`repostats/__init__.py`**: import `extension_report` and add it to `__all__` (kept sorted).
3. **`tests/test_report.py`** (new): tests take the `sample_repo` fixture (rule 1).
   - Sample tree: `.md`=2, `.py`=2, none=1. Expected output is the exact table above. This covers count-descending, extension tiebreak and `(none)`.
   - Empty case: in the test, `(sample_repo / "empty").mkdir()` and report on that directory. Expect header and separator only. (`.git` as root is not empty, since `list_files` skips `.git` only relative to root.)
   - Tie-order test: extend `sample_repo` in `conftest.py` only if needed. Prefer not to, so existing tests stay valid.
   - Export test: `from repostats import extension_report`.
4. **`CHANGELOG.md`**: under `## Unreleased` add `- Added \`extension_report\`, a Markdown table of file counts per extension.` (rule 3).
5. **`README.md`** (optional, small): add an `extension_report(".")` usage line.

## Testing

Run `ruff check .`, `ruff format --check .` and `pytest --doctest-modules`. These are the CI checks. They include the convention tests for doctests and no dependencies.

## Risks

- Tie-ordering ambiguity: `""` sorts before `.x`, so `(none)` can appear above same-count extensions. This follows the spec ("then by extension") literally. Mention it in the docstring.
- A literal extension string containing `|` is impossible in practice on most filesystems, but unlikely names could break the table. Escape `|` as `\|` in the extension cell, which is cheap.
- The empty-tree test makes a directory inside the fixture's tmp path rather than a new tree, to respect rule 1.
- Lesson L1 (byte line counting) does not apply here, because no lines are counted.
