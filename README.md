# repostats

Small statistics about the files in a repository checkout: which files there are and how many of each kind.

```python
from repostats import list_files, count_by_extension, count_lines

list_files(".")          # ['README.md', 'repostats/__init__.py', ...]
count_by_extension(".")  # {'.md': 3, '.py': 4, ...}
count_lines(".")        # {'': 2, '.md': 40, ...}
```

Python 3.12, no runtime dependencies. See CONTRIBUTING.md before changing anything.
