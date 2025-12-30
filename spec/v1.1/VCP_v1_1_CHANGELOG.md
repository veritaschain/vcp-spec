# VCP v1.1 Changelog: Complete List of Changes from v1.0

**Document ID:** VSO-CHANGELOG-v1.1  
**Date:** December 2025  
**Status:** Final  
**Maintainer:** VeritasChain Standards Organization (VSO)

---

---

> **Definition (v1.1):** *Completeness Guarantees* ensure that any omission of required events is cryptographically detectable by third parties, not merely that recorded events were not altered.

---

## Executive Summary

VCP v1.1 introduces **5 major changes** and **11 minor enhancements** to strengthen external verifiability, improve implementation clarity, and add new capabilities for multi-party verification.

> **Core Enhancement:** VCP v1.1 extends tamper-evidence to **completeness guarantees**, enabling third parties to cryptographically verify not only that events were not altered, but that **no required events were omitted**.

| Category | Count | Impact |
|----------|-------|--------|
| Breaking Changes (Certification-level) | 2 | Silver tier implementations need updates |
| Major New Features | 3 | New sections added |
| Clarifications & Enhancements | 11 | Improved guidance and definitions |

---

## Compatibility Summary

| Change | Protocol Compatibility | Certification Impact |
|--------|----------------------|---------------------|
| PrevHash → OPTIONAL | ✅ Fully compatible | No impact (relaxation) |
| External Anchor → REQUIRED | ✅ Fully compatible | ⚠️ Silver tier must add anchoring |
| Policy Identification → REQUIRED | ✅ Fully compatible | ⚠️ All tiers must add field |
| VCP-XREF added | ✅ Fully compatible | No impact (OPTIONAL) |
| Three-Layer Architecture | ✅ Fully compatible | Documentation only |

**Summary**: Existing v1.0 implementations remain **protocol-compatible**, but may require additional components to obtain **v1.1 VC-Certified status**.

> ※ v1.1 is a **protocol-compatible / certification-stricter** update.

---

## Major Changes

### 1. Three-Layer Architecture (Section 6.0 - NEW)

**Type:** Structural Clarification  
**Impact:** Documentation only

Introduced clear three-layer architecture for integrity and security:

```
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 3: External Verifiability                                    │
│  ├─ Digital Signature: REQUIRED                                     │
│  ├─ Timestamp (dual format): REQUIRED                               │
│  └─ External Anchor: REQUIRED (Tier-dependent frequency)            │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 2: Collection Integrity    ← Core for external verifiability │
│  ├─ Merkle Tree (RFC 6962): REQUIRED                                │
│  ├─ Merkle Root: REQUIRED                                           │
│  └─ Audit Path: REQUIRED                                            │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 1: Event Integrity                                           │
│  ├─ EventHash: REQUIRED                                             │
│  └─ PrevHash (hash chain): OPTIONAL                                 │
└─────────────────────────────────────────────────────────────────────┘
```

**Rationale:** Clarifies the relationship between different cryptographic mechanisms and where integrity guarantees originate.

---

### 2. PrevHash Changed from REQUIRED to OPTIONAL (Section 6.1.2)

**Type:** Requirement Relaxation  
**Impact:** Simplifies Silver tier implementations

| Version | PrevHash Requirement |
|---------|---------------------|
| v1.0 | REQUIRED (except for INIT events) |
| v1.1 | **OPTIONAL** |

**Rationale:** 
- PrevHash-based hash chaining was REQUIRED in v1.0 to prioritize real-time, in-process tamper detection
- In v1.1, equivalent or stronger integrity guarantees are achieved through Merkle-based collection integrity (Layer 2) combined with mandatory external anchoring (Layer 3)
- Implementations targeting regulatory use cases (MiFID II RTS 25, SEC CAT) SHOULD still enable hash chains

**Related Test Changes:**
- HCH-001 (Genesis event prev_hash): Changed from Critical to **Removed**
- HCH-002 (Hash chain enabled): Added as **Non-Critical** test

