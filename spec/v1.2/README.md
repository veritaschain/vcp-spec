# VCP Specification v1.2

**VeritasChain Protocol (VCP)** — The open standard for cryptographic audit trails in algorithmic trading systems.

> *"Verify, Don't Trust"*

---

## Status

**Release Candidate (RC1)** — 2026-05-31.

v1.2 is a **protocol-compatible / certification-stricter** update over v1.1. It introduces **zero breaking changes**: all v1.0 and v1.1 events remain valid and verifiable under v1.2. The complete normative specification of every change is defined in the normative annex VSO-SPEC-CHANGE-001, which is **not yet published in this repository** (see Documents below).

A Release Candidate is feature-complete and published for final review; it is not a Released version (VAP v1.2 §4.5.2 status vocabulary).

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
| 6 | Latency budget clarification | Informative | §6 |
| 7 | Anchor target continuity plan | Normative | §7 |
| 8 | Reference implementation benchmarks | Informative | §8 |
| 9 | Multi-actor chain linking (cross-party VCP-XREF) | Normative (when used) | §9 |

**Certification:** VC-Certified v1.2 additionally requires the strengthened VCP-RECOVERY constraints and a documented anchor continuity plan. v1.0/v1.1-certified implementations remain protocol-compatible but must meet these constraints for v1.2 certification.

**Post-quantum:** `DILITHIUM2` (ML-DSA / FIPS 204) and `FALCON512` (FN-DSA / FIPS 206 draft) advance from *FUTURE* to *EXPERIMENTAL*. `Ed25519` remains the DEFAULT; PQC is not yet a certification requirement.

## Documents

| Language | File | Status |
|----------|------|--------|
| 🇬🇧 English | [VCP-Specification-v1_2_en.md](VCP-Specification-v1_2_en.md) | Release Candidate (normative) |
| 📎 Change Proposal (normative annex) | VSO-SPEC-CHANGE-001.md | **Not yet published in this repository** — referenced by the RC1 text as "included in this directory" |
| 🇯🇵 日本語 | [VCP-Specification-v1_2_ja.md](VCP-Specification-v1_2_ja.md) | Translation of RC1 (convenience only; English prevails) |
| 🇨🇳 中文 | [VCP-Specification-v1_2_zh.md](VCP-Specification-v1_2_zh.md) | Translation of RC1 (convenience only; English prevails) |
| 📄 PDF | VCP-Specification-v1_2_en.pdf | Planned |

## Three-Layer Architecture

The three-layer integrity architecture introduced in v1.1 (Layer 1 Event Integrity, Layer 2 Collection Integrity / Merkle Tree, Layer 3 External Verifiability) is **unchanged** in v1.2. See Section 6 of the specification for details.

## Known issues in RC1 (informative)

The RC1 text is unchanged; these will be addressed in the next revision.

| Location | Issue |
|----------|-------|
| Summary of Changes; §12 "VSO Normative Annexes" | `VSO-SPEC-CHANGE-001.md` is referenced as included in this directory but is not yet published |
| §12 References | `draft-ietf-scitt-architecture` and `draft-ietf-cose-merkle-tree-proofs` are now **RFC 9943** and **RFC 9942** (June 2026) |
| §6.3.3 Attested Database Examples | AWS QLDB reached end of support on 2025-07-31 |
| §6.3.1 table | DILITHIUM2 / FALCON512 still shown as "Future (reserved)", while §1.4 and §1.5.1 give their v1.2 status as EXPERIMENTAL; §1.5.1 prevails |
| §1.1 | "immutable" and "ensuring compliance with international regulations" — the property provided is tamper-evidence, and conformance does not constitute compliance (VAP v1.2 §1.6) |
| §3.2.2 | ERASURE described as "a new immutable event" — append-only, tamper-evident |

## Relationship to VAP

VCP v1.2 RC1 is the reference profile for [VAP v1.2](https://github.com/veritaschain/vap-spec/tree/main/spec/v1.2) (VAP §5.1; VSO-VAP-CHANGE-001 Annex A). VAP and VCP version numbers are assigned independently; the matching "1.2" is coincidental (VAP §10.4).

## Relationship to v1.1

v1.2 does not restructure the protocol. It extends v1.1 with the changes listed above. To migrate from v1.1, see Section 10.4 of the specification; no data migration is required.

---

<p align="center">
  <strong>VeritasChain Standards Organization (VSO)</strong><br/>
  <em>"Verify, Don't Trust"</em><br/>
  <a href="https://veritaschain.org">veritaschain.org</a>
</p>
