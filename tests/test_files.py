import pytest

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
    assert largest_files(sample_repo, 3) == [
        ("src/app.py", 51),
        ("README.md", 30),
        ("docs/guide.md", 17),
    ]


def test_largest_files_default_skips_git(sample_repo):
    result = largest_files(sample_repo)
    assert len(result) == 5
    assert all(not path.startswith(".git") for path, _ in result)


def test_largest_files_n_bounds(sample_repo):
    assert len(largest_files(sample_repo, 100)) == 5
    for bad in (0, -2):
        with pytest.raises(ValueError, match="n must be at least 1"):
            largest_files(sample_repo, bad)


def test_largest_files_ties_by_path(sample_repo):
    (sample_repo / "z.txt").write_text("x" * 100)
    (sample_repo / "a.txt").write_text("x" * 100)
    assert largest_files(sample_repo, 2) == [("a.txt", 100), ("z.txt", 100)]
