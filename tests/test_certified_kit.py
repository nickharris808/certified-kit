"""certified-kit: a lobby, not a new thing to trust.

Two properties. It contains no verification logic, and it never behaves as
though a check ran when the component that would run it is absent.
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

import certified_kit
from certified_kit.dispatch import COMMANDS, MissingComponent, format_inventory, inventory, resolve


def _cli(args, env=None):
    return subprocess.run([sys.executable, "-m", "certified_kit.cli", *args],
                          capture_output=True, text=True, env=env)


# ---------------------------------------------------------------- dispatch

def test_every_verb_resolves_to_a_real_main():
    for verb in COMMANDS:
        assert callable(resolve(verb)), verb


def test_an_unknown_verb_is_a_usage_error_not_a_verdict():
    r = _cli(["definitely-not-a-verb"])
    assert r.returncode == 5
    assert "unknown command" in r.stderr


def test_help_lists_every_command():
    r = _cli(["--help"])
    assert r.returncode == 0
    for verb in COMMANDS:
        assert verb in r.stdout


def test_arguments_are_forwarded_verbatim():
    """`certified-kit verify --scope` must be `lcert-verify --scope`."""
    a = _cli(["verify", "--scope"])
    b = subprocess.run([sys.executable, "-m", "lcert_verify.cli", "--scope"],
                       capture_output=True, text=True)
    assert a.returncode == b.returncode
    assert a.stdout == b.stdout


def test_the_exit_code_of_the_component_survives(tmp_path):
    """An abstention must still be exit 4 through the wrapper."""
    import lcert_verify as L
    cert = L.interval_bound_cert("t", quantity="q", unit="u", threshold=1.0,
                                 direction="below", loci=[(0.0, 0.5)])
    L.make_bundle(tmp_path, interval_bound_certs=[cert], kpis=[], prereg={})
    assert _cli(["verify", str(tmp_path)]).returncode == 4
    assert _cli(["verify", str(tmp_path), L.bundle_fingerprint(tmp_path)]).returncode == 0


# ---------------------------------------------------------------- honesty

def test_inventory_reports_what_is_installed():
    rows = inventory()
    assert {r["verb"] for r in rows} == set(COMMANDS)
    assert all(r["installed"] for r in rows), "the test environment is incomplete"
    assert all(r["version"] for r in rows)


def test_a_missing_component_is_named_with_its_install_line(monkeypatch):
    import importlib

    real = importlib.import_module

    def fake(name, *a, **kw):
        if name == "lcert_build.cli":
            raise ImportError("no module named lcert_build")
        return real(name, *a, **kw)

    monkeypatch.setattr(importlib, "import_module", fake)
    with pytest.raises(MissingComponent) as exc:
        resolve("build")
    assert "lcert-build" in str(exc.value)
    assert "pip install" in str(exc.value)


def test_the_inventory_says_when_something_is_missing():
    rows = inventory()
    rows[0] = dict(rows[0], installed=False, version="")
    text = format_inventory(rows)
    assert "NOT INSTALLED" in text
    assert "rather than behaving as if the check had passed" in text


# ---------------------------------------------------------------- the boundary

def test_it_contains_no_verification_logic():
    """A meta-package that made its own judgements would be a new thing to trust."""
    src = Path(certified_kit.__file__).parent
    banned = {"verify_bundle", "forward_rup_check", "rederive_gate_verdict",
              "merkle_root", "sha256", "digest", "canon"}
    for py in src.glob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                assert node.name not in banned, f"{py.name} defines {node.name}"
            if isinstance(node, ast.Import):
                for n in node.names:
                    assert n.name.split(".")[0] not in ("hashlib", "hmac"), \
                        f"{py.name} imports {n.name}"


def test_it_only_ever_calls_a_components_main():
    """Dispatch is a lookup into COMMANDS; there is nowhere else for logic to hide."""
    src = (Path(certified_kit.__file__).parent / "dispatch.py").read_text()
    assert src.count("import_module") <= 2
    assert "COMMANDS[verb]" in src


# ---------------------------------------------------------------- the example

def test_the_readme_example_runs_and_prints_what_the_readme_says():
    root = Path(__file__).resolve().parents[1]
    r = subprocess.run([sys.executable, str(root / "examples" / "end_to_end.py")],
                       capture_output=True, text=True, cwd=root,
                       env=dict(os.environ))
    assert r.returncode == 0, r.stderr
    readme = (root / "README.md").read_text()
    for line in r.stdout.strip().splitlines():
        assert line in readme, f"README does not show: {line!r}"


def test_the_example_is_deterministic():
    root = Path(__file__).resolve().parents[1]
    runs = {subprocess.run([sys.executable, str(root / "examples" / "end_to_end.py")],
                           capture_output=True, text=True, cwd=root).stdout
            for _ in range(2)}
    assert len(runs) == 1, "the same inputs must give the same digests"


def test_the_readme_shows_the_example_verbatim():
    root = Path(__file__).resolve().parents[1]
    body = (root / "examples" / "end_to_end.py").read_text().split('"""\n', 2)[-1].strip()
    assert body in (root / "README.md").read_text()
