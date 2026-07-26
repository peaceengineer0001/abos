# 🤝 Contributing to the Peace Protocols Raven Network

Thank you for helping build sovereignty infrastructure. Contribution to the Raven Network is aligned with the Peace Protocols' **7,777 deployment model**: a non-hierarchical network of Peace Engineers who each own their node, share their gains, and teach the next cohort.

This document explains **how** to contribute and **the philosophy** that guides what we accept.

---

## 🌱 Contribution Philosophy — Regeneration Over Extraction

Every contribution should leave the commons richer than it found it. We evaluate proposals against three questions drawn directly from the Peace Protocols:

1. **Does it preserve sovereignty?** Contributions must never create a chokepoint, a mandatory cloud dependency, or a mechanism that moves raw user data off-device without explicit consent.
2. **Does it increase reciprocity?** Prefer changes that make it easier for one node to help another (shared workflows, open calculators, documentation) over changes that benefit only a single deployment.
3. **Is it regenerative?** Prefer additive, forkable, well-documented contributions over clever-but-opaque ones. If the next Peace Engineer can't read it, run it, and teach it, it isn't done.

---

## 🧭 What You Can Contribute

| Type | Examples | Where |
|---|---|---|
| **Agent content** | Improved system prompts, better intake questions, new scope adaptations | [`agents/`](agents/) |
| **Math** | New/refined index calculators, tests, Rust ports | [`math/`](math/) |
| **Workflows** | New 6D or coherence-shock workflows | [`workflows/`](workflows/) |
| **Docs** | Tutorials, translations, math explainers | [`docs/`](docs/) |
| **Config** | New LLM provider recipes, privacy-tier presets | [`config/`](config/) |
| **Bug reports** | Reproducible issues with logs and scope context | GitHub Issues |

> **Note:** We do **not** modify Buzz source here. Buzz is a submodule. Improvements to Buzz itself belong upstream at [block/buzz](https://github.com/block/buzz).

---

## 🔧 Development Setup

```bash
# Clone with the Buzz submodule
git clone --recurse-submodules https://github.com/peaceengineer0001/peace-protocols.git
cd peace-protocols

# Run setup
./scripts/setup.sh

# Run the math test suite before you start
./scripts/run-math-tests.sh
```

Prerequisites and a full walkthrough live in [docs/getting-started.md](docs/getting-started.md).

---

## 🧪 Standards & Checks

- **Python calculators** must include docstrings, type hints, input validation, and a `__main__` self-test block. Run `./scripts/run-math-tests.sh` and ensure everything passes.
- **Agent prompts** (`system_prompt.md`) should be 300–500 words, encode the agent's Peace Protocol index correctly, and follow the 6D loop structure.
- **Config files** must be valid TOML/YAML and include explanatory comments for every non-obvious option.
- **Formulas** must match the Peace Protocols whitepaper exactly. When in doubt, cite the section in your PR description.
- **Docs** use clear headings, working relative links, and inclusive language.

---

## 🔀 Pull Request Workflow

1. **Fork** the repo and create a feature branch: `git checkout -b feature/<short-name>`.
2. **Make focused changes.** One logical change per PR. Keep the overlay auditable.
3. **Test locally.** Run the math tests; if you touched an agent, validate its config loads.
4. **Write a clear PR description.** State what changed, why, and which Peace Protocol section/formula it references.
5. **Sign your commits** where possible. All work is Apache-2.0 licensed.
6. **Open the PR** against `main`. A maintainer (a fellow Peace Engineer) reviews against the three philosophy questions above.

We favor small, well-documented PRs that a reviewer can fully understand in one sitting.

---

## 📜 Licensing of Contributions

By contributing, you agree that your contributions are licensed under the **Apache License 2.0** (see [LICENSE](LICENSE)), the same license as the project and as Buzz. Do not submit code you do not have the right to license this way.

---

## 💬 Community

Discussion happens in the open, on Nostr and in the project's channels. Be excellent to one another — see our [Code of Conduct](CODE_OF_CONDUCT.md): **respect, reciprocity, regeneration.**

*Every node you help stand up is one of the 7,777. Thank you for engineering peace.*
