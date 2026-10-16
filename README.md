# repostats

Small statistics about the files in a repository checkout: which files there are and how many of each kind.

```python
from repostats import list_files, count_by_extension, largest_files

list_files(".")          # ['README.md', 'repostats/__init__.py', ...]
largest_files(".", 3)  # [('path', size_in_bytes), ...]
count_by_extension(".")  # {'.md': 3, '.py': 4, ...}
```

Python 3.12, no runtime dependencies. See CONTRIBUTING.md before changing anything.
