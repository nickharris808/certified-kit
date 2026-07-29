# Tutorial — certified-kit

One install and one command for the whole toolkit.

```bash
pip install "certified-kit @ git+https://github.com/nickharris808/certified-kit.git@main"
certified-kit list
```

Every verb forwards its arguments to that component's own CLI, so
`certified-kit verify --help` *is* `lcert-verify --help`. Nothing is wrapped, renamed or
reinterpreted, and exit codes pass through unchanged — an abstention is still `4`.

| verb | package |
|---|---|
| `verify` | [lcert-verify](https://github.com/nickharris808/lcert-verify) |
| `build` | [lcert-build](https://github.com/nickharris808/lcert-build) |
| `equiv` | [equiv-receipt](https://github.com/nickharris808/equiv-receipt) |
| `seal` | [prereg-seal](https://github.com/nickharris808/prereg-seal) |
| `atlas` | [cert-atlas](https://github.com/nickharris808/cert-atlas) |

## One pass through everything

[`examples/end_to_end.py`](examples/end_to_end.py) seals criteria, builds a certificate, verifies
it as a stranger, and checks the seal still holds. The test suite runs it and checks its output
against the README, so it cannot rot.

## What it will not do

**It adds no verification logic.** Not a line — `test_it_contains_no_verification_logic` asserts
it. A meta-package that started making its own judgements would be a new thing to trust, which is
the opposite of the point.

**It does not paper over a missing component.** If `lcert-build` is absent, `certified-kit build`
says so and gives the install line. It never behaves as though a check ran.

---

*For the story, start at [certified-oss](https://github.com/nickharris808/certified-oss).*
