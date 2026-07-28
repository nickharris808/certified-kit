"""``certified-kit <verb> [args...]`` — one entry point for the toolkit."""
from __future__ import annotations

import sys

from .dispatch import COMMANDS, MissingComponent, format_inventory, resolve

_USAGE = """usage: certified-kit <command> [args...]

commands:
{commands}
  list           what is installed, and at what version

Every command forwards its arguments to that component's own CLI, so
`certified-kit verify --help` is `lcert-verify --help`. certified-kit adds no
verification logic of its own; each component works standalone.
"""


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    listing = "\n".join(f"  {v:14} {COMMANDS[v][2]}" for v in sorted(COMMANDS))

    if not argv or argv[0] in ("-h", "--help", "help"):
        print(_USAGE.format(commands=listing))
        return 0
    if argv[0] in ("-V", "--version"):
        from . import __version__
        print(f"certified-kit {__version__}")
        return 0
    if argv[0] == "list":
        print(format_inventory())
        return 0

    verb, rest = argv[0], argv[1:]
    if verb not in COMMANDS:
        print(f"certified-kit: unknown command {verb!r}\n", file=sys.stderr)
        print(_USAGE.format(commands=listing), file=sys.stderr)
        return 5
    try:
        run = resolve(verb)
    except MissingComponent as exc:
        print(str(exc), file=sys.stderr)
        return 5
    return run(rest)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
