# repostats

Small statistics about the files in a repository checkout: which files there are and how many of each kind.

```python
from repostats import list_files, count_by_extension

list_files(".")          # ['README.md', 'repostats/__init__.py', ...]
count_by_extension(".")  # {'.md': 3, '.py': 4, ...}
```

From the command line:

```
python -m repostats ROOT           # one relative path per line
python -m repostats --counts ROOT  # file counts per extension, as JSON
```

A ROOT that is not a directory prints an error to stderr and exits with status 2.

Python 3.12, no runtime dependencies. See CONTRIBUTING.md before changing anything.
