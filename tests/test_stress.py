"""The adversarial suite for certified-kit.

Oracle: the dispatcher must never turn a component's answer into a different one,
and must never behave as though a check ran when it did not.
"""
from __future__ import annotations

import os
import subprocess
import sys

import pytest

from certified_kit.dispatch import COMMANDS, MissingComponent, format_inventory, resolve


def _cli(args, env=None):
    return subprocess.run([sys.executable, "-m", "certified_kit.cli", *args],
                          capture_output=True, text=True, env=env or dict(os.environ))


# ============================================================ 1. MALFORMED INPUT

HOSTILE_ARGV = [
    [], [""], [" "], ["\n"], ["--"], ["-"], ["---"], ["verify" * 100],
    ["\x00"], ["../verify"], ["VERIFY"], ["Verify"], ["verify\n"], ["ver ify"],
    ["-h", "extra"], ["--version", "extra"],
]


@pytest.mark.parametrize("argv", HOSTILE_ARGV, ids=[repr(a)[:20] for a in HOSTILE_ARGV])
def test_no_argv_produces_a_confident_success_it_did_not_earn(argv, capsys):
    """In-process: a NUL byte cannot survive `subprocess`, so this calls main()."""
    from certified_kit.cli import main
    code = main(list(argv))                        # must not raise
    out = capsys.readouterr().out
    if code == 0:
        # The only zero-exit paths are help, version and list — each of which
        # says what it is rather than implying a check happened.
        assert any(w in out for w in ("usage:", "certified-kit ", "ok ",
                                      "NOT INSTALLED")), (argv, out[:200])
    else:
        assert code == 5, argv                     # usage error, never a verdict code


def test_an_unknown_verb_is_a_usage_error_not_a_verdict():
    r = _cli(["definitely-not-a-verb"])
    assert r.returncode == 5
    assert "unknown command" in r.stderr


def test_a_verb_that_is_a_prefix_of_a_real_one_is_not_guessed():
    """`ver` is not `verify`. Guessing would run a check the caller did not ask for."""
    for partial in ("ver", "veri", "bui", "atl", "sea"):
        r = _cli([partial])
        assert r.returncode == 5, partial
        assert "unknown command" in r.stderr


# ============================================================ 2. PASS-THROUGH

def test_arguments_are_forwarded_byte_for_byte():
    a = _cli(["verify", "--scope"])
    b = subprocess.run([sys.executable, "-m", "lcert_verify.cli", "--scope"],
                       capture_output=True, text=True)
    assert a.returncode == b.returncode
    assert a.stdout == b.stdout


@pytest.mark.parametrize("expected", [0, 4])
def test_component_exit_codes_survive_the_wrapper(tmp_path, expected):
    """An abstention is 4 through the wrapper, or every CI integration breaks."""
    import lcert_verify as L
    cert = L.interval_bound_cert("t", quantity="q", unit="u", threshold=1.0,
                                 direction="below", loci=[(0.0, 0.5)])
    L.make_bundle(tmp_path, interval_bound_certs=[cert], kpis=[], prereg={})
    args = ["verify", str(tmp_path)]
    if expected == 0:
        args.append(L.bundle_fingerprint(tmp_path))
    assert _cli(args).returncode == expected


def test_a_hostile_argument_is_passed_through_not_interpreted(tmp_path):
    """The wrapper must not parse arguments meant for the component."""
    r = _cli(["verify", "--definitely-not-a-flag"])
    assert r.returncode != 0
    # argparse in lcert-verify owns that error, not certified-kit
    assert "unknown command" not in r.stderr


# ============================================================ 3. MISSING COMPONENTS

def test_a_missing_component_is_named_and_never_silently_skipped(monkeypatch):
    import importlib
    real = importlib.import_module

    def fake(name, *a, **kw):
        if name.startswith("lcert_build"):
            raise ImportError("no module named lcert_build")
        return real(name, *a, **kw)

    monkeypatch.setattr(importlib, "import_module", fake)
    with pytest.raises(MissingComponent) as exc:
        resolve("build")
    assert "lcert-build" in str(exc.value) and "pip install" in str(exc.value)


def test_the_inventory_never_claims_a_missing_component_is_present():
    from certified_kit.dispatch import inventory
    rows = inventory()
    rows[0] = dict(rows[0], installed=False, version="")
    text = format_inventory(rows)
    assert "NOT INSTALLED" in text
    assert "rather than behaving as if the check had passed" in text


def test_every_verb_in_the_table_actually_resolves():
    for verb in COMMANDS:
        assert callable(resolve(verb)), verb


# ============================================================ 4. THE BOUNDARY

def test_the_dispatcher_contains_no_verification_logic():
    """A lobby, not a new thing to trust."""
    import ast
    from pathlib import Path

    import certified_kit
    banned_names = {"verify_bundle", "forward_rup_check", "rederive_gate_verdict",
                    "merkle_root", "digest", "canon", "check"}
    banned_imports = {"hashlib", "hmac", "secrets", "base64"}
    for py in Path(certified_kit.__file__).parent.glob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                assert node.name not in banned_names, f"{py.name}: {node.name}"
            if isinstance(node, ast.Import):
                for n in node.names:
                    assert n.name.split(".")[0] not in banned_imports, \
                        f"{py.name}: {n.name}"
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in banned_imports, \
                    f"{py.name}: {node.module}"


def test_the_command_table_is_the_only_dispatch():
    """There is nowhere else for logic to hide."""
    from pathlib import Path

    import certified_kit
    src = (Path(certified_kit.__file__).parent / "dispatch.py").read_text()
    assert "COMMANDS[verb]" in src
    assert src.count("import_module") <= 2


# ============================================================ 5. DETERMINISM

def test_listing_twice_gives_the_same_answer():
    a, b = _cli(["list"]), _cli(["list"])
    assert a.stdout == b.stdout and a.returncode == b.returncode


def test_help_does_not_depend_on_what_is_installed():
    """Help is a description of the interface, not a report on the environment."""
    r = _cli(["--help"])
    for verb in COMMANDS:
        assert verb in r.stdout
