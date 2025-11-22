"""
Make the `src` directory a package so imports like `import src.core` work
when the project is installed into the environment.

This is a compatibility shim to avoid requiring `PYTHONPATH` during local
development and to allow `poetry install` to install the package without
using `--no-root`.
"""

__all__ = []
