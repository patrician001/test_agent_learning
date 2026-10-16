# Plan: `python -m repostats` command-line entry point

## Design
- `repostats/cli.py` holds `main(argv=None) -> int`, built on stdlib `argparse` (no new dependencies).
  - Positional `root`; optional flag `--counts`.
  - Without `--counts`: print each `list_files(root)` entry on its own line.
  - With `--counts`: print `json.dumps(count_by_extension(root))`. The output is compact, key order is
    already sorted by the library, and the no-extension key is `""`.
  - If `root` is not a directory (`Path(root).is_dir()` is false, which includes a missing path or a file),
    print `repostats: error: not a directory: <root>` to stderr and return 2.
  - `main` returns the exit status and does not call `sys.exit`, so tests can call it directly.
    argparse's own usage errors (for example a missing ROOT) already exit with 2.
- `repostats/__main__.py` is `from repostats.cli import main`, then `if __name__ == "__main__": raise SystemExit(main())`.
  The guard is required. `tests/test_conventions.py` runs `pkgutil.walk_packages`, and pytest runs
  `--doctest-modules`. Both import every module in the package, so an unguarded call would run the CLI during collection.

## Files to change
1. `repostats/cli.py` (new): `main` as above, with a docstring that includes a passing `>>>` doctest
   (CONTRIBUTING rule 2). `public_functions()` in `test_conventions.py` will pick up `main`.
   The doctest can call `main(["--help"])`-free code, such as `main([str(nonexistent_tmp_path)])`. It must not
   build its own tree. It can use `tempfile` like the existing doctests in `files.py`, or check only the
   status-2 path. Keep it simple and deterministic.
2. `repostats/__main__.py` (new): thin guarded wrapper.
3. `tests/test_cli.py` (new): uses the `sample_repo` fixture (rule 1) and does not build its own trees.
   - `main([str(sample_repo)])` with `capsys` prints exactly `Makefile\nREADME.md\ndocs/guide.md\nsrc/app.py\nsrc/util.py\n`
     and returns 0. This also shows that `.git` is skipped.
   - `main(["--counts", str(sample_repo)])` returns 0, and `json.loads(out) == {"": 1, ".md": 2, ".py": 2}`.
   - A nonexistent path returns 2, stdout is empty, and stderr is non-empty. The same holds for a path that is a
     file (`sample_repo / "README.md"`), both with and without `--counts`.
   - One end-to-end test runs `subprocess.run([sys.executable, "-m", "repostats", str(sample_repo)])`. It checks
     the returncode and stdout. It also runs a bad root and checks returncode 2. This covers `__main__.py` and its
     guard. `cwd` is the repo root, or the package is already installed in CI, so `-m` resolves.
     Check how CI installs the package when writing it, and add `cwd=` if needed.
4. `CHANGELOG.md`: under `## Unreleased`, add `Added \`python -m repostats ROOT\` (and \`--counts\`) command-line entry point.` (rule 3).
5. `README.md`: optionally add a short usage snippet. The README was not read in detail; skip this if there is no
   usage section.

`pyproject.toml` stays unchanged: `packages = ["repostats"]` already includes the new modules, and no
`[project.scripts]` entry is requested.

## Verification
`ruff check .`, `ruff format --check .`, `pytest --doctest-modules` (all three are run by CI). Also run
`python -m repostats .`, `python -m repostats --counts .` and `python -m repostats /nope; echo $?` by hand.

## Risks
- Importing `__main__` during test or doctest collection. The `if __name__ == "__main__"` guard handles this, and
  the subprocess test covers the real invocation.
- `list_files` follows `rglob`, so symlinked files are listed and symlinked directories are not followed. This
  existing behaviour is unchanged.
- File names with newlines would break the one-path-per-line output. This is an edge case and is out of scope.
- Output uses the terminal encoding. Non-ASCII names could raise on a non-UTF-8 locale. `json.dumps` escapes
  non-ASCII by default, which is acceptable and parseable.
- `--counts` placed before or after ROOT both work in argparse. Tests use the order from the goal.
