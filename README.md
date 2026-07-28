# certified-kit

**One install and one command for the whole toolkit.**

The portfolio has six repositories and no front desk. This is the front desk.

```bash
pip install "certified-kit @ git+https://github.com/nickharris808/certified-kit@main"
certified-kit list
```

```
  atlas    ok             1.0.0    score a verifier against the adversarial corpus
  build    ok             1.0.0    produce a certificate bundle from your own analysis
  equiv    ok             1.0.0    verify a logic-equivalence receipt or a DRAT proof
  seal     ok             1.0.0    seal acceptance criteria before you measure
  verify   ok             1.0.0    re-derive a certificate bundle's verdict
```

[![ci](https://github.com/nickharris808/certified-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/nickharris808/certified-kit/actions/workflows/ci.yml)

## 30-second quickstart

```bash
certified-kit build demo                 # produce a bundle
certified-kit verify demo $ANCHOR        # re-derive its verdict
certified-kit seal criteria.json         # fix acceptance criteria before measuring
certified-kit equiv demo                 # prove and check an equivalence
certified-kit atlas build atlas          # the adversarial corpus
```

Every verb forwards its arguments to that component's own CLI, so `certified-kit verify --help` *is*
`lcert-verify --help`. Nothing is wrapped, renamed, or reinterpreted.

## Worked example — one pass through everything

```python
import json
from pathlib import Path
from tempfile import mkdtemp

import lcert_verify as V
import prereg_seal as P
from lcert_build import Bundle

work = Path(mkdtemp())

# 1. Seal the criteria BEFORE measuring, so they cannot move afterwards.
criteria = {"junction_temperature_K": {"max": 358.15}}
seal = P.seal(criteria)
print(f"1 sealed      : {seal['digest'][:16]}…")

# 2. Your analysis runs and produces enclosures. Round them OUTWARD.
hotspots = [(340.0, 351.2), (338.4, 349.9), (344.1, 355.0)]

# 3. Package the result as a certificate anyone can re-derive.
path, anchor = (Bundle(work / "thermal")
                .preregister({"criteria": criteria, "seal": seal["digest"]})
                .bound("hotspots", quantity="junction temperature", unit="K",
                       threshold=criteria["junction_temperature_K"]["max"],
                       direction="below", loci=hotspots)
                .build())
print(f"2 built       : {anchor[:16]}…")

# 4. Be the stranger: trust nothing but the bytes and the out-of-band anchor.
res = V.verify_bundle(path, anchor)
print(f"3 verified    : {res['verdict']} ({res['n_gated_loci']} gated loci)")

# 5. The criteria in the bundle are still the ones that were sealed.
P.verify(json.loads((path / "preregistration.json").read_text())["criteria"], seal)
print("4 seal holds  : the criteria never moved")

# And without the anchor, the honest answer is an abstention.
print(f"5 no anchor   : {V.verify_bundle(path)['verdict']}")
```

```
1 sealed      : b87ca9d7a5ed1a42…
2 built       : ec84bb954a7062f1…
3 verified    : VERIFIED (3 gated loci)
4 seal holds  : the criteria never moved
5 no anchor   : UNVERIFIED
```

That is [`examples/end_to_end.py`](examples/end_to_end.py) verbatim; a test runs it and checks
this output, so it cannot rot. The digests are deterministic — run it twice and get the same bytes.

## A note on the name

The obvious name, `certkit`, is taken on this account by an unrelated project, and its CLI would
collide. So the package and the command are both `certified-kit`. Nothing else about it changed.

## What certified-kit is not

**It adds no verification logic.** Not a line. Everything it can tell you comes from a package
that installs, runs, and can be audited without it. That is on purpose: a meta-package that
started making its own judgements would be a new thing to trust, which is the opposite of the
point.

**It does not paper over a missing component.** If `lcert-build` is absent, `certified-kit build` says
so and gives the install line. It never behaves as though a check ran.

```
$ certified-kit build demo
`certified-kit build` needs lcert-build, which is not installed.
    pip install "lcert-build @ git+https://github.com/nickharris808/lcert-build@main"
```

## The components

| verb | package | what it does |
|---|---|---|
| `verify` | [lcert-verify](https://github.com/nickharris808/lcert-verify) | re-derive a certificate bundle's verdict |
| `build` | [lcert-build](https://github.com/nickharris808/lcert-build) | produce one from your own analysis |
| `equiv` | [equiv-receipt](https://github.com/nickharris808/equiv-receipt) | logic equivalence, combinational and sequential |
| `seal` | [prereg-seal](https://github.com/nickharris808/prereg-seal) | fix acceptance criteria before measuring |
| `atlas` | [cert-atlas](https://github.com/nickharris808/cert-atlas) | score a verifier against forgeries |

## Licence

Apache-2.0.

---

One idea, six pieces: **a recorded verdict is a claim to be checked, never an input to be trusted.**

The whole story, and the objections answered, live at
**[certified-oss](https://github.com/nickharris808/certified-oss)**.
