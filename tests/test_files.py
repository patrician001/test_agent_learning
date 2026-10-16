from repostats import count_by_extension, largest_files, list_files


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


def test_largest_files(sample_repo):
    assert largest_files(sample_repo) == [
        ("src/app.py", len("def main():\n    # TODO: handle errors\n    return 0\n")),
        ("README.md", len("# sample\n\nA small repository.\n")),
        ("docs/guide.md", len("Read the README.\n")),
        ("Makefile", len("check:\n\tpytest\n")),
        ("src/util.py", len("VALUE = 1\n")),
    ]
    assert [path for path, _ in largest_files(sample_repo, n=2)] == ["src/app.py", "README.md"]
    assert largest_files(sample_repo, n=0) == []
    assert largest_files(sample_repo, n=-1) == []


def test_largest_files_tie_breaks_by_path(sample_repo):
    (sample_repo / "src" / "aaa.py").write_text("VALUE = 2\n")
    result = largest_files(sample_repo, n=10)
    assert result[-2:] == [("src/aaa.py", 10), ("src/util.py", 10)]
