![VCP specification status](https://img.shields.io/badge/VCP-v1.2%20Specification%20GA-blue)
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
and its first implementation profile. [VAP v1.2 alignment remains under review](https://github.com/veritaschain/vap-spec/blob/b5ef9316717bebe638d5eca621327b54cdda93e1/spec/v1.2/VAP_Framework_Specification.md); full conformance has not been established. Within the VAP family, the designation
"Protocol" is reserved for VCP, which defines an actual wire protocol.

This repository is maintained by the
**VeritasChain Standards Organization (VSO)**.

### Implementation status (mandatory disclosure)

As of 25 October 2026: **zero external implementations** of VCP or any other VAP
profile, and **zero Evidence Packs accepted in any proceeding**. How these items
will be counted is set out in VSO's [proposed counting criteria](https://github.com/veritaschain/vap-spec/blob/main/disclosures/2026-10-24-counting-criteria.md).

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
| **v1.2** | **Released** — GA declared 2026-07-06; tag `v1.2.0` (commit `b23acb2`, 2026-10-09) | 2026-07-06 (RC1: 2026-05-31) | [`/spec/v1.2/`](spec/v1.2/) · [JSON Schema](spec/v1.2/vcp-event-v1.2.json) |
| v1.1 | Published (no tagged release) | 2025-12-30 | [`/spec/v1.1/`](spec/v1.1/) |
| v1.0 | Released (tag `v1.0.0`) | 2025-11-25 | [`/spec/v1.0/`](spec/v1.0/) |

v1.2 adds features and stricter certification requirements. Historical v1.0/v1.1
records retain their original validation context and signed bytes; this does not
mean that every old-format event passes the v1.2 schema. Known Header and
EventType divergences prevent an unconditional backward-compatibility claim.
Assess producer/verifier compatibility against the declared version and policy;
do not rewrite historical signed records to make them pass a newer schema.
See the [known issues](spec/v1.2/README.md#known-issues-in-v12-informative) and
version-specific migration notes. This is an informative clarification, not a
change to the frozen specifications or schemas.

GA was declared on 2026-07-06. The GA text was committed to this repository
after that date; until that commit, this repository showed RC1. The `v1.2.0` tag
points to the validated consistency correction (commit `b23acb2`, 2026-10-09),
not the earlier uncorrected PR #1 merge.
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
- **VCP-ANCHOR** — Anchor migration and failover payloads (`MigrationDetails`,
  `FailoverDetails`) carried by the `SYS_ANCHOR_MIGRATION` and
  `SYS_ANCHOR_FAILOVER` system events (v1.2 GA correction; specification §3.2.3,
  Annex §1.4.10). §1.6 of the specification does not list it (see Known issues)

---

## 🌐 Standardization

| Body | Document | Status |
|------|----------|--------|
| IETF | [`draft-kamimura-scitt-vcp-05`](https://datatracker.ietf.org/doc/draft-kamimura-scitt-vcp/) (posted 2026-10-24) | Individual Internet-Draft, active. Not adopted by any IETF Working Group; no standing in the IETF standards process |

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
P8 in the [pinned research record](https://github.com/veritaschain/vap-spec/blob/9fa5fbc68075079b4599e16940e9078db976cd59/experiments/vcp-v1.2-integrity-alignment/README.md); P5, cited here from 2026-10-25, records that the VCP Merkle leaf input, `H(0x00 || EventHash)`, differs from the `H(0x00 || canonical(E))` of VAP v1.2 Mechanism B, a mapping item for the clause-level mapping; P3 separately concerns the quickstart verifier (its claims were corrected on 2026-10-25; the algorithm is unchanged).

The numeric finding distinguishes library input rejection from precision loss:
all 40 tested fixture timestamps are exactly binary64-representable, whereas
arbitrary nanosecond integers need not be. The duplicate-node example is a tree-construction ambiguity, not a SHA-256
collision. Metadata tampering applies where no separate signature or external
anchor authenticates the full AnchorRecord; EventID uniqueness checks and other
controls require implementation-specific assessment. An inclusion proof alone
is not a check of the entire submitted batch. No claim is made that all deployed
implementations have the example's behavior.

The [technical-errata draft](proposals/integrity-2026-10-24/technical-errata-draft.md)
and the [normative-change draft](proposals/integrity-2026-10-24/normative-change-draft.md)
were merged on 24 October 2026 as discussion documents (PR #3 and PR #4). Merging
them did not adopt them: both remain **unadopted proposals**, not an issued erratum or repaired release. Target
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

Recorded 2026-10-25:

- **Certification governance language.** §9.2 says VC-Certified certificates
  are issued by "VSO-accredited Conformity Assessment Bodies (CABs)", draws
  "Accredited CABs (multiple)" and lists "CAB accreditation" among VSO's
  responsibilities; §6.3.3 cites VSO-CAB-REQ-001 as "CAB Accreditation
  Requirements". The JA translation says the same; the ZH translation uses 认可 in §9.2 and "CAB认证要求" in §6.3.3. The scheme requires
  CABs that are independent of the scheme owner. The only registered CAB,
  VeritasChain Co., Ltd., operates VSO and is not independent of it (VAP v1.2
  §8.3, §10.1, ERRATA E-2026-10-21). VSO approval of a CAB is not
  accreditation in the ISO/IEC 17000 sense.
- **Annex compliance and SDK language.** Annex §3.1 introduces ERASURE "for
  GDPR Article 17 compliance"; §3.3 describes audit trails as "Immutability by
  design"; §10.4 says one line of `vcp-core-py` configuration "achieves v1.2
  Silver compliance"; §10.8 promises "Zero-config compliance"; Appendix B.2
  asks "Do you need GDPR Article 17 compliance?". `vcp-core-py` is not publicly
  available, so the configuration claim cannot be checked from published
  artifacts. Tier conformance is not regulatory compliance (VAP v1.2 §1.6),
  crypto-shredding may support but does not determine Article 17 compliance
  (VAP v1.2 §6.3.4), and the records are append-only and tamper-evident, not
  immutable.
- **Attested-database anchor targets.** §2.2.2, §2.2.3 and §6.3.3 accept an
  attested database as an external anchor target, and the §6.3.3 AnchorRecord
  allows `AnchorTarget.Type` `DATABASE`. VAP v1.2 §4.1.4 (INT-006) lists the
  anchor target classes profiles select from (RFC 3161 TSA, RFC 6962-class
  transparency log, public blockchain, SCITT transparency service, public
  timestamping service); an attested database is not among them, and
  `DATABASE` is not in the VAP §7.5 `anchor_target.type` enum. This is a
  mapping item for the clause-level mapping.
- **Header and governance fields.** §4 says "unchanged from v1.0", but the v1.0
  header fields `ClockSyncStatus`, `TimestampPrecision`, `VenueID`, `Symbol`,
  `AccountID` and `OperatorID` are rejected in `Header` by the closed v1.2
  schema (`VenueID`, `Symbol` and `AccountID` are defined under
  `Payload.VCP-TRADE`; `ClockSyncStatus` and `TimestampPrecision` have no
  schema location). The schema's `VCP-GOV` defines no `LastApprovalBy`,
  `TestingRecordLink` or `OperatorID`, which VAP v1.2 §5.1.4 maps. Field
  placement is discussed in the unadopted
  [native-layout migration draft](proposals/native-layout-migration-2026-10-25/README.md).
- **Event type registry and compatibility wording.** The §3.1 state diagram uses
  `REJ` and `PRT`, §8.1.3 uses `SNC`, and §3.2 inherits the v1.0 core event
  types, which also include `ALG`, `AUD` and `REC` (v1.0 §3.2.1). The v1.2
  schema `EventType` enum contains none of these six, so such events fail
  schema validation. §1.3 says "Full backward compatibility is guaranteed
  within the v1.x series"; the schema does not support that for these types.
  The same applies to the VSO-SPEC-CHANGE-001 §4.3 rows "v1.2 accepts all v1.0
  events" and "v1.2 accepts all v1.1 events" (recorded 2026-10-28).
- **Schema validity is not conformance.** §6.3.1 says all events MUST be
  signed, and §5.5.3 makes `ConformanceTier`, `RegistrationPolicy.Issuer` and
  `VerificationDepth` REQUIRED. The schema requires only `EventHash` and
  `SignAlgo` in `Security`, makes the `PolicyIdentification` block optional
  and does not require `Issuer` or `VerificationDepth` in it. For the Merkle
  and anchor fields, see "Security field names and levels" above. Passing the
  schema does not show conformance.
- **Event envelope versus VAP §7.1.** The closed v1.2 schema rejects the VAP
  v1.2 §7.1 top-level `vap_version` member, has no counterpart of
  `policy.vap_conformance`, and declares verification depth as three booleans
  (§5.5.2: `HashChainValidation`, `MerkleProofRequired`,
  `ExternalAnchorRequired`; untyped in the schema) rather than VAP's
  `sequence_mechanisms` list.
  This structural divergence is to be resolved in the clause-level mapping.
- **ERASURE fields versus VAP §6.3.3.** VCP `ErasureDetails` (seven nested
  members) has no published mapping to the VAP fields
  `erasure_target_event_ids`, `erasure_reason`, `key_destruction_proof`,
  `retention_exemption` and `operator_id`. The canonical `ErasureDetails.Reason.Code` enum rejects `LEGAL_ORDER`,
  which is in the VAP base `erasure_reason` enum (Annex §3.4.3 maps it to
  `COURT_ORDER` only with court-order evidence). VAP §6.3.4 requires
  `retention_exemption` where a retention duty overrides erasure; VCP keeps
  `RetentionExemption` outside `ErasureDetails`, and Annex §3.4 says not to
  emit a successful ERASURE event for data that remains decryptable.
- **Algorithm, identifier and count types.** §1.4 lists `RSA_2048` among
  supported algorithms, while §1.5.1 marks it DEPRECATED. The schema `HashAlgo`
  enum accepts `SHA3_512`, which §1.5.2 marks FUTURE. §9.1.1 and UID-001 make
  UUID v7 required at every tier, while the schema comment requires it at
  Gold/Platinum only and accepts any string in the 8-4-4-4-12 hex pattern (not only RFC 9562 UUIDs), and v1.0 §4.1.1 allows v7
  or v4. The §6.3.3 AnchorRecord `EventCount` is `int32`; VAP v1.2 §7.5
  `event_count` is `int64`.
- **Module list.** §1.6 lists seven modules and omits `VCP-ANCHOR`, which §3.2.3
  and Annex §1.4.10 use for the `SYS_ANCHOR_MIGRATION` and
  `SYS_ANCHOR_FAILOVER` payloads.
- **Partial translations.** The JA and ZH texts omit parts of the English text,
  including §5.6.5, §5.6.6 and §5.6.9; the bodies of §6.1–§6.2, §6.3.1 and
  §6.3.2; three §6.3.3 subsections; §6.4; §7.1; §8.1.2–§8.1.3; the Gold/Platinum
  steps of §10.2; and Appendix E.3. Details are in
  [`spec/v1.2/README.md`](spec/v1.2/README.md#known-issues-in-v12-informative).

---

## 🧪 Reference Implementation

A **non-certified reference implementation** is available separately:

https://github.com/veritaschain/vcp-rta-reference

This implementation is provided for demonstration and testing purposes only
and does **not** imply certification or regulatory approval. It targets VCP
v1.1; it is not a v1.2 verifier. It is a
first-party implementation: VSO and VeritasChain Co., Ltd. share a founder, and
a first-party implementation is not independent validation.

An offline core library for v1.2, [vcp-sdk](https://github.com/veritaschain/vcp-sdk)
v0.1.0 (pre-release; Python, TypeScript, MQL5), is also available. It is written
by VeritasChain Co., Ltd., so it is first-party as well and does not change the
external-implementation count above. Where the v1.2 text is ambiguous it makes a
choice of its own, listed in its
[INTERPRETATIONS.md](https://github.com/veritaschain/vcp-sdk/blob/v0.1.0/INTERPRETATIONS.md)
(for example, RFC 6962 trees rather than the §6.2.1 example builder, and integers
canonicalised as exact digits). Those choices are not adopted by VSO change
control. A `VALID` result from it is not a conformance claim.

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
