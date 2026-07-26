# Whitepaper & Foundational Documents

This directory holds the canonical source documents behind the Peace Protocols.
They are the authoritative reference for the vision, the mathematics, the agent
architecture, and the economic model. When code and docs in this repository
disagree with these documents, the documents are the source of truth for
*intent* — but always confirm the exact formula against
[`docs/math/`](../docs/math/) before implementing.

> These PDFs are tracked deliberately (see the `!whitepaper/*.pdf` rule in the
> repository `.gitignore`). Do not edit them here; they are exports of the
> upstream manuscripts.

## Contents

| File | Description |
| --- | --- |
| **Peace_Protocols.pdf** | The core whitepaper. Defines the vision of community self-reliance "without hierarchy," the 6-Dimensional operating loop (Discover → Decipher → Design → Develop → Deploy → Defend), the 7 Sovereign Bodies and 12 Resource Realms, and the two master metrics — the Peace Efficiency Index (Pe) and the Community Vitality Index (CVI). |
| **Peace_Protocols_Citations.pdf** | The citation bundle: the full reference list and supporting sources cited throughout the core whitepaper, for readers who want to trace claims back to primary literature. |
| **Peace_Protocols_Review_Comments.pdf** | Consolidated peer-review comments on the whitepaper, capturing critiques, clarifications, and the reasoning behind key design decisions. |
| **PEACE_Ecosystem_Master_Business_Plan.pdf** | The master business plan for the PEACE ecosystem: operating model, phased rollout, resourcing, and sustainability strategy for standing up communities of Peace Engineers. |
| **PEACE_Ecosystem_Executive_Teaser.pdf** | A short executive teaser summarizing the ecosystem's purpose, opportunity, and call to action for prospective partners and contributors. |
| **PEACE_Ecosystem_Org_Structure.pdf** | The organizational structure of the ecosystem — how the sovereign bodies, resource realms, and the community of 7,777 Peace Engineers relate and coordinate without hierarchy. |

## How these map to the code

- **Vision & 6D loop** → [`VISION.md`](../VISION.md), [`docs/6d-framework.md`](../docs/6d-framework.md)
- **Agents (Raven + 19 domains)** → [`AGENTS.md`](../AGENTS.md), [`agents/`](../agents/)
- **Master metrics & indexes** → [`docs/math/`](../docs/math/), [`math/`](../math/)
- **Architecture (Nostr, Tauri/Rust, block/buzz fork)** → [`ARCHITECTURE.md`](../ARCHITECTURE.md)

_Author: Raven Rolland Gregg (Keetá Yeìl of the Lukaaẋ.ádi Clan)._
