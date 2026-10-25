# VCP Specification v1.2

**VeritasChain Protocol (VCP)** — The open standard for cryptographic audit trails in algorithmic trading systems.

> *"Verify, Don't Trust"*

---

## Status

**Production Ready** — Released. GA declared 2026-07-06 (Release Candidate RC1 published 2026-05-31); tag `v1.2.0` (commit `b23acb2`, 2026-10-09) on the validated correction commit, not the earlier PR #1 merge.

v1.2 is a **protocol-compatible / certification-stricter** update over v1.1. It introduces **zero breaking changes**: all v1.0 and v1.1 events remain valid and verifiable under v1.2. The complete normative specification of every change is provided in this directory as the normative annex VSO-SPEC-CHANGE-001 (see Documents below).

The 2026-10-09 GA consistency correction changes the untagged pre-GA ERASURE encoding and adds the five Annex system codes to the schema. **This is not technically identical to RC1.** See [GA consistency and compatibility](GA-CONSISTENCY.md) for migration, validation scope and release gates. The 2026-07-06 GA declaration is historical; it is not evidence of a tag or completed release.

## Overview

v1.2 strengthens operational integrity (VCP-RECOVERY), reconciles append-only audit trails with the GDPR right to erasure (ERASURE / crypto-shredding), aligns with IETF SCITT for interoperability, and adds support for multi-party (cross-organization) audit chains.

## Key Changes in v1.2

| # | Change | Type | Annex |
|---|--------|------|-------|
| 1 | VCP-RECOVERY constraint strengthening (SKIP/REBUILD/MERGE/CHECKPOINT bounds, Emergency Override) | Normative | §1 |
| 2 | External Anchor blockchain selection criteria | Normative | §2 |
| 3 | ERASURE event type (GDPR Art. 17 / crypto-shredding) | Normative | §3 |
| 4 | Version Compatibility Matrix | Informative | §4 |
| 5 | SCITT alignment fields (COSE Receipts, transparency service) | Normative (opt-in) | §5 |
| 6 | Latency budget clarification | Informative (the annex classifies it as Normative — see Known issues) | §6 |
| 7 | Anchor target continuity plan | Normative | §7 |
| 8 | Reference implementation benchmarks | Informative | §8 |
| 9 | Multi-actor chain linking (cross-party VCP-XREF) | Normative (when used) | §9 |

**Certification:** VC-Certified v1.2 additionally requires the strengthened VCP-RECOVERY constraints and a documented anchor continuity plan. v1.0/v1.1-certified implementations remain protocol-compatible but must meet these constraints for v1.2 certification.

**Post-quantum:** `DILITHIUM2` (ML-DSA / FIPS 204) and `FALCON512` (FN-DSA / FIPS 206 draft) advance from *FUTURE* to *EXPERIMENTAL*. `Ed25519` remains the DEFAULT; PQC is not yet a certification requirement.

## What v1.2 GA Claims — and What It Does Not

GA ("Production Ready") is a **specification-level** status. In keeping
with VSO's honest-scoping policy, the following distinctions apply.

**GA means:**

- The v1.2 specification text (EN/JA/ZH), its normative annex
  (VSO-SPEC-CHANGE-001), and the canonical JSON Schema are stable and
  frozen only by the verified release tag. Future tagged-artifact changes require errata or a new version.
- v1.2 is protocol-compatible with v1.0/v1.1: zero breaking changes;
  historical v1.0/v1.1 events retain their original validation context. Untagged v1.2 ERASURE migration is explicitly breaking (Annex §3.4.3).
