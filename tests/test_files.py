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
    result = count_lines(sample_repo)
    assert result == {"": 2, ".md": 4, ".py": 4}
    assert list(result) == sorted(result)


def test_count_lines_skips_invalid_utf8(sample_repo):
    baseline = count_lines(sample_repo)
    (sample_repo / "logo.png").write_bytes(b"\xff\xfe\x00")
    (sample_repo / "bad.py").write_bytes(b"x = 1\n\xff\n")
    assert count_lines(sample_repo) == baseline


def test_count_lines_final_line_without_newline_and_empty_file(sample_repo):
    (sample_repo / "notes.txt").write_text("a\nb")
    (sample_repo / "empty.txt").write_text("")
    result = count_lines(sample_repo)
    assert result[".txt"] == 2
    (sample_repo / "notes.txt").unlink()
    assert count_lines(sample_repo)[".txt"] == 0
