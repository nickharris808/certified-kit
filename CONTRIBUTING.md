# Contributing to certified-kit

This package is part of [certified-oss][p]. **The portfolio-wide guide is
[CONTRIBUTING.md][c] and it is the one to read** — it covers the rules that are not negotiable,
how to install packages that depend on each other, and what kind of contribution is most wanted
(a forgery this project fails to catch).

What is specific to this package:

- **This package contains no verification logic.** `test_it_contains_no_verification_logic` asserts
  it, down to refusing an import of `hashlib`. It is a lobby, not a new thing to trust.
- **Exit codes pass through unchanged.** A wrapper that flattened them would break every CI
  integration downstream.

## Working on it

```bash
pip install -e ".[test]"
pytest -q
ruff check .
```

## Licence

Apache-2.0. By contributing you agree your contribution is licensed the same way.

[p]: https://github.com/nickharris808/certified-oss
[c]: https://github.com/nickharris808/certified-oss/blob/main/CONTRIBUTING.md
