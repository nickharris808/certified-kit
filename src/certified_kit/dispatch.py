"""Dispatch to each component's own CLI, and report honestly on what is missing."""
from __future__ import annotations

import importlib
from typing import Dict, List, Optional, Tuple

#: verb -> (distribution name, module holding `main`, one-line description)
COMMANDS: Dict[str, Tuple[str, str, str]] = {
    "verify": ("lcert-verify", "lcert_verify.cli",
               "re-derive a certificate bundle's verdict"),
    "build": ("lcert-build", "lcert_build.cli",
              "produce a certificate bundle from your own analysis"),
    "equiv": ("equiv-receipt", "equiv_receipt.cli",
              "verify a logic-equivalence receipt or a DRAT proof"),
    "seal": ("prereg-seal", "prereg_seal.cli",
             "seal acceptance criteria before you measure"),
    "atlas": ("cert-atlas", "cert_atlas.cli",
              "score a verifier against the adversarial corpus"),
}


class MissingComponent(RuntimeError):
    """A component is not installed. Named, never silently skipped."""


def resolve(verb: str):
    """Return the ``main`` of the component that handles ``verb``."""
    if verb not in COMMANDS:
        raise KeyError(verb)
    dist, module, _ = COMMANDS[verb]
    try:
        return importlib.import_module(module).main
    except ImportError as exc:
        raise MissingComponent(
            f"`certified-kit {verb}` needs {dist}, which is not installed.\n"
            f"    pip install \"{dist} @ git+https://github.com/nickharris808/{dist}@main\"\n"
            f"  (installing certified-kit itself pulls in every component; this usually "
            f"means a partial environment.)") from exc


def inventory() -> List[Dict]:
    """What is installed, and at what version. A missing component is reported."""
    out = []
    for verb, (dist, module, desc) in sorted(COMMANDS.items()):
        row = {"verb": verb, "distribution": dist, "description": desc,
               "installed": False, "version": ""}
        try:
            mod = importlib.import_module(module.split(".")[0])
            row["installed"] = True
            row["version"] = getattr(mod, "__version__", "?")
        except ImportError:
            pass
        out.append(row)
    return out


def format_inventory(rows: Optional[List[Dict]] = None) -> str:
    rows = rows if rows is not None else inventory()
    lines = []
    for r in rows:
        mark = "ok " if r["installed"] else "NOT INSTALLED"
        lines.append(f"  {r['verb']:8} {mark:14} {r['version']:8} {r['description']}")
    missing = [r for r in rows if not r["installed"]]
    if missing:
        lines.append("")
        lines.append(f"  {len(missing)} component(s) missing. "
                     f"`certified-kit <verb>` will say which and how to install it, "
                     f"rather than behaving as if the check had passed.")
    return "\n".join(lines)
