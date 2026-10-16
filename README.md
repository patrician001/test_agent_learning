# repostats

Small statistics about the files in a repository checkout: which files there are and how many of each kind.

```python
from repostats import list_files, count_by_extension

list_files(".")          # ['README.md', 'repostats/__init__.py', ...]
count_by_extension(".")  # {'.md': 3, '.py': 4, ...}
```

Paths matched by a `.statsignore` file at the root (gitignore-style patterns, one per line) are skipped.

Python 3.12, no runtime dependencies. See CONTRIBUTING.md before changing anything.
