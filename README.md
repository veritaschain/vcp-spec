![VCP Version](https://img.shields.io/badge/VCP-v1.2%20Production%20Ready-blue)
![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-green)

# VeritasChain Protocol (VCP)

**VeritasChain Protocol (VCP)** is an open, vendor-neutral standard for
**cryptographically verifiable audit trails** in algorithmic and AI-driven
trading systems.

VCP enables regulators, auditors, and market participants to
**verify — not merely trust —** the integrity, completeness (at anchor
granularity), and ordering of recorded trading decisions, orders, executions,
and risk controls.

VCP is the finance profile of the
[Verifiable AI Provenance Framework (VAP)](https://github.com/veritaschain/vap-spec)
and its first implementation profile. [VAP v1.2 alignment remains under review](https://github.com/veritaschain/vap-spec/blob/0f8a2faa2cd50c296c90974476f4b6ecf169c163/spec/v1.2/VAP_Framework_Specification.md); full conformance has not been established. Within the VAP family, the designation
"Protocol" is reserved for VCP, which defines an actual wire protocol.

This repository is maintained by the
**VeritasChain Standards Organization (VSO)**.

### Implementation status (mandatory disclosure)

As of September 2026: **zero external implementations** of VCP or any other VAP
profile, and **zero Evidence Packs accepted in any proceeding**.

**Commercial disclosure correction — 24 October 2026:** the previously published paid-service contract figure and associated commercial details have not been substantiated through reconciliation with primary records. The claim is withdrawn pending verification; this does **not** establish a count of zero. No verified contract count, customer count or revenue figure is asserted here. Commercial activity is separate from external implementation, independent validation and Evidence Pack acceptance. See the [dated correction and counting criteria](https://github.com/veritaschain/vap-spec/blob/main/disclosures/2026-10-24-commercial-contracts.md). Fixed distributions and historical evidence remain unchanged.

---

## 📌 Canonical Specification Location (IMPORTANT)

The **canonical (normative) specification** of VCP is located under:

```text
/spec/
├─ v1.0/   index.html (HTML rendition; Markdown source at repository root)
├─ v1.1/   VCP-Specification-v1_1_{en,ja,zh}.md, PDF, CHANGELOG
└─ v1.2/   VCP-Specification-v1_2_{en,ja,zh}.md,
           VSO-SPEC-CHANGE-001.md (normative annex),
           vcp-event-v1.2.json (JSON Schema)
```

- The English Markdown file in each version directory is the authoritative text;
  Japanese and Chinese translations and PDFs are provided **for convenience only**
- `VCP-Specification-*.md` and `VSO-SPEC-CHANGE-001.md` files at the
  repository root are **non-normative copies** (identical to the `/spec/`
  versions for v1.1 and v1.2)

**If there is any conflict, the content under `/spec/` always prevails.**

---

## 📘 Available Versions

| Version | Status | Date | Location |
|---------|--------|------|----------|
| **v1.2** | **Production Ready (GA)** — corrected source; release target `v1.2.0` | 2026-07-06 (RC1: 2026-05-31) | [`/spec/v1.2/`](spec/v1.2/) · [JSON Schema](spec/v1.2/vcp-event-v1.2.json) |
| v1.1 | Published (no tagged release) | 2025-12-30 | [`/spec/v1.1/`](spec/v1.1/) |
| v1.0 | Released (tag `v1.0.0`) | 2025-11-25 | [`/spec/v1.0/`](spec/v1.0/) |

v1.2 is a protocol-compatible / certification-stricter update: zero breaking
changes, all v1.0 and v1.1 events remain valid. Migration notes and
compatibility considerations are documented inside each version directory.

GA was declared on 2026-07-06. The GA text was committed to this repository
after that date; until that commit, this repository showed RC1. The GA tag must
point to the validated consistency correction, not the earlier uncorrected merge.
Pre-GA v1.2 ERASURE producers need migration; historical records stay unchanged.

---

## 🎯 Purpose

VCP defines a globally consistent audit format that allows third parties to
independently verify the recorded:

- Algorithmic **signals and decisions**
- **Order lifecycle** events (submit, acknowledge, execute, cancel)
- **Risk controls** and parameter snapshots
- **AI governance metadata** (model identity, decision factors, approvals)
- **Time synchronization** and event ordering

VCP makes these records auditable and attributable after the fact. It does not
prevent, block, or intercept any trading or AI behaviour, and events that were
never recorded are outside its reach.

VCP produces evidence relevant to regimes such as:

- MiFID II — Art. 17 with RTS 6 (algorithmic trading) and RTS 25 (clock synchronisation)
- EU AI Act — Article 12 record-keeping, Article 14 human oversight
- GDPR — Article 17 erasure (crypto-shredding may support, and does not determine, compliance)
- SEC CAT (Rule 613) and similar global regimes

> **Legal scope (adopted verbatim from VAP v1.2 §1.6).** VAP and its domain profiles define mechanisms for producing **cryptographically verifiable evidence** of AI system decisions. Conformance to VAP or any profile: (a) does **not** constitute compliance with the EU AI Act, GDPR, MiFID II/III, CAT Rule 613, NIS2, FDA SaMD guidance, or any other law or regulation; (b) does **not** constitute a legal determination that any technical mechanism (including crypto-shredding) satisfies a specific legal obligation; (c) does **not** warrant the correctness, fairness, or safety of the underlying AI decisions — only the integrity, completeness (at anchor granularity), and attributability of their records. VAP generates evidence; competent authorities and courts evaluate it.

---

## 🧩 Protocol Modules

- **VCP-CORE** — Event headers, timestamps, security metadata
- **VCP-TRADE** — Trading and execution payloads
- **VCP-GOV** — Algorithm governance and AI transparency
- **VCP-RISK** — Risk parameters and control triggers
- **VCP-PRIVACY** — Pseudonymization, crypto-shredding, ERASURE event (v1.2)
- **VCP-RECOVERY** — Bounded chain disruption and consistency recovery
- **VCP-XREF** — Cross-party provenance / dual logging (v1.1; multi-actor chains in v1.2)

---

## 🌐 Standardization

| Body | Document | Status |
|------|----------|--------|
| IETF | [`draft-kamimura-scitt-vcp-03`](https://datatracker.ietf.org/doc/draft-kamimura-scitt-vcp/) | Individual Internet-Draft, active. Not adopted by any IETF Working Group; no standing in the IETF standards process |

The SCITT architecture and COSE Receipts that VCP v1.2 aligns with (opt-in) are
now published as **RFC 9943** and **RFC 9942** (June 2026).

---

## 📝 Known issues in v1.2 (informative)

### Integrity review notice — 24 October 2026 (informative)

The published specification requires RFC 6962 construction, but its odd-node
builder and audit-path examples conflict with that requirement. The shown
root-only AnchorRecord signature does not authenticate attached count, endpoint
or policy metadata. Exact nanosecond integer handling also needs a portable
canonicalization contract. These are the bounded observations P1, P2, P4, P6 and
P8 in the [pinned research record](https://github.com/veritaschain/vap-spec/blob/9fa5fbc68075079b4599e16940e9078db976cd59/experiments/vcp-v1.2-integrity-alignment/README.md); P3 separately concerns the quickstart verifier.

The numeric finding distinguishes library input rejection from precision loss:
all 40 tested fixture timestamps are exactly binary64-representable, whereas
arbitrary nanosecond integers need not be. The duplicate-node example is a tree-construction ambiguity, not a SHA-256
collision. Metadata tampering applies where no separate signature or external
anchor authenticates the full AnchorRecord; EventID uniqueness checks and other
controls require implementation-specific assessment. An inclusion proof alone
is not a check of the entire submitted batch. No claim is made that all deployed
implementations have the example's behavior.

[Technical-errata Draft PR #3](https://github.com/veritaschain/vcp-spec/pull/3)
and [normative-change Draft PR #4](https://github.com/veritaschain/vcp-spec/pull/4)
are **unadopted proposals**, not an issued erratum or repaired release. Target
version and migration remain undecided. Existing signed data and fixed releases
are preserved. VAP integrity alignment is under review; full conformance has
not been established. Internal synthetic results are not independent third-party
reproduction, which remains unestablished. Current protocol requirements and
K3 baselines, criteria and results are unchanged.

The 2026-10-09 consistency correction changes pre-GA ERASURE encoding and
registers the Annex system events. It is not technically identical to RC1.
See [compatibility and release gates](spec/v1.2/GA-CONSISTENCY.md). The following
remain errata candidates for the next revision. The full list, including issues
in the normative annex, is in
[`spec/v1.2/README.md`](spec/v1.2/README.md#known-issues-in-v12-informative).

- **Superseded references.** §12 cites `draft-ietf-scitt-architecture` and
  `draft-ietf-cose-merkle-tree-proofs`; these are now **RFC 9943** and
  **RFC 9942**. §12 also cites `draft-kamimura-scitt-vcp` under a former
  title; the current revision is -05 (2026-10-24).
- **Security field names and levels.** §6.4 names the anchor reference
  `AnchorReference`, and §6.4.1 lists it with `MerkleRoot` and `MerkleIndex`
  as REQUIRED from v1.1. The v1.2 schema treats the three as VC-Certified
  requirements enforced by Registration Policy and also accepts `AnchorRef`,
  the field name of draft-kamimura-scitt-vcp. The intended level and the
  canonical name are to be settled in the next revision.
- **Retired service in examples.** The "Attested Database Examples" table in
  §6.3.3, and Annex §2.4 and §8.8, list AWS QLDB, which reached end of support
  on 2025-07-31.
- **Capability language.** §1.1 describes the format as "immutable" and as
  "ensuring compliance with international regulations"; §3.2.2 calls ERASURE
  "a new immutable event". The property the protocol provides is
  tamper-evidence (append-only records), and conformance does not constitute
  compliance (see Legal scope above).
- **Status and cross-party language.** §1.1 calls VCP "a global standard
  specification"; it has not been adopted by any established standards body.
  §1.1 also says the chain of evidence "establishes truth"; it makes
  alteration and post-anchor omission detectable, not the recorded content
  true. §5.6 (VCP-XREF) says "Guarantee: Unless both parties collude", lists
  "Prevent payout disputes" as a use case and calls the result "non-repudiable
  evidence". The property provided is that one party's omission or
  modification is detectable by the other when both parties record and do
  not collude; the evidential weight is for competent authorities and courts.
- **Completeness language.** §1.1 (note "Completeness Guarantees"), §2.2.3,
  §6.0 and Appendix D speak of "completeness guarantees", say that "no required
  events were omitted" and call event batches "provably complete". The property
  the protocol provides is detectability, at batch granularity, of omission
  after anchoring and of split-view presentation (VAP v1.2 INT-008). An event
  that never entered an anchored batch is not revealed by it.
- **Annex benchmark figures.** Annex §8 reports figures for `vcp-core-py` and
  `vcp-core-cpp` v1.2.0. Those implementations are not publicly available, so
  the figures cannot be reproduced from published artifacts. They are
  informative (Annex §8.2) and are not independent evidence of performance.

---

## 🧪 Reference Implementation

A **non-certified reference implementation** is available separately:

https://github.com/veritaschain/vcp-rta-reference

This implementation is provided for demonstration and testing purposes only
and does **not** imply certification or regulatory approval. It is a
first-party implementation: VSO and VeritasChain Co., Ltd. share a founder, and
a first-party implementation is not independent validation.

---

## 🔒 License

The VeritasChain Protocol specification is licensed under:

**Creative Commons Attribution 4.0 International (CC BY 4.0)**

You may copy, redistribute, and adapt the specification with proper attribution
to **VeritasChain Standards Organization (VSO)**.

---

## 🏛 Maintainer

**VeritasChain Standards Organization (VSO)**<br>
Website: https://veritaschain.org<br>
Email: standards@veritaschain.org<br>
GitHub: https://github.com/veritaschain

---

## 🤝 Contributions

We welcome:
- Technical feedback on the specification
- Interoperability and conformance reports
- Early adopter experiences
- Proposals for future versions or domain profiles

Please open an Issue or Pull Request to contribute.

---

**VeritasChain Protocol — Verify, Don’t Trust.**
