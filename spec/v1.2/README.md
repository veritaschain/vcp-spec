# VCP Specification v1.2

**VeritasChain Protocol (VCP)** — The open standard for cryptographic audit trails in algorithmic trading systems.

> *"Verify, Don't Trust"*

---

## Status

**Production Ready** — GA 2026-07-06 (Release Candidate RC1 published 2026-05-31). Release target: `v1.2.0` on the validated correction commit, not the earlier PR #1 merge. Tag existence must be verified before downstream publication.

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

Certification against VCP is performed by independent Conformity
Assessment Bodies (CABs), not by VSO.

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

The v1.2 text is unchanged in these respects; they are errata candidates for the next revision.

| Location | Issue |
|----------|-------|
| §12 References | `draft-ietf-scitt-architecture` and `draft-ietf-cose-merkle-tree-proofs` are now **RFC 9943** and **RFC 9942** (June 2026) |
| §6.3.3 Attested Database Examples; Annex §2.4, §8.8 | AWS QLDB reached end of support on 2025-07-31 |
| §6.3.1 table | DILITHIUM2 / FALCON512 still shown as "Future (reserved)", while §1.4 and §1.5.1 give their v1.2 status as EXPERIMENTAL; §1.5.1 prevails |
| §1.1 | "immutable" and "ensuring compliance with international regulations" — the property provided is tamper-evidence, and conformance does not constitute compliance (VAP v1.2 §1.6) |
| §3.2.2 | ERASURE described as "a new immutable event" — append-only, tamper-evident |
| §1.1 note; §2.2.3; §6.0; Appendix D | "Completeness guarantees", "no required events were omitted", "provably complete" — the property provided is detectability, at batch granularity, of omission after anchoring and of split-view presentation (VAP v1.2 INT-008); an event that never entered an anchored batch is not revealed by it |
| Summary of Changes; Annex Executive Summary, Appendix A | Change counts disagree: both summaries state 7 Normative / 2 Informative; the specification's own change table lists 6 / 3; annex Appendix A lists 7 / 3 (adding §10 Silver Tier guidance). Annex Appendix A has no heading of its own (A.1 follows §10 directly) |
| Summary of Changes #6 vs Annex §6.2, A.1 | Latency budget clarification is Informative in the specification's change table and Normative in the annex; the annex prevails (Summary of Changes note) |
| Annex §8 | Benchmark figures are reported for `vcp-core-py` / `vcp-core-cpp` v1.2.0, which are not publicly available; the figures cannot be reproduced from published artifacts and are informative only (§8.2) |

## Relationship to VAP

VCP v1.2 is the reference profile for [VAP v1.2](https://github.com/veritaschain/vap-spec/tree/main/spec/v1.2) (VAP §5.1; VSO-VAP-CHANGE-001 Annex A). VAP and VCP version numbers are assigned independently; the matching "1.2" is coincidental (VAP §10.4).

## Relationship to v1.1

v1.2 does not restructure the protocol. It extends v1.1 with the changes listed above. To migrate from v1.1, see Section 10.4 of the specification; no data migration is required.

---

<p align="center">
  <strong>VeritasChain Standards Organization (VSO)</strong><br/>
  <em>"Verify, Don't Trust"</em><br/>
  <a href="https://veritaschain.org">veritaschain.org</a>
</p>
