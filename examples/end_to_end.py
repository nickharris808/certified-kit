"""One pass through the whole toolkit: seal, build, verify, score.

Run it:  python examples/end_to_end.py
"""
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
