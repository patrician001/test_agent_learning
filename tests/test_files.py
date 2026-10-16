from conftest import SAMPLE_FILES

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


def sample_sizes():
    return {
        name: len(text.encode())
        for name, text in SAMPLE_FILES.items()
        if not name.startswith(".git/")
    }


def test_largest_files_top_n(sample_repo):
    expected = sorted(sample_sizes().items(), key=lambda item: (-item[1], item[0]))
    assert largest_files(sample_repo, 2) == expected[:2]


def test_largest_files_ties_broken_by_path(sample_repo):
    (sample_repo / "zzz.txt").write_text("x" * 1000)
    (sample_repo / "aaa.txt").write_text("y" * 1000)
    assert largest_files(sample_repo, 3)[:2] == [("aaa.txt", 1000), ("zzz.txt", 1000)]


def test_largest_files_n_out_of_range(sample_repo):
    assert len(largest_files(sample_repo, 100)) == 5
    assert largest_files(sample_repo, 0) == []
    assert largest_files(sample_repo, -1) == []


def test_largest_files_skips_git(sample_repo):
    (sample_repo / ".git" / "huge").write_text("x" * 10_000)
    assert all(not path.startswith(".git") for path, _ in largest_files(sample_repo, 100))
