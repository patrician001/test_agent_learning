# Plan: honour a root `.statsignore` in `list_files` / `count_by_extension`

## Background
`repostats/files.py` has `list_files(root)` (rglob, skips `.git`) and `count_by_extension(root)`, which calls
`list_files`. So the ignore logic goes in `list_files` only and `count_by_extension` inherits it. The package is
stdlib-only (CONTRIBUTING rule 4), so no `pathspec`; `fnmatch` is not enough (no `**`, `*` crosses `/`), so
patterns are translated to regexes by a small private helper.

## Changes

### `repostats/files.py`
- Add private helpers (names start with `_`, so no doctest required, but short doctests are welcome):
  - `_load_rules(base) -> list[tuple[re.Pattern, bool, bool]]`: read `base / ".statsignore"` if it is a file
    (missing file -> no rules; read as UTF-8 with `errors="replace"`). Per line: strip the trailing `\n`/`\r`
    and trailing unescaped spaces; skip blank lines and lines starting with `#`. Do not use `str.splitlines()`
    (it splits on `\x0b`, `\x0c`, etc.); use `split("\n")`.
  - `_compile(pattern) -> (regex, negated, dir_only)` with gitignore semantics:
    - trailing `/` -> matches directories only (and so everything beneath them);
    - a `/` at the start or middle -> anchored to the root; otherwise the pattern matches the name at any depth;
    - `*` and `?` do not match `/`; `**/`, `/**`, `/**/` work as in gitignore; `[...]` classes supported;
      `\` escapes the next character (e.g. `\#x`, `\!x`).
    - leading `!` negates (re-includes); the last matching rule wins.
- `_is_ignored(rel_parts, is_dir, rules)`: a path is ignored if any ancestor directory is ignored (so `build/`
  drops `build/x/y.o`, and a negation cannot re-include a file under an ignored dir, as in git), else by the
  last matching rule on the path itself.
- `list_files`: after the existing `.git` filter, drop ignored files. `.statsignore` itself is not special-cased,
  so it is listed unless a pattern matches it. Update the docstring, and extend the doctest with a `.statsignore`
  example (`*.log` ignored).
- `count_by_extension`: docstring one-liner noting it honours `.statsignore`; no logic change.
- Only the `.statsignore` at `root` is read; nested ones are ignored (stated in docstring).

### `tests/conftest.py`
`sample_repo` is shared, and the existing tests assert its exact listing, so do not add `.statsignore` to
`SAMPLE_FILES`. Instead extend the fixture's module with a second fixture, `sample_repo_with_ignore`, built on
`sample_repo` (adds extra files such as `debug.log`, `src/trace.log`, `build/out.o`, `src/build/x.o`,
`docs/api.md`, `docs/sub/deep.md`, plus a `.statsignore`). It must be a fixture in conftest, not an ad-hoc tmp
tree (CONTRIBUTING rule 1). Tests write different `.statsignore` contents over it as needed.

### `tests/test_files.py`
New tests using those fixtures:
- no `.statsignore` -> unchanged listing (existing tests keep passing);
- `*.log` ignores logs at any depth; `build/` ignores the dir at any depth but not a *file* named `build`;
- `docs/*.md` ignores `docs/api.md` but not `docs/sub/deep.md` nor `README.md`; anchoring (`/README.md`);
- blank lines, `# comments` and trailing whitespace are ignored; CRLF file works; empty `.statsignore` works;
- `.statsignore` is itself listed, and is hidden only if a pattern names it;
- `!` re-include and `**` cases; negation under an ignored directory stays ignored;
- `count_by_extension` reflects ignored files;
- `.statsignore` that is a directory does not crash.

### `CHANGELOG.md`
Under `## Unreleased`: `- Added support for a root \`.statsignore\` file (gitignore-style patterns) in \`list_files\` and \`count_by_extension\`.`

### `README.md`
Optional two-line note on `.statsignore`.

## Verification
`ruff check .`, `ruff format --check .`, `pytest --doctest-modules` (the CI trio); `test_conventions.py` confirms
public doctests and no dependencies.

## Risks
- Gitignore semantics are subtle; a hand-written translator may differ from git in corners (escapes, `**`,
  character-class edge cases). Mitigation: cover the goal's three examples plus the cases above; document that
  this is a subset-faithful implementation.
- Scope: `!` negation and `**` are not demanded by the goal. If the reviewer wants a smaller PR, drop them and
  treat `!`-lines as ordinary (non-matching) patterns; the rest of the plan is unchanged.
- Performance: patterns are compiled once per call, but each file is checked against all rules and its ancestors;
  fine for repository-sized trees. `rglob` still descends ignored directories (no pruning) — acceptable now.
- Behaviour change for anyone with an existing `.statsignore` at root (intended by the goal).
- A `.statsignore` pattern could match `.git`-less paths only; `.git` stays skipped regardless.
