"""certified-kit — one install and one command for the whole verification toolkit.

The portfolio had six front doors and no lobby. This is the lobby: it pulls in
every package and dispatches to each one's CLI, so `verify`, `build`, `equiv`,
`seal` and `atlas` all work from a single `pip install`.

It deliberately adds no verification logic of its own. Everything it can tell you
comes from a package that can be installed and audited without it, and
:func:`inventory` reports exactly which of them are present — a missing one is
named, never silently skipped.
"""
from .dispatch import COMMANDS, MissingComponent, inventory, resolve  # noqa: F401

__version__ = "1.0.0"
__all__ = ["COMMANDS", "MissingComponent", "inventory", "resolve", "__version__"]