- An IETF SCITT profile aligned with v1.2 exists as an individual
  Internet-Draft ([draft-kamimura-scitt-vcp](https://datatracker.ietf.org/doc/draft-kamimura-scitt-vcp/)).

**GA does not claim:**

- **Production track record.** VCP has zero external implementations
  and no production deployments in institutional trading environments.
  The benchmark figures in Annex §8 are informative and cannot be
  reproduced from published artifacts (see Known issues).
- **IETF status.** draft-kamimura-scitt-vcp is an individual
  submission. It is not adopted by the SCITT Working Group, is not
  endorsed by the IETF, and confers no formal standing.
- **Regulatory compliance.** VCP supports evidence generation for
  obligations such as EU AI Act Articles 12/19/26/72 and MiFID II
  RTS 6/25. It does not make any system compliant, is not a
  harmonised standard, and carries no presumption of conformity.
- **Legal certainty for ERASURE.** Crypto-shredding is a technical
  mechanism supporting erasure obligations, not a legal
  determination. Case law is evolving — CJEU C-413/23 P (judgment of
  4 September 2025) confirmed a "relative" approach to personal data
  for pseudonymised data, supportive but not dispositive for
  crypto-shredding as GDPR Article 17 erasure — and interaction with
  retention regimes (e.g., SEC Rule 17a-4, MiFID II Art. 16(7))
  remains jurisdiction-dependent.
- **Completeness beyond its limits.** v1.2 strengthens omission
  *detection* (sequence continuity, external anchoring). It cannot
  prove that an event was never recorded in the first place — an
  information-theoretic limit, stated as such.
- **Implementation GA.** SDKs and the conformance test suite do not
  yet validate v1.2-specific structures (SCITTAlignment, ERASURE).
  Until they do, GA is a statement about the specification, not the
  toolchain.

The certification scheme requires that certification against VCP be performed
by Conformity Assessment Bodies (CABs) that are independent of the scheme owner,
not by VSO. The only registered CAB, VeritasChain Co., Ltd., operates VSO and is
not independent of it; no independent CAB is registered (VAP v1.2 §8.3, §10.1,
ERRATA E-2026-10-21).

## Documents

| Language | File | Status |
|----------|------|--------|
| 🇬🇧 English | [VCP-Specification-v1_2_en.md](VCP-Specification-v1_2_en.md) | Production Ready (normative) |
| 📎 Change Proposal (normative annex) | [VSO-SPEC-CHANGE-001.md](VSO-SPEC-CHANGE-001.md) | Adopted into v1.2 (Rev. 3 + 2026-10-09 correction); prevails over the specification text where they differ |
| 🧩 JSON Schema | [vcp-event-v1.2.json](vcp-event-v1.2.json) | Canonical source; website copy must match at release (https://veritaschain.org/schema/vcp-event-v1.2.json) |
| 🇯🇵 日本語 | [VCP-Specification-v1_2_ja.md](VCP-Specification-v1_2_ja.md) | Translation (convenience only; English prevails) |
| 🇨🇳 中文 | [VCP-Specification-v1_2_zh.md](VCP-Specification-v1_2_zh.md) | Translation (convenience only; English prevails) |
| 📄 PDF | VCP-Specification-v1_2_en.pdf | Planned |

## Three-Layer Architecture

The three-layer integrity architecture introduced in v1.1 (Layer 1 Event Integrity, Layer 2 Collection Integrity / Merkle Tree, Layer 3 External Verifiability) is **unchanged** in v1.2. See Section 6 of the specification for details.

## Known issues in v1.2 (informative)

### Integrity review notice — 24 October 2026 (informative)

The published specification requires RFC 6962 construction, but its odd-node
builder and audit-path examples conflict with that requirement. The shown
root-only AnchorRecord signature does not authenticate attached count, endpoint
or policy metadata. Exact nanosecond integer handling also needs a portable
canonicalization contract. These are the bounded observations P1, P2, P4, P6 and
P8 in the [pinned research record](https://github.com/veritaschain/vap-spec/blob/9fa5fbc68075079b4599e16940e9078db976cd59/experiments/vcp-v1.2-integrity-alignment/README.md); P5 (added 2026-10-25) records that the VCP Merkle leaf input, `H(0x00 || EventHash)`, differs from the `H(0x00 || canonical(E))` of VAP v1.2 Mechanism B, a mapping item for the clause-level mapping; P3 separately concerns the quickstart verifier (its claims were corrected on 2026-10-25; the algorithm is unchanged).

The numeric finding distinguishes library input rejection from precision loss:
all 40 tested fixture timestamps are exactly binary64-representable, whereas
arbitrary nanosecond integers need not be. The duplicate-node example is a tree-construction ambiguity, not a SHA-256
collision. Metadata tampering applies where no separate signature or external
anchor authenticates the full AnchorRecord; EventID uniqueness checks and other
controls require implementation-specific assessment. An inclusion proof alone
is not a check of the entire submitted batch. No claim is made that all deployed
implementations have the example's behavior.

The [technical-errata draft](../../proposals/integrity-2026-10-24/technical-errata-draft.md)
and the [normative-change draft](../../proposals/integrity-2026-10-24/normative-change-draft.md)
were merged on 24 October 2026 as discussion documents (PR #3 and PR #4). Merging
them did not adopt them: both remain **unadopted proposals**, not an issued erratum or repaired release. Target
version and migration remain undecided. Existing signed data and fixed releases
are preserved. VAP integrity alignment is under review; full conformance has
not been established. Internal synthetic results are not independent third-party
reproduction, which remains unestablished. Current protocol requirements and
K3 baselines, criteria and results are unchanged.

The v1.2 text is unchanged in these respects; they are errata candidates for the next revision.

| Location | Issue |
|----------|-------|
| §12 References | `draft-ietf-scitt-architecture` and `draft-ietf-cose-merkle-tree-proofs` are now **RFC 9943** and **RFC 9942** (June 2026) |
| §12 References | `draft-kamimura-scitt-vcp` is cited under a former title, "SCITT Profile for Financial Trading Audit Trails — VCP". The current title is "A SCITT Profile for Verifiable Audit Trails in Algorithmic Trading: The VeritasChain Protocol (VCP)" (revision -05, 2026-10-24); it remains an individual Internet-Draft with no IETF standing |
| §6.4, §6.4.1; `vcp-event-v1.2.json` | §6.4 names the anchor reference `AnchorReference`, and §6.4.1 lists `AnchorReference`, `MerkleRoot` and `MerkleIndex` as REQUIRED from v1.1. The v1.2 schema requires only `EventHash` and `SignAlgo` in `Security`, describes the three fields as VC-Certified requirements enforced by Registration Policy, and also accepts `AnchorRef`, the field name used by draft-kamimura-scitt-vcp. Whether the three fields are protocol or certification requirements, and which name is canonical, is to be settled in the next revision |
| §6.3.3 Attested Database Examples; Annex §2.4, §8.8 | AWS QLDB reached end of support on 2025-07-31 |
| §6.3.1 table | DILITHIUM2 / FALCON512 still shown as "Future (reserved)", while §1.4 and §1.5.1 give their v1.2 status as EXPERIMENTAL; §1.5.1 prevails |
| §1.1 | "immutable" and "ensuring compliance with international regulations" — the property provided is tamper-evidence, and conformance does not constitute compliance (VAP v1.2 §1.6) |
| §3.2.2 | ERASURE described as "a new immutable event" — append-only, tamper-evident |
| §1.1 note; §2.2.3; §6.0; Appendix D | "Completeness guarantees", "no required events were omitted", "provably complete" — the property provided is detectability, at batch granularity, of omission after anchoring and of split-view presentation (VAP v1.2 INT-008); an event that never entered an anchored batch is not revealed by it |
| Summary of Changes; Annex Executive Summary, Appendix A | Change counts disagree: both summaries state 7 Normative / 2 Informative; the specification's own change table lists 6 / 3; annex Appendix A lists 7 / 3 (adding §10 Silver Tier guidance). Annex Appendix A has no heading of its own (A.1 follows §10 directly) |
| Summary of Changes #6 vs Annex §6.2, A.1 | Latency budget clarification is Informative in the specification's change table and Normative in the annex; the annex prevails (Summary of Changes note) |
| §1.1 | "a global standard specification" — VCP is a published VSO specification; it has not been adopted by any established standards body, and its IETF profile is an individual Internet-Draft. "establishes truth ('Veritas')" — the chain of evidence makes alteration and post-anchor omission of records detectable; it does not establish that the recorded decisions or events were correct or true (VAP v1.2 §1.6(c)) |
| §5.6.1 diagram; §5.6.2 use-case table; §5.6.7 | "Guarantee: Unless both parties collude …", "Prevent payout disputes" and "KEY GUARANTEE … non-repudiable evidence" — VCP-XREF makes one party's omission or modification detectable by the other party when both parties record and do not collude; it does not prevent disputes, and the evidential weight of the records is for competent authorities and courts (VAP v1.2 §1.6) |
| Annex §8 | Benchmark figures are reported for `vcp-core-py` / `vcp-core-cpp` v1.2.0, which are not publicly available; the figures cannot be reproduced from published artifacts and are informative only (§8.2) |
| §3.2.1 Error Event Schema Extension | The example puts `ErrorDetails` at the top level of the event and uses `Header.Timestamp`. The v1.2 event schema allows only `Header`, `Payload`, `Security` and `PolicyIdentification` at the top level (`additionalProperties: false`), requires `Header.TimestampInt`, does not allow `Header.Timestamp`, and defines no `ErrorDetails`. A schema-valid event therefore cannot carry `ErrorDetails` where §3.2.1 places it, although §3.2.1 makes `ErrorDetails.Severity` and `ErrorDetails.ErrorMessage` REQUIRED |
| §6.3.1; §7.1 example | "All VCP events MUST be digitally signed", but v1.2 defines only the Merkle-root signature (`sign_merkle_root`, over the decoded root bytes). The §7.1 example calls `sign_event`, which v1.2 does not define; the bytes an event signature covers are defined only in VCP v1.0 §6.2.2 (`event_hash.encode()`, the ASCII hex digest) |
| §2.1 tier table | Silver lists "Ed25519 (Delegated)"; the specification does not define delegated signing (who holds the key, what is delegated, and how the delegation is recorded) |

The last three rows were found while writing [vcp-sdk](https://github.com/veritaschain/vcp-sdk) v0.1.0, a first-party, pre-release offline core for v1.2. Its [INTERPRETATIONS.md](https://github.com/veritaschain/vcp-sdk/blob/v0.1.0/INTERPRETATIONS.md) records the reading that library takes in each case (I-5, I-7). Those readings are the library's and are not adopted by VSO change control. The unit of `AnchorRecord.Timestamp` is covered by the [numeric-field inventory](../../proposals/numeric-fields-2026-10-25/).

Recorded 2026-10-25:

| Location | Issue |
|----------|-------|
| §9.2; §6.3.3 (VSO-CAB-REQ-001 reference); JA/ZH §9.2 | "VSO-accredited Conformity Assessment Bodies (CABs)", "Accredited CABs (multiple)", "CAB accreditation" as a VSO responsibility, and "CAB Accreditation Requirements" — the scheme requires CABs that are independent of the scheme owner; the only registered CAB, VeritasChain Co., Ltd., operates VSO and is not independent of it (VAP v1.2 §8.3, §10.1, ERRATA E-2026-10-21). VSO approval of a CAB is not accreditation in the ISO/IEC 17000 sense |
| Annex §3.1, §3.3, §10.4, §10.8, Appendix B.2 | "for GDPR Article 17 compliance", "Immutability by design", "This single line achieves v1.2 Silver compliance" (`vcp-core-py`), "Zero-config compliance", "Do you need GDPR Article 17 compliance?" — `vcp-core-py` is not publicly available, so the configuration claim cannot be checked from published artifacts; tier conformance is not regulatory compliance (VAP v1.2 §1.6); crypto-shredding may support but does not determine Article 17 compliance (VAP v1.2 §6.3.4); the records are append-only and tamper-evident, not immutable |
| §2.2.2, §2.2.3, §6.3.3 (anchor targets; AnchorRecord `AnchorTarget.Type`) | An attested database is accepted as an external anchor target and `DATABASE` is an AnchorRecord target type. VAP v1.2 §4.1.4 (INT-006) lists the anchor target classes profiles select from (RFC 3161 TSA, RFC 6962-class transparency log, public blockchain, SCITT transparency service, public timestamping service); an attested database is not among them, and `DATABASE` is not in the VAP §7.5 `anchor_target.type` enum. Mapping item for the clause-level mapping |
| §4 ("unchanged from v1.0"); `vcp-event-v1.2.json` `Header`, `VCP-GOV` | The v1.0 §4.1.1 header fields `ClockSyncStatus`, `TimestampPrecision`, `VenueID`, `Symbol`, `AccountID` and `OperatorID` are rejected in `Header` by the closed v1.2 schema (`VenueID`, `Symbol`, `AccountID` are defined under `Payload.VCP-TRADE`; `ClockSyncStatus` and `TimestampPrecision` have no schema location). `VCP-GOV` defines no `LastApprovalBy`, `TestingRecordLink` or `OperatorID`, which VAP v1.2 §5.1.4 maps. See the unadopted [native-layout migration draft](../../proposals/native-layout-migration-2026-10-25/README.md) |
| §3.1 diagram, §3.2, §8.1.3; §1.3; `vcp-event-v1.2.json` `EventType` | The §3.1 diagram uses `REJ` and `PRT`, §8.1.3 uses `SNC`, and §3.2 inherits the v1.0 core event types, which also include `ALG`, `AUD` and `REC` (v1.0 §3.2.1). None of these six is in the schema `EventType` enum, so such events fail schema validation; §1.3 "Full backward compatibility is guaranteed within the v1.x series" is not supported by the schema for these types |
| §6.3.1, §5.5.3; `vcp-event-v1.2.json` `Security`, `PolicyIdentification` | The text requires every event to be signed and makes `ConformanceTier`, `RegistrationPolicy.Issuer` and `VerificationDepth` REQUIRED; the schema requires only `EventHash` and `SignAlgo` in `Security`, makes the top-level `PolicyIdentification` block optional and does not require `Issuer` or `VerificationDepth` in it. For the Merkle and anchor fields see the §6.4 / §6.4.1 row above. Schema validity is not conformance |
| §5.5.2; `vcp-event-v1.2.json` (root) | The closed schema rejects the VAP v1.2 §7.1 top-level `vap_version` member, has no counterpart of `policy.vap_conformance`, and declares verification depth as a boolean `HashChainValidation` rather than VAP's `sequence_mechanisms` list. Structural divergence for the clause-level mapping |
| §3.2.2; Annex §3.4, §3.4.3; `vcp-event-v1.2.json` `ErasureDetails` | VCP `ErasureDetails` has no published mapping to the VAP v1.2 §6.3.3 fields (`erasure_target_event_ids`, `erasure_reason`, `key_destruction_proof`, `retention_exemption`, `operator_id`). The schema rejects `LEGAL_ORDER`, which is in the VAP base `erasure_reason` enum (Annex §3.4.3 maps it to `COURT_ORDER` only with court-order evidence). VAP §6.3.4 requires `retention_exemption` where a retention duty overrides erasure; VCP keeps `RetentionExemption` outside `ErasureDetails`, and Annex §3.4 says not to emit a successful ERASURE event for data that remains decryptable |
| §1.4; §1.5.2; §9.1.1, §9.1.2 (UID-001); §6.3.3 AnchorRecord | §1.4 lists `RSA_2048` as supported, while §1.5.1 marks it DEPRECATED. The schema `HashAlgo` enum accepts `SHA3_512`, which §1.5.2 marks FUTURE. UUID v7 is "Required" at every tier, while the schema comment requires it at Gold/Platinum only and accepts any RFC 9562 UUID, and v1.0 §4.1.1 allows v7 or v4. AnchorRecord `EventCount` is `int32`; VAP v1.2 §7.5 `event_count` is `int64` |
| §1.6 | The core module list omits `VCP-ANCHOR`, which §3.2.3 and Annex §1.4.10 use for `Payload.VCP-ANCHOR.MigrationDetails` / `FailoverDetails` (`SYS_ANCHOR_MIGRATION`, `SYS_ANCHOR_FAILOVER`) |
| JA / ZH translations | Partial translations. Omitted relative to the English text: §5.6.5 Cross-Reference Protocol, §5.6.6 Discrepancy Handling and §5.6.9 (JA/ZH §5.6.5–§5.6.6 correspond to English §5.6.7–§5.6.8); the bodies of §6.1–§6.2 (placeholders only), §6.3.1 and §6.3.2; the §6.3.3 subsections Acceptable Anchor Targets, Anchoring Record Schema and Silver Tier Anchoring Options; §6.4 and §6.4.1; §7.1 (placeholder only); §8.1.2 and §8.1.3; the Gold/Platinum steps of §10.2; Appendix E.3 AnchorRecord PQC Extension (JA/ZH E.3 corresponds to English E.4). The English text prevails |

## Relationship to VAP

VCP is the first implementation profile of the VAP family. [The current VAP status](https://github.com/veritaschain/vap-spec/blob/b5ef9316717bebe638d5eca621327b54cdda93e1/spec/v1.2/VAP_Framework_Specification.md) records VCP v1.1 and v1.2 integrity alignment under review, a mapping outstanding, and full conformance unestablished. Under VAP §1.7, that current status prevails over the historical compatibility claims in VSO-VAP-CHANGE-001 CH-11 / Annex A; the annex itself is preserved. VAP and VCP version numbers are assigned independently; matching version numbers do not establish conformance.

## Relationship to v1.1

v1.2 does not restructure the protocol. It extends v1.1 with the changes listed above. To migrate from v1.1, see Section 10.4 of the specification; no data migration is required.

---

<p align="center">
  <strong>VeritasChain Standards Organization (VSO)</strong><br/>
  <em>"Verify, Don't Trust"</em><br/>
  <a href="https://veritaschain.org">veritaschain.org</a>
</p>
