# CLI reference — `certified-kit`

**The command listings below are generated.** Run `python gen_cli_docs.py` after changing any
argument; a test fails if they are stale.

## Top level

```
usage: certified-kit <command> [args...]

commands:
  atlas          score a verifier against the adversarial corpus
  build          produce a certificate bundle from your own analysis
  equiv          verify a logic-equivalence receipt or a DRAT proof
  seal           seal acceptance criteria before you measure
  verify         re-derive a certificate bundle's verdict
  list           what is installed, and at what version

Every command forwards its arguments to that component's own CLI, so
`certified-kit verify --help` is `lcert-verify --help`. certified-kit adds no
verification logic of its own; each component works standalone.
```

## Exit codes

Every command in this toolkit uses the same taxonomy, so a caller can branch on it:

| Code | Meaning |
|---|---|
| `0` | verified / sealed / equivalent — the check was made and it stood |
| `1` | refuted by re-derivation |
| `2` | refuted on integrity: fingerprint, manifest, root, commitment |
| `3` | vacuous — nothing was certified |
| `4` | **abstained** — the evidence for an assertion is absent |
| `5` | usage error — not a verdict at all |

`4` is the one worth wiring up. It is not a failure of the artifact; it means nothing was
established, and treating it as a pass is the failure this toolkit exists to prevent.

---

*Part of [certified-oss](https://github.com/nickharris808/certified-oss).*
