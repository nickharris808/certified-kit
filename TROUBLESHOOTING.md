# Troubleshooting — certified-kit

## `certified-kit <verb>` says a component is not installed

Exactly what it means, and the message carries the install line. Installing `certified-kit` itself
pulls in every component, so this usually indicates a partial environment — a `--no-deps` install,
or a virtualenv that lost a package.

`certified-kit list` shows what is present and at what version.

## `ResolutionImpossible` when installing

Two packages pinning the same dependency with URLs that differ at all — even by a `.git` — are two
sources for one name as far as pip is concerned. Every direct reference must be exactly
`git+https://github.com/nickharris808/<name>.git@main`.

## The command is `certified-kit`, not `certkit`

`certkit` is taken on this account by an unrelated project, and its CLI would collide. Nothing else
about the package changed.

## An exit code looks wrong

It is the component's. `certified-kit verify` returns whatever `lcert-verify` returns, including
`4` for an abstention. That is deliberate — a wrapper that flattened exit codes would break every
CI integration downstream.

---

*Still stuck? Open an issue with `certified-kit list` output.*
