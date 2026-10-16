from repostats import count_by_extension, count_lines, list_files


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


def test_count_lines(sample_repo):
    assert count_lines(sample_repo) == {"": 2, ".md": 4, ".py": 4}


def test_count_lines_skips_invalid_utf8(sample_repo):
    (sample_repo / "bad.py").write_bytes(b"\xff\xfe\n")
    assert count_lines(sample_repo) == {"": 2, ".md": 4, ".py": 4}


def test_count_lines_unterminated_and_empty(sample_repo):
    (sample_repo / "no_newline.txt").write_text("a\nb")
    (sample_repo / "empty.txt").write_text("")
    result = count_lines(sample_repo)
    assert result[".txt"] == 2
    assert list(result) == sorted(result)
