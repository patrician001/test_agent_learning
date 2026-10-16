import pytest

from repostats import count_by_extension, list_files


def test_list_files_skips_git(sample_repo):
    assert list_files(sample_repo) == [
        "Makefile",
        "README.md",
        "docs/guide.md",
        "src/app.py",
        "src/util.py",
    ]


def test_count_by_extension(sample_repo):
    assert count_by_extension(sample_repo) == {"": 1, ".md": 2, ".py": 2}


BASE = ["Makefile", "README.md", "docs/guide.md", "src/app.py", "src/util.py"]


def listed(root):
    return [p for p in list_files(root) if p != ".statsignore"]


def test_no_statsignore_file(sample_repo):
    assert list_files(sample_repo) == BASE


def test_empty_and_directory_statsignore(statsignore):
    root = statsignore("")
    assert list_files(root) == sorted([*BASE, ".statsignore"])
    (root / ".statsignore").unlink()
    (root / ".statsignore").mkdir()
    assert list_files(root) == BASE


def test_statsignore_is_listed(statsignore):
    assert ".statsignore" in list_files(statsignore("*.log\n"))


@pytest.mark.parametrize("pattern", [".statsignore", ".*"])
def test_statsignore_can_ignore_itself(statsignore, pattern):
    assert ".statsignore" not in list_files(statsignore(pattern + "\n"))


def test_git_still_skipped(statsignore):
    assert not any(p.startswith(".git/") for p in list_files(statsignore("!.git/config\n")))


def test_star_pattern_any_depth(statsignore):
    root = statsignore("*.log\n", ["a.log", "src/b.log", "src/c.logx"])
    assert listed(root) == sorted([*BASE, "src/c.logx"])


def test_dir_only_pattern(statsignore):
    root = statsignore("build/\n", ["build/x.o", "src/build/y.o", "lib/build"])
    assert listed(root) == sorted([*BASE, "lib/build"])


def test_path_pattern_is_anchored(statsignore):
    root = statsignore("docs/*.md\n", ["docs/sub/x.md"])
    assert listed(root) == sorted([b for b in BASE if b != "docs/guide.md"] + ["docs/sub/x.md"])


def test_leading_slash_anchors(statsignore):
    root = statsignore("/README.md\n", ["src/README.md"])
    assert listed(root) == sorted([b for b in BASE if b != "README.md"] + ["src/README.md"])


def test_comments_blanks_trailing_space_crlf(statsignore):
    root = statsignore("# comment\r\n\r\n   \r\nplain.txt  \r\n", ["plain.txt", "other.txt"])
    assert listed(root) == sorted([*BASE, "other.txt"])


def test_count_by_extension_filtered(statsignore):
    assert count_by_extension(statsignore("*.md\n")) == {"": 2, ".py": 2}


@pytest.mark.parametrize(
    "pattern, ignored, kept",
    [
        ("**/gen.py", ["gen.py", "a/gen.py", "a/b/gen.py"], ["xgen.py"]),
        ("out/**", ["out/a", "out/b/c"], ["x/out/a"]),
        ("a/**/z.txt", ["a/z.txt", "a/b/z.txt", "a/b/c/z.txt"], ["b/a/z.txt", "a/z.txt.bak"]),
        ("f?.txt", ["f1.txt"], ["f.txt", "f12.txt"]),
        ("f?x", [], ["f/x"]),
        ("[ab].txt", ["a.txt", "b.txt"], ["c.txt"]),
        ("[0-9].dat", ["5.dat"], ["a.dat"]),
        ("[!a].txt", ["b.txt"], ["a.txt"]),
        ("[^a].txt", ["b.txt"], ["a.txt"]),
        ("a[/]b", [], ["a/b"]),
        ("un[term.txt", ["un[term.txt"], ["unx.txt"]),
        (r"\#hash.txt", ["#hash.txt"], []),
        ("#hash.txt", [], ["#hash.txt"]),
        (r"\!bang.txt", ["!bang.txt"], ["bang.txt"]),
        (r"literal\*.txt", ["literal*.txt"], ["literalX.txt", "literal.txt"]),
        (r"q\?.txt", ["q?.txt"], ["qX.txt"]),
        (r"br\[a].txt", ["br[a].txt"], ["bra.txt"]),
        ("back\\\\slash", ["back\\slash"], ["backslash"]),
        ("trail\\ ", ["trail "], ["trail"]),
        ("plain.txt ", ["plain.txt"], []),
        ("lone\\", [], ["lone"]),
    ],
)
def test_pattern_syntax(statsignore, pattern, ignored, kept):
    root = statsignore(pattern + "\n", [*ignored, *kept])
    assert listed(root) == sorted([*BASE, *kept])


@pytest.mark.parametrize(
    "patterns, kept",
    [
        ("*.md\n!README.md\n", ["README.md"]),
        ("!README.md\n*.md\n", []),
        ("*.md\n!README.md\n*.md\n", []),
    ],
)
def test_last_match_wins(statsignore, patterns, kept):
    root = statsignore(patterns)
    remaining = [b for b in BASE if b not in ("README.md", "docs/guide.md")]
    assert listed(root) == sorted(remaining + kept)


@pytest.mark.parametrize(
    "patterns, kept",
    [
        ("build/\n!build/keep.txt\n", []),
        ("build/\n!build/**\n", []),
        ("build/*\n!build/keep.txt\n", ["build/keep.txt"]),
    ],
)
def test_no_reinclusion_under_ignored_parent(statsignore, patterns, kept):
    root = statsignore(patterns, ["build/keep.txt", "build/drop.txt"])
    assert listed(root) == sorted([*BASE, *kept])
