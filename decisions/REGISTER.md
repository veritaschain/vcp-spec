# VCP change-proposal register

Procedure: [VCP-PROC-001](../CHANGE-CONTROL.md) (interim). "Adopted" has the meaning in §7 of that procedure: an accepted decision record is merged.

The entries below are proposed initial assignments. They take effect with VCP-DR-2026-001. Until then, every listed document keeps its current status: **unadopted**.

| ID | Title | Source | Proposed class | Status | Decision record |
|---|---|---|---|---|---|
| VCP-CP-2026-001 | Interim change-control procedure | [CHANGE-CONTROL.md](../CHANGE-CONTROL.md) | M | Public review in [#26](https://github.com/veritaschain/vcp-spec/issues/26), closes no earlier than 2026-12-08 04:00 UTC | [VCP-DR-2026-001](VCP-DR-2026-001.md) (pending) |
| VCP-CP-2026-002 | Normative precedence: annex, normative text, JSON Schema, examples, translations | [proposals/precedence-2026-11-08/](../proposals/precedence-2026-11-08/README.md) | P | Public review in [#27](https://github.com/veritaschain/vcp-spec/issues/27), closes no earlier than 2026-11-22 04:00 UTC; decision waits for DR-2026-001 | — |
| VCP-CP-2026-003 | Integrity-layer technical errata notices (Merkle construction, AnchorRecord coverage, exact numbers) | [technical-errata-draft.md](../proposals/integrity-2026-10-24/technical-errata-draft.md), PR #3 | P / S | Draft | — |
| VCP-CP-2026-004 | Integrity byte contract and migration | [normative-change-draft.md](../proposals/integrity-2026-10-24/normative-change-draft.md), PR #4 | X (with separable M parts) | Draft | — |
| VCP-CP-2026-005 | Numeric-field inventory | [proposals/numeric-fields-2026-10-25/](../proposals/numeric-fields-2026-10-25/) | input to CP-2026-004 | Draft | — |
| VCP-CP-2026-006 | Native field layout and migration | [proposals/native-layout-migration-2026-10-25/](../proposals/native-layout-migration-2026-10-25/) | M / X | Draft | — |
| VCP-CP-2026-007 | VCP v1.2.1 errata scope (triage of the v1.2 known issues) | [triage draft](../proposals/v1.2.1-errata-triage-2026-11-10/README.md) | P scope proposed; byte/schema changes require separate M/X classification | Draft; no public review opened | — |

## Notes

- **Concurrent reviews.** Reviews of CP-2026-002 and later may open while CP-2026-001 is under review. Decisions on them are recorded only after VCP-DR-2026-001 accepts the procedure. A review opened under the proposed text restarts if the accepted procedure changes its class or period.
- **CP-2026-002 goes first.** Its outcome decides whether the Merkle example corrections in CP-2026-003 are class P (example corrected to match "MUST follow RFC 6962") or class M (new tree-scheme identifier).
- **CP-2026-003 is marked P / S** because the Merkle and AnchorRecord findings describe ways a verifier may accept a modified batch count. Those findings are already public, so they are reviewed in public (VCP-PROC-001 §6.3).
- **Splitting CP-2026-004.** Under specification §1.3 (Semantic Versioning 2.0.0), the AnchorRecord statement signature can ship as an addition (M). The event-commitment preimage and decimal-string numbers change hash inputs and wire types (X). The Editor may split CP-2026-004 accordingly when review opens.
