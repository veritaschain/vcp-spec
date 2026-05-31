# VCP Specification v1.2

**VeritasChain Protocol (VCP)** — The open standard for cryptographic audit trails in algorithmic trading systems.

> *"Verify, Don't Trust"*

---

## Status

**Release Candidate (RC1)** — 2026-05-31.

v1.2 is a **protocol-compatible / certification-stricter** update over v1.1. It introduces **zero breaking changes**: all v1.0 and v1.1 events remain valid and verifiable under v1.2. The complete normative specification of every change is provided in this directory as a normative annex (see Documents below).

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
| 🇬🇧 English | [VCP-Specification-v1_2_en.md](VCP-Specification-v1_2_en.md) | Release Candidate |
| 📎 Change Proposal (normative annex) | [VSO-SPEC-CHANGE-001.md](VSO-SPEC-CHANGE-001.md) | Adopted into v1.2 (Rev. 3) |
| 🇯🇵 日本語 | VCP-Specification-v1_2_ja.md | Planned (after EN finalization) |
| 🇨🇳 中文 | VCP-Specification-v1_2_zh.md | Planned (after EN finalization) |
| 📄 PDF | VCP-Specification-v1_2_en.pdf | Planned |

## Three-Layer Architecture

The three-layer integrity architecture introduced in v1.1 (Layer 1 Event Integrity, Layer 2 Collection Integrity / Merkle Tree, Layer 3 External Verifiability) is **unchanged** in v1.2. See Section 6 of the specification for details.

## Relationship to v1.1

v1.2 does not restructure the protocol. It extends v1.1 with the changes listed above. To migrate from v1.1, see Section 10.4 of the specification; no data migration is required.

---

<p align="center">
  <strong>VeritasChain Standards Organization (VSO)</strong><br/>
  <em>"Verify, Don't Trust"</em><br/>
  <a href="https://veritaschain.org">veritaschain.org</a>
</p>