---

### 3. External Anchor Changed from OPTIONAL to REQUIRED for All Tiers (Section 6.3.3)

**Type:** Requirement Strengthening  
**Impact:** Silver tier implementations must add anchoring

| Tier | v1.0 | v1.1 |
|------|------|------|
| Platinum | Required (10 min) | Required (10 min) |
| Gold | Recommended (1 hr) | **Required (1 hr)** |
| Silver | Optional (24 hr) | **Required (24 hr)** |

**Rationale:** Without external anchoring, log producers could retroactively modify Merkle Roots, undermining "Verify, Don't Trust" principle.

**Lightweight Options for Silver:**
- OpenTimestamps (free, Bitcoin-backed)
- FreeTSA (free RFC 3161)
- OriginStamp (commercial with free tier)

---

### 4. Policy Identification Added (Section 5.5 - NEW)

**Type:** New Mandatory Feature  
**Impact:** All tiers must implement

Every VCP event must now explicitly declare its conformance tier and registration policy:

```json
{
  "PolicyIdentification": {
    "Version": "1.1",
    "PolicyID": "org.veritaschain.prod:hft-system-001",
    "ConformanceTier": "PLATINUM",
    "RegistrationPolicy": {
      "Issuer": "VeritasChain Inc.",
      "PolicyURI": "https://veritaschain.org/policies/prod-hft"
    },
    "VerificationDepth": {
      "HashChainValidation": true,
      "MerkleProofRequired": true,
      "ExternalAnchorRequired": true
    }
  }
}
```

**PolicyID Naming Convention (Section 5.5.4):**
```
PolicyID = <reverse_domain>:<local_identifier>

Examples:
  org.veritaschain.prod:hft-system-001
  com.example.trading:gold-algo-v2
```

**Rationale:** Enables verifiers to apply appropriate validation rules and supports multi-tier deployments.

---

### 5. VCP-XREF Dual Logging Extension Added (Section 5.6 - NEW)

**Type:** New Optional Feature  
**Impact:** OPTIONAL extension module

Enables independent VCP event streams from multiple parties for cross-reference verification:

```
┌──────────────────┐          ┌──────────────────┐
│  Trading Algo    │─────────▶│     Broker       │
└────────┬─────────┘          └────────┬─────────┘
         │                             │
         ▼                             ▼
┌──────────────────┐          ┌──────────────────┐
│   VCP Sidecar    │          │   Broker VCP     │
│  (Trader-side)   │          │  (Broker-side)   │
└────────┬─────────┘          └────────┬─────────┘
         │                             │
         └───────────┬─────────────────┘
                     ▼
              Cross-Reference
               Verification
```

**Use Cases:**
| Scenario | Party A | Party B |
|----------|---------|---------|
| Prop Firm Trading | Trader | Prop Firm |
| Broker Execution | Algo Provider | Broker |
| Multi-Venue | Smart Order Router | Exchange |

**Security Guarantee:** Unless both parties collude AND compromise external anchors, manipulation is detectable.

---

## Minor Changes & Enhancements

### 6. Attested Database Requirements Defined (Section 6.3.3)

**Type:** Definition Clarification

Added minimum criteria for "Attested Database" to qualify as anchor target:

| Criterion | Requirement |
|-----------|-------------|
| Third-Party Audit | Annual audit by independent party |
| Tamper Detection | Cryptographic integrity checks |
| Access Controls | SOC 2 Type II or equivalent |
| Retention Policy | ≥ 7 years |
| Availability SLA | ≥ 99.9% uptime |

**Examples Added:**
| Example | Attestation Level |
|---------|------------------|
| AWS QLDB + SOC 2 Type II | High |
| Azure SQL Ledger + SOC 2 | High |
| Self-hosted PostgreSQL + annual crypto audit | Medium |
| Internal database without attestation | **Not acceptable** |

---

### 7. Anchor Target Unavailability Handling (Section 6.3.3)

