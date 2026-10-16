from repostats import count_by_extension, find_todos, list_files


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


def test_find_todos_baseline(sample_repo):
    assert find_todos(sample_repo) == [("src/app.py", 2, "# TODO: handle errors")]


def test_find_todos_order_and_skips(sample_repo):
    (sample_repo / "a").mkdir()
    (sample_repo / "a/z.txt").write_text("TODO one\n\n   TODO two  \n")
    (sample_repo / "b.txt").write_text("TODO b\n")
    (sample_repo / ".git/hooks").mkdir()
    (sample_repo / ".git/hooks/x").write_text("TODO hidden\n")
    (sample_repo / "bin.dat").write_bytes(b"TODO \xff\xfe\n")
    assert find_todos(sample_repo) == [
        ("a/z.txt", 1, "TODO one"),
        ("a/z.txt", 3, "TODO two"),
        ("b.txt", 1, "TODO b"),
        ("src/app.py", 2, "# TODO: handle errors"),
    ]


def test_find_todos_word_boundary(sample_repo):
    (sample_repo / "w.txt").write_text("TODOS\ntodo\nMYTODO\n# TODO(bob)\n")
    got = [t for t in find_todos(sample_repo) if t[0] == "w.txt"]
    assert got == [("w.txt", 4, "# TODO(bob)")]


def test_find_todos_line_splitting(sample_repo):
    (sample_repo / "f.txt").write_bytes(b"a\x0cb\nTODO\n")
    (sample_repo / "empty.txt").write_bytes(b"")
    (sample_repo / "nonl.txt").write_bytes(b"x\nTODO end")
    (sample_repo / "crlf.txt").write_bytes(b"TODO crlf\r\n")
    got = [t for t in find_todos(sample_repo) if t[0] != "src/app.py"]
    assert got == [
        ("crlf.txt", 1, "TODO crlf"),
        ("f.txt", 2, "TODO"),
        ("nonl.txt", 2, "TODO end"),
    ]
