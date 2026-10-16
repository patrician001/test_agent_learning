"""CI checks for two of the four conventions in CONTRIBUTING.md: doctests and no dependencies."""

import importlib
import inspect
import pkgutil
import tomllib
from pathlib import Path

import repostats

ROOT = Path(__file__).resolve().parent.parent


def public_functions():
    for info in pkgutil.walk_packages(repostats.__path__, "repostats."):
        module = importlib.import_module(info.name)
        for name, fn in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith("_") and fn.__module__ == module.__name__:
                yield f"{module.__name__}.{name}", fn


def test_every_public_function_has_a_doctest():
    missing = [name for name, fn in public_functions() if ">>>" not in (fn.__doc__ or "")]
    assert missing == [], f"public functions without a doctest: {missing}"


def test_no_dependencies():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert project.get("dependencies", []) == [], "CONTRIBUTING.md rule 4: no new dependencies"
    assert "optional-dependencies" not in project, "CONTRIBUTING.md rule 4: no new dependencies"