**Type:** New Guidance

Added requirements for handling anchor target unavailability:

| Scenario | Required Action |
|----------|-----------------|
| Temporary outage | Queue requests; retry with exponential backoff |
| Permanent discontinuation | Migrate to alternative within 30 days |
| Verification failure | Retain local AnchorRecord copy as backup |

---

### 8. Silver Tier Semi-Regulatory Use Guidance (Section 2.2.3)

**Type:** Clarification

Added guidance for Silver tier logs used in semi-regulatory contexts:

| Aspect | Silver Capability | Assurance Level |
|--------|------------------|-----------------|
| Timestamp accuracy | BEST_EFFORT | Indicative only |
| Event completeness | Daily anchor | Gaps possible within 24h |
| Chain continuity | PrevHash OPTIONAL | No real-time detection unless enabled |

**Intraday Anchoring Recommendation:**
> For higher assurance within the 24-hour window, implementations MAY perform intraday manual anchoring (e.g., at end of trading session) or reduce the anchor interval to 12 hours.

---

### 9. Silver Tier Merkle Proof Clarification (Section 9.1.1)

**Type:** Clarification

Clarified that Silver tier:
- Per-event audit path **storage** MAY be omitted
- However, MUST retain sufficient data to **generate audit paths on-demand** when requested for audit

---

### 10. ClockSyncStatus Usage in Regulatory Context (Section 8.1 - NEW)

**Type:** New Guidance

Added guidance on interpreting ClockSyncStatus for compliance:

| ClockSyncStatus | Regulatory Interpretation |
|-----------------|--------------------------|
| PTP_LOCKED | Authoritative; suitable for latency disputes |
| NTP_SYNCED | Reliable; suitable for order sequencing |
| BEST_EFFORT | Indicative; not suitable for precise sequencing |
| UNRELIABLE | Development/testing only |

---

### 11. Certification Governance Section (Section 9.2 - NEW)

**Type:** Governance Clarification

Explicitly documented CAB (Conformity Assessment Body) model:

```
VSO (Scheme Owner)
  │
  │  Accreditation
  ▼
Accredited CABs (multiple)
  │
  │  Certification
  ▼
VCP Adopters
```

Reference to VSO-GOV-SCHEME-001 for detailed governance structure.

---

### 12. Non-Critical Tests Added (Section 9.1.3 - NEW)

**Type:** Testing Enhancement

Added non-critical tests that don't cause certification failure but are reported:

| Test ID | Description | Notes |
|---------|-------------|-------|
| HCH-002 | Hash chain enabled (PrevHash) | For RTS25/CAT alignment |
| ANC-002 | Anchoring delay threshold | Warning >threshold, violation at 2x |
| ANC-003 | Anchor target availability | Backup recommended |
| CLK-001 | Clock sync status consistency | Tier-dependent |
| XREF-001 | Cross-reference ID uniqueness | If VCP-XREF enabled |
| XREF-002 | Cross-reference reconciliation | If VCP-XREF enabled |

---

### 13. Critical Tests Updated (Section 9.1.2)

**Type:** Testing Enhancement

| Test ID | Description | v1.0 | v1.1 |
|---------|-------------|------|------|
| HCH-001 | Genesis event prev_hash | Critical | **Removed** |
| HCH-003 | Hash calculation algorithm | Critical | Critical (EventHash only) |
| MKL-001 | Merkle tree construction | - | **Critical (New)** |
| MKL-002 | Merkle proof verification | - | **Critical (New)** |
| ANC-001 | External anchor presence | - | **Critical (New)** |
| POL-001 | Policy Identification | - | **Critical (New)** |

---

### 14. Post-Quantum Cryptography Migration Guidance (Appendix E - NEW)

**Type:** Non-Normative Guidance

Added advisory appendix for PQC migration:

**Dual Signature Strategy:**
```json
{
  "Signature": "base64(Ed25519_signature)",
  "SignAlgo": "ED25519",
  "PQCSignature": "base64(Dilithium2_signature)",
  "PQCSignAlgo": "DILITHIUM2"
}
```

**Recommended Timeline:**
| Phase | Timeline | Action |
|-------|----------|--------|
| Preparation | 2025-2026 | Implement dual-signature capability |
| Hybrid | 2027-2029 | Deploy dual signatures |
| Transition | 2030+ | Phase out classical-only |

---

### 15. Security Object Schema Updated (Section 6.4)

**Type:** Schema Change

| Field | v1.0 | v1.1 |
|-------|------|------|
| EventHash | REQUIRED | REQUIRED |
| PrevHash | REQUIRED (except INIT) | **OPTIONAL** |
| MerkleRoot | OPTIONAL (Gold/Platinum) | **REQUIRED** |
| MerkleIndex | OPTIONAL | **REQUIRED** |
| AnchorReference | OPTIONAL | **REQUIRED** |

---

### 16. Core Modules List Updated (Section 1.6)

**Type:** Documentation

Added new module to core modules list:
- **VCP-XREF**: Cross-reference and dual logging (NEW in v1.1)

---

## Migration Guide Summary

### For Silver Tier

| Action | Priority | Deadline |
|--------|----------|----------|
| Add External Anchoring (daily) | **Required** | June 2026 |
| Add Policy Identification | **Required** | March 2026 |
| Generate audit paths on-demand | **Required** | March 2026 |
| Consider intraday anchoring | Recommended | - |
| Enable hash chain (PrevHash) | Optional | - |
| Implement VCP-XREF | Optional | - |

### For Gold Tier

| Action | Priority | Deadline |
|--------|----------|----------|
| Add Policy Identification | **Required** | March 2026 |
| Verify anchoring frequency (1 hr) | **Required** | Immediate |
| Enable hash chain (PrevHash) | Recommended | - |
| Implement VCP-XREF | Optional | - |

### For Platinum Tier

| Action | Priority | Deadline |
|--------|----------|----------|
| Add Policy Identification | **Required** | March 2026 |
| Verify anchoring frequency (10 min) | **Required** | Immediate |
| Enable hash chain (PrevHash) | Recommended | - |
| Consider PQC dual signatures | Optional | - |
| Implement VCP-XREF | Optional | - |

---

## Grace Period

| Requirement | Grace Period | Hard Deadline |
|-------------|--------------|---------------|
| External Anchor (Silver) | 6 months | 2026-06-25 |
| Policy Identification | 3 months | 2026-03-25 |
| Merkle fields in Security | 3 months | 2026-03-25 |

After the hard deadline, v1.0-only implementations will not receive VC-Certified status for new certifications.

---

## Document Statistics

| Metric | v1.0 | v1.1 | Change |
|--------|------|------|--------|
| Total Lines | 1024 | 1431 | +407 (+40%) |
| Sections | 12 | 12 | - |
| Subsections | ~50 | ~70 | +20 |
| Extension Modules | 5 | 6 | +1 (VCP-XREF) |
| Appendices | 3 | 5 | +2 (D, E) |
| Test Categories | ~15 | ~21 | +6 |

---

## Related Documents

| Document ID | Title | Status |
|-------------|-------|--------|
| VSO-SPEC-v1.1 | VCP Specification v1.1 | DRAFT |
| VSO-GOV-SCHEME-001 | VC-Certified Scheme Governance | v1.0 |
| VSO-CAB-REQ-001 | CAB Accreditation Requirements | Planned |
| draft-kamimura-scitt-vcp-02 | IETF Internet-Draft | Planned |

---

## Acknowledgments

v1.1 changes incorporate feedback from:
- Dick Brooks (IETF SCITT WG - Policy Identification)
- Community reviewers (External Anchor requirements)
- Implementation teams (Silver tier simplification)
- Regulatory consultants (ClockSyncStatus guidance)

---

*Copyright © 2025 VeritasChain Standards Organization. Licensed under CC BY 4.0.*
