# VCP v1.2 Change Proposal

## VeritasChain Protocol Specification Update

**Document ID:** VSO-SPEC-CHANGE-001  
**Status:** ADOPTED (Revision 3) — Normative Annex to VCP v1.2  
**Date:** 2026-01-06  
**Target Version:** 1.2  
**Adopted:** 2026-05-31 (v1.2 RC1); GA 2026-07-06  
**Maintainer:** VeritasChain Standards Organization (VSO)  
**License:** CC BY 4.0 International

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.2-draft-03 | 2026-01-06 | Silver Tier implementation guidance, CAB audit requirements for Emergency Override, Failover automation criteria, Implementation cost estimates, Phased adoption roadmap |
| 1.2-draft-02 | 2026-01-06 | Normative count fixed, blockchain criteria harmonized, CHECKPOINT emergency override added, tier-specific RTO/RPO, privacy guidance for ERASURE |
| 1.2-draft-01 | 2026-01-06 | Initial draft with all 9 proposed changes |

---

## Executive Summary

VCP v1.2 is a **Protocol-Compatible / Certification-Stricter** update that addresses community feedback, strengthens operational clarity, and aligns with IETF SCITT standardization efforts. This document specifies all proposed changes for v1.2.

### Change Classification

| Category | Count | Impact |
|----------|-------|--------|
| Normative (REQUIRED) | 7 | Certification requirements tightened |
| Informative (RECOMMENDED) | 2 | Documentation improvements |
| Breaking Changes | 0 | Full backward compatibility maintained |

> **Note**: Multi-Actor Chain Linking (§9) is classified as Normative because when used, it imposes MUST-level requirements. However, its adoption remains OPTIONAL.

---

## Table of Contents

1. [VCP-RECOVERY Constraint Strengthening](#1-vcp-recovery-constraint-strengthening)
2. [External Anchor Blockchain Selection Criteria](#2-external-anchor-blockchain-selection-criteria)
3. [ERASURE Event Type Specification](#3-erasure-event-type-specification)
4. [Version Compatibility Matrix](#4-version-compatibility-matrix)
5. [SCITT Alignment Fields](#5-scitt-alignment-fields)
6. [Latency Budget Clarification](#6-latency-budget-clarification)
7. [Anchor Target Continuity Plan](#7-anchor-target-continuity-plan)
8. [Reference Implementation Benchmarks](#8-reference-implementation-benchmarks)
9. [Multi-Actor Chain Linking Extension](#9-multi-actor-chain-linking-extension)
10. [Silver Tier Implementation Guidance](#10-silver-tier-implementation-guidance)

---

## 1. VCP-RECOVERY Constraint Strengthening

### 1.1 Purpose

VCP v1.0/v1.1 defined VCP-RECOVERY with generic `RecoveryType` and `RecoveryAction` enumerations but lacked operational constraints. This update defines strict boundaries for each recovery operation to prevent abuse and ensure audit trail integrity.

### 1.2 Change Type

**Normative** — Affects VC-Certified compliance requirements.

### 1.3 Current State (v1.1)

```json
{
  "VCP-RECOVERY": {
    "RecoveryType": "enum",    // CHAIN_BREAK | FORK | REORG | CHECKPOINT
    "RecoveryAction": {
      "Method": "enum"         // REBUILD | SKIP | MERGE | CHECKPOINT
    }
  }
}
```

**Problem**: No constraints on how many events can be skipped, how far back rebuilds can reach, or what conditions permit each action.

### 1.4 Proposed Change (v1.2)

#### 1.4.1 RecoveryType Constraints

| RecoveryType | Definition | Trigger Conditions | Max Duration |
|--------------|------------|-------------------|--------------|
| **CHAIN_BREAK** | Hash chain continuity lost | System crash, storage corruption | N/A |
| **FORK** | Divergent chains detected | Multi-instance conflict | Must resolve within 1 anchor cycle |
| **REORG** | Event reordering required | Out-of-order delivery | Max 100 events |
| **CHECKPOINT** | Intentional chain reset | Scheduled maintenance, migration | See §1.4.6 for notice requirements |

#### 1.4.2 RecoveryAction Constraints

| Method | Permitted Scope | REQUIRED Conditions | Audit Requirements |
|--------|-----------------|---------------------|-------------------|
| **SKIP** | Max N events (tier-dependent) | Must not cross anchor boundary | `SkippedEventIDs` REQUIRED |
| **REBUILD** | From last valid anchor only | External anchor verification REQUIRED | `RebuildSourceAnchor` REQUIRED |
| **MERGE** | Same session only | Timestamp consistency check REQUIRED | `MergedChainIDs` REQUIRED |
| **CHECKPOINT** | Any point | See §1.4.6 | Pre-announcement or EmergencyOverride REQUIRED |

#### 1.4.3 Tier-Specific SKIP Limits

| Tier | Max Skippable Events | Max Skip Duration | Anchor Boundary Rule |
|------|---------------------|-------------------|---------------------|
| **Platinum** | 10 events | 1 second | MUST NOT cross 10-min anchor |
| **Gold** | 100 events | 1 minute | MUST NOT cross 1-hour anchor |
| **Silver** | 1,000 events | 1 hour | MUST NOT cross 24-hour anchor |

#### 1.4.4 Updated Schema

```json
{
  "VCP-RECOVERY": {
    "Version": "1.2",
    "RecoveryType": "enum",
    "RecoveryConstraints": {
      "MaxSkipEvents": "int32",
      "MaxSkipDuration": "int64",
      "AnchorBoundaryEnforced": "boolean"
    },
    "BreakPoint": {
      "LastValidEventID": "uuid",
      "LastValidHash": "string",
      "LastValidAnchorID": "string",
      "BreakTimestamp": "int64",
      "BreakReason": "string"
    },
    "RecoveryAction": {
      "Method": "enum",
      "SkippedEventIDs": ["uuid"],
      "RebuildSourceAnchor": "string",
      "MergedChainIDs": ["string"],
      "RecoveredEvents": "int32",
      "ValidationMethod": "string",
      "OperatorID": "string",
      "PreAnnouncementEventID": "uuid",
      "EmergencyOverride": {
        "IsEmergency": "boolean",
        "EmergencyJustification": "string",
        "ApprovalChain": [
          {
            "ApproverRoleID": "string",
            "ApproverSignature": "string",
            "ApprovalTimestamp": "int64"
          }
        ],
        "IncidentReference": "string"
      }
    },
    "ChainValidation": {
      "PreBreakHash": "string",
      "PostRecoveryHash": "string",
      "MerkleProof": ["string"],
      "AnchorReference": "string",
      "AnchorVerificationTimestamp": "int64"
    }
  }
}
```

#### 1.4.5 Recovery Event Sequence (Normal)

```
┌─────────────────────────────────────────────────────────────────────┐
│  CHECKPOINT Recovery Flow (Normal - 24h Advance Notice)            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  T-24h: RECOVERY_ANNOUNCE event                                     │
│         {                                                           │
│           "EventType": "SYS_RECOVERY_ANNOUNCE",                    │
│           "PlannedRecoveryType": "CHECKPOINT",                     │
│           "ScheduledTime": "2026-01-07T00:00:00Z",                 │
│           "Reason": "Scheduled maintenance window",                │
│           "OperatorID": "ops-role-001"                             │
│         }                                                           │
│                                                                     │
│  T-0:   Last normal event before checkpoint                        │
│                                                                     │
│  T+0:   CHECKPOINT event                                           │
│         {                                                           │
│           "EventType": "SYS_CHECKPOINT",                           │
│           "VCP-RECOVERY": {                                        │
│             "EmergencyOverride": { "IsEmergency": false }          │
│           }                                                         │
│         }                                                           │
│                                                                     │
│  T+1:   First event in new chain segment                           │
│         (PrevHash references CHECKPOINT event)                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### 1.4.6 CHECKPOINT Notice Requirements (NEW in v1.2-draft-02)

| Scenario | Notice Requirement | Additional Requirements |
|----------|-------------------|------------------------|
| **Planned maintenance** | 24 hours advance `RECOVERY_ANNOUNCE` | None |
| **Planned migration** | 72 hours advance `RECOVERY_ANNOUNCE` | Migration plan documentation |
| **Emergency - Security incident** | No advance notice | EmergencyOverride REQUIRED |
| **Emergency - System failure** | No advance notice | EmergencyOverride REQUIRED |
| **Emergency - Regulatory order** | No advance notice | EmergencyOverride REQUIRED |

#### 1.4.7 Emergency Override Requirements (NEW in v1.2-draft-02)

When `EmergencyOverride.IsEmergency = true`, the following constraints apply:

| Requirement | Specification |
|-------------|---------------|
| **Minimum Approvers** | 2 (different individuals) |
| **Approver Role Level** | Senior Operator or above (org-defined) |
| **Justification** | REQUIRED, min 50 characters |
| **Incident Reference** | REQUIRED (ticket ID, case number, etc.) |
| **Post-Incident Review** | MUST be conducted within 72 hours |
| **Audit Trail** | All approval signatures cryptographically verifiable |

```
┌─────────────────────────────────────────────────────────────────────┐
│  CHECKPOINT Recovery Flow (Emergency Override)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  T-0:   Security incident detected                                 │
│                                                                     │
│  T+1m:  Emergency CHECKPOINT event (NO advance notice)             │
│         {                                                           │
│           "EventType": "SYS_CHECKPOINT",                           │
│           "VCP-RECOVERY": {                                        │
│             "EmergencyOverride": {                                 │
│               "IsEmergency": true,                                 │
│               "EmergencyJustification": "Critical security breach  │
│                 detected in signing key infrastructure. Immediate  │
│                 chain reset required to prevent further compromise.│
│                 See INC-2026-0106-001 for details.",               │
│               "ApprovalChain": [                                   │
│                 {                                                  │
│                   "ApproverRoleID": "security-lead-001",          │
│                   "ApproverSignature": "base64...",               │
│                   "ApprovalTimestamp": 1736150400000000           │
│                 },                                                 │
│                 {                                                  │
│                   "ApproverRoleID": "cto-001",                    │
│                   "ApproverSignature": "base64...",               │
│                   "ApprovalTimestamp": 1736150460000000           │
│                 }                                                  │
│               ],                                                   │
│               "IncidentReference": "INC-2026-0106-001"            │
│             }                                                      │
│           }                                                         │
│         }                                                           │
│                                                                     │
│  T+72h: Post-incident review MUST be completed                     │
│         → Review findings logged as SYS_AUDIT event                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### 1.4.8 Emergency Justification Categories

| Category | Code | Example Justification |
|----------|------|----------------------|
| **Security Incident** | SEC | Key compromise, unauthorized access, malware |
| **System Failure** | SYS | Unrecoverable hardware failure, data corruption |
| **Regulatory Order** | REG | Regulator-mandated immediate action |
| **Safety Critical** | SAF | Imminent risk to market integrity |

#### 1.4.9 CAB Audit Requirements for Emergency Override (NEW in v1.2-draft-03)

> **CRITICAL**: Emergency Override is a high-risk feature that, if misused, could enable concealment of fraudulent activity. Conformity Assessment Bodies (CABs) MUST treat Emergency Override logs as **priority audit items**.

**CAB Audit Checklist for Emergency Override:**

| Check Item | Verification Method | Severity |
|------------|-------------------|----------|
| **Approval Chain Completeness** | Verify ≥2 distinct ApproverRoleIDs with valid signatures | CRITICAL |
| **Justification Adequacy** | Review EmergencyJustification for specificity (min 50 chars, incident details) | CRITICAL |
| **Incident Reference Validity** | Cross-reference IncidentReference with external incident management system | HIGH |
| **Post-Incident Review** | Confirm SYS_AUDIT event logged within 72 hours | CRITICAL |
| **Frequency Analysis** | Flag if >2 Emergency Overrides in 90-day period | HIGH |
| **Temporal Proximity** | Flag if Emergency Override within 24h of disputed event | CRITICAL |

**Red Flags Requiring Escalation:**

```
┌─────────────────────────────────────────────────────────────────────┐
│  Emergency Override Red Flag Detection                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  🚨 IMMEDIATE ESCALATION (Certification at risk):                  │
│  ─────────────────────────────────────────────────                 │
│  □ Emergency Override used without subsequent Post-Incident Review │
│  □ Same ApproverRoleID appears in >1 approval (single-person)      │
│  □ IncidentReference does not match external records               │
│  □ Emergency Override coincides with customer dispute timeline     │
│                                                                     │
│  ⚠️ INVESTIGATION REQUIRED:                                        │
│  ─────────────────────────────                                     │
│  □ >3 Emergency Overrides in 180 days                              │
│  □ EmergencyJustification contains generic/templated text          │
│  □ Post-Incident Review findings not actioned                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**CAB Reporting Requirement:**

All Emergency Override instances MUST be documented in the annual VC-Certified audit report with:
1. Date and time of override
2. Justification category (SEC/SYS/REG/SAF)
3. Post-Incident Review outcome
4. Remediation actions taken

### 1.5 Migration Impact

| Existing Implementation | Required Action |
|------------------------|-----------------|
| v1.0/v1.1 without recovery | No action (recovery remains optional) |
| v1.0/v1.1 with recovery | Update to include new constraints for VC-Certified v1.2 |

---

## 2. External Anchor Blockchain Selection Criteria

### 2.1 Purpose

VCP v1.1 states "Blockchain (Ethereum, Bitcoin, etc.)" without defining selection criteria. This update provides normative requirements for acceptable blockchains and an informative list of current recommendations.

### 2.2 Change Type

**Normative** (selection criteria) + **Informative** (recommended list)

### 2.3 Normative Requirements

#### 2.3.1 Core Blockchain Requirements (All Classes)

All blockchain anchor targets MUST meet these minimum criteria:

| Criterion | Requirement | Rationale |
|-----------|-------------|-----------|
| **Finality Model** | Probabilistic or deterministic finality | Ensures anchor permanence |
| **Minimum Security** | 6 BTC-equivalent confirmations | Industry standard for irreversibility |
| **Decentralization** | ≥1,000 active validators/miners | Prevents single-party control |
| **Public Verifiability** | Permissionless read access | Third-party verification requirement |
| **Data Availability** | Full node archival available | Long-term proof retrieval |

> **Note (v1.2-draft-02)**: "Historical Availability" (operational history) is a **classification factor**, not a core requirement. See §2.3.2 for class-based treatment.

#### 2.3.2 Blockchain Classification (REVISED in v1.2-draft-02)

| Classification | Operational History | Additional Criteria | Tier Applicability |
|----------------|--------------------|--------------------|-------------------|
| **Class A** | ≥10 years | All core requirements + proven resilience through major events | Platinum, Gold, Silver |
| **Class B** | ≥5 years | All core requirements | Platinum, Gold, Silver |
| **Class C** | ≥2 years, <5 years | All core requirements + enhanced monitoring REQUIRED | Gold, Silver only |
| **Class D** | <2 years OR partial criteria | Case-by-case evaluation | Silver only with documented justification |
| **Not Acceptable** | Any | Private/consortium without public verification | None |

> **Rationale (v1.2-draft-02)**: The previous draft required "≥5 years" in core requirements while allowing Class C for "<5 years", creating a contradiction. This revision moves operational history to the classification system, where it affects tier applicability rather than blocking compliance entirely.

#### 2.3.3 Class C Enhanced Monitoring Requirements

When using a Class C blockchain, implementations MUST:

| Requirement | Specification |
|-------------|---------------|
| **Dual Anchoring** | RECOMMENDED to anchor to both Class C and Class A/B fallback |
| **Monitoring Frequency** | Check network health every anchor cycle |
| **Fallback Trigger** | Auto-switch if >3 consecutive anchor failures |
| **Documentation** | Maintain risk assessment for blockchain choice |

#### 2.3.4 Finality Calculation

```python
def calculate_equivalent_confirmations(blockchain: str, confirmations: int) -> float:
    """
    Calculate Bitcoin-equivalent confirmation depth.
    
    Reference: BTC 6 confirmations ≈ 60 minutes ≈ $500M+ attack cost (2026 estimate)
    """
    # Hashrate/stake-weighted security factor (relative to BTC)
    security_factors = {
        "bitcoin": 1.0,
        "ethereum": 0.8,      # Post-merge PoS
        "polygon_pos": 0.3,
        "arbitrum": 0.7,      # Inherits ETH security
        "solana": 0.4,
        "avalanche_c": 0.5
    }
    
    # Time to finality (minutes)
    finality_times = {
        "bitcoin": 60,        # 6 blocks × 10 min
        "ethereum": 15,       # 2 epochs × 6.4 min + buffer
        "polygon_pos": 30,    # ~128 blocks
        "arbitrum": 20,       # ETH finality + L2 delay
        "solana": 0.5,        # ~400ms slots
        "avalanche_c": 2      # Snowball consensus
    }
    
    factor = security_factors.get(blockchain.lower(), 0.1)
    return confirmations * factor
```

### 2.4 Informative Appendix: Recommended Blockchains (January 2026)

> **NOTE**: This appendix is INFORMATIVE and subject to change. VSO will publish updates at https://veritaschain.org/anchor-recommendations.

#### 2.4.1 Class A (Recommended for Platinum)

| Blockchain | Operational Since | Confirmations | Finality Time | Notes |
|------------|-------------------|---------------|---------------|-------|
| **Bitcoin** | 2009 | 6 | ~60 min | Highest security, highest cost |
| **Ethereum Mainnet** | 2015 | 2 epochs (64 blocks) | ~15 min | Native smart contract support |

#### 2.4.2 Class B (Acceptable for All Tiers)

| Blockchain | Operational Since | Confirmations | Finality Time | Notes |
|------------|-------------------|---------------|---------------|-------|
| **Polygon PoS** | 2020 | 128 | ~30 min | Lower cost, ETH-compatible |
| **Arbitrum One** | 2021 | 1 (after ETH finality) | ~20 min | ETH L2, inherits security |

#### 2.4.3 Class C (Gold/Silver Only, Enhanced Monitoring Required)

| Blockchain | Operational Since | Confirmations | Finality Time | Conditions |
|------------|-------------------|---------------|---------------|------------|
| **Base** | 2023 | 1 (after ETH finality) | ~20 min | ETH L2, Coinbase-operated |
| **Solana** | 2020 | 32 | ~15 sec | Monitor for network stability |
| **Avalanche C-Chain** | 2020 | 1 | ~2 sec | Fast finality, smaller validator set |

#### 2.4.4 Non-Blockchain Alternatives

| Target | Class Equivalent | Notes |
|--------|------------------|-------|
| **RFC 3161 TSA** (DigiCert, GlobalSign) | B | Traditional PKI, regulatory familiar |
| **OpenTimestamps** | B | Free, Bitcoin-backed |
| **AWS QLDB + SOC 2** | C | Attested database, enterprise option |

### 2.5 Schema Update

```json
{
  "AnchorTarget": {
    "Type": "enum",           // BLOCKCHAIN | TSA | DATABASE | PUBLIC_SERVICE
    "Identifier": "string",   // Chain ID, TSA URL, etc.
    "Classification": "enum", // CLASS_A | CLASS_B | CLASS_C | CLASS_D
    "Proof": "string",        // Transaction hash, TSA token, etc.
    "Confirmations": "int32", // Number of confirmations at anchor time
    "FinalityTimestamp": "int64",  // When finality was achieved
    "VerificationURL": "string",   // Public explorer/verification endpoint
    "EnhancedMonitoring": {        // REQUIRED for Class C/D
      "Enabled": "boolean",
      "FallbackTarget": "string",
      "LastHealthCheck": "int64"
    }
  }
}
```

---

## 3. ERASURE Event Type Specification

### 3.1 Purpose

VCP-PRIVACY defines crypto-shredding conceptually, but lacks a formal event type for recording and verifying erasure operations. This update introduces the `ERASURE` event type for GDPR Article 17 compliance with auditor-verifiable proof.

### 3.2 Change Type

**Normative** — New event type addition.

### 3.3 Background

**The GDPR-Immutability Paradox:**
- GDPR Article 17: Right to erasure ("right to be forgotten")
- MiFID II Article 16(7): 5-7 year record retention requirement
- Cryptographic audit trails: Immutability by design

**Resolution:** Crypto-shredding encrypts personal data with per-subject keys. Key destruction renders data computationally inaccessible while preserving hash chain integrity. The ERASURE event provides verifiable proof of this process.

### 3.4 ERASURE Event Schema

```json
{
  "Header": {
    "EventID": "uuid-v7",
    "EventType": "ERASURE",
    "Timestamp": "int64",
    "TimestampISO": "string"
  },
  "ErasureDetails": {
    "Version": "1.2",
    "TargetIdentifier": {
      "Type": "enum",                    // ACCOUNT | SESSION | EVENT_RANGE
      "Hash": "string",                  // SHA-256 hash of original identifier
      "Salt": "string"                   // Per-erasure salt for privacy
    },
    "Scope": {
      "AffectedEventCount": "int32",
      "FirstAffectedEventID": "uuid",
      "LastAffectedEventID": "uuid",
      "AffectedFields": ["string"]       // e.g., ["ClientID", "AccountID"]
    },
    "Reason": {
      "Code": "enum",                    // See 3.4.1
      "Description": "string",
      "LegalBasis": "string",            // e.g., "GDPR Art. 17(1)(a)"
      "RequestReferenceHash": "string"   // REVISED: Hash of ticket/case number
    },
    "Authorization": {
      "AuthorizedByRoleID": "string",    // REVISED: Role ID, not personal name
      "AuthorizerSignature": "string",   // Cryptographic signature
      "AuthorizationTimestamp": "int64",
      "ApprovalChain": [                 // For multi-party approval
        {
          "ApproverRoleID": "string",
          "ApproverSignature": "string",
          "ApprovalTimestamp": "int64"
        }
      ],
      "DPONotified": "boolean"           // Data Protection Officer notification
    },
    "CryptoShredding": {
      "KeyIDHash": "string",             // SHA-256 of destroyed key ID
      "KeyAlgorithm": "string",          // e.g., "AES-256-GCM"
      "DestructionMethod": "enum",       // HSM_ZEROIZE | SECURE_DELETE | CLOUD_KMS_DESTROY
      "DestructionTimestamp": "int64",
      "DestructionCertificate": "string" // HSM attestation if available
    },
    "Verification": {
      "PreErasureEventHash": "string",   // Hash of last affected event
      "PostErasureChainHash": "string",  // Hash proving chain continuity
      "MerkleProof": ["string"],         // Inclusion proof for ERASURE event
      "VerificationEndpoint": "string"   // URL for third-party verification
    }
  }
}
```

#### 3.4.1 Erasure Reason Codes

| Code | Description | Legal Basis | Retention Override |
|------|-------------|-------------|-------------------|
| **GDPR_ART_17_1A** | Consent withdrawn | GDPR Art. 17(1)(a) | After retention period |
| **GDPR_ART_17_1B** | Purpose fulfilled | GDPR Art. 17(1)(b) | After retention period |
| **GDPR_ART_17_1C** | Objection (no override) | GDPR Art. 17(1)(c) | After retention period |
| **GDPR_ART_17_1D** | Unlawful processing | GDPR Art. 17(1)(d) | Immediate |
| **RETENTION_EXPIRED** | Legal retention period ended | MiFID II Art. 16(7) | N/A |
| **SUBJECT_REQUEST** | Data subject request (non-GDPR) | PDPA, CCPA, etc. | Jurisdiction-dependent |
| **COURT_ORDER** | Legal requirement to delete | Varies | Immediate |
| **ERROR_CORRECTION** | Erroneous data recorded | GDPR Art. 16 | Immediate |

#### 3.4.2 Destruction Method Requirements

| Method | Tier Applicability | Verification |
|--------|-------------------|--------------|
| **HSM_ZEROIZE** | Platinum, Gold | HSM audit log + attestation |
| **SECURE_DELETE** | Gold, Silver | Software verification + timestamp |
| **CLOUD_KMS_DESTROY** | All tiers | Cloud provider deletion confirmation |

### 3.5 Privacy Guidance for ERASURE Events (NEW in v1.2-draft-02)

> **IMPORTANT**: ERASURE events themselves may inadvertently contain personal data. Follow these guidelines:

| Field | Privacy Risk | Recommendation |
|-------|-------------|----------------|
| `TargetIdentifier.Hash` | Low (hashed) | ✅ Use SHA-256 with per-erasure salt |
| `Reason.RequestReferenceHash` | Medium | ✅ Hash external ticket IDs; do not store plaintext |
| `Authorization.AuthorizedByRoleID` | Medium | ✅ Use role identifiers (e.g., "dpo-001"), not personal names |
| `Authorization.ApprovalChain` | Medium | ✅ Use role IDs with cryptographic signatures |
| `Reason.Description` | High | ⚠️ Avoid including data subject names or identifiers |

**Implementation Pattern:**

```python
def create_erasure_event(
    request_ticket: str,
    authorizer_email: str,
    subject_account_id: str
) -> dict:
    """
    Create ERASURE event with privacy-preserving identifiers.
    """
    import hashlib
    import secrets
    
    # Generate per-erasure salt
    salt = secrets.token_hex(16)
    
    return {
        "ErasureDetails": {
            "TargetIdentifier": {
                "Type": "ACCOUNT",
                # Hash the account ID with salt
                "Hash": hashlib.sha256(
                    f"{subject_account_id}:{salt}".encode()
                ).hexdigest(),
                "Salt": salt
            },
            "Reason": {
                "Code": "GDPR_ART_17_1A",
                "Description": "Consent withdrawn by data subject",  # No PII
                # Hash the ticket reference
                "RequestReferenceHash": hashlib.sha256(
                    request_ticket.encode()
                ).hexdigest()
            },
            "Authorization": {
                # Use role ID, not email/name
                "AuthorizedByRoleID": "dpo-eu-001",
                "AuthorizerSignature": sign_with_role_key("dpo-eu-001", ...),
                # ...
            }
        }
    }
```

### 3.6 Auditor Verification Process

```python
def verify_erasure_event(
    erasure_event: dict,
    chain: VCPChain,
    anchor_service: AnchorService
) -> VerificationResult:
    """
    Auditor verification procedure for ERASURE events.
    
    Returns: VerificationResult with status and evidence
    """
    
    # Step 1: Verify ERASURE event exists in chain
    if not chain.contains_event(erasure_event["Header"]["EventID"]):
        return VerificationResult(
            status="FAILED",
            reason="ERASURE event not found in chain"
        )
    
    # Step 2: Verify ERASURE event's Merkle inclusion proof
    merkle_proof = erasure_event["ErasureDetails"]["Verification"]["MerkleProof"]
    if not verify_merkle_proof(erasure_event, merkle_proof):
        return VerificationResult(
            status="FAILED",
            reason="Invalid Merkle proof for ERASURE event"
        )
    
    # Step 3: Verify chain continuity (hash chain not broken)
    pre_hash = erasure_event["ErasureDetails"]["Verification"]["PreErasureEventHash"]
    post_hash = erasure_event["ErasureDetails"]["Verification"]["PostErasureChainHash"]
    if not chain.verify_continuity(pre_hash, post_hash):
        return VerificationResult(
            status="FAILED",
            reason="Chain continuity broken"
        )
    
    # Step 4: Verify external anchor for ERASURE event
    anchor_ref = anchor_service.get_anchor_for_event(erasure_event["Header"]["EventID"])
    if not anchor_ref or not anchor_service.verify_anchor(anchor_ref):
        return VerificationResult(
            status="WARNING",
            reason="External anchor not yet confirmed",
            evidence={"anchor_status": "PENDING"}
        )
    
    # Step 5: Verify affected events are now inaccessible
    affected_events = chain.get_events_in_range(
        erasure_event["ErasureDetails"]["Scope"]["FirstAffectedEventID"],
        erasure_event["ErasureDetails"]["Scope"]["LastAffectedEventID"]
    )
    for event in affected_events:
        if is_decryptable(event, erasure_event["ErasureDetails"]["CryptoShredding"]):
            return VerificationResult(
                status="FAILED",
                reason="Affected data still accessible",
                evidence={"accessible_event": event["Header"]["EventID"]}
            )
    
    # All checks passed
    return VerificationResult(
        status="LEGITIMATELY_ERASED",
        erasure_timestamp=erasure_event["ErasureDetails"]["Authorization"]["AuthorizationTimestamp"],
        authorized_by=erasure_event["ErasureDetails"]["Authorization"]["AuthorizedByRoleID"],
        key_destroyed=erasure_event["ErasureDetails"]["CryptoShredding"]["KeyIDHash"],
        anchor_reference=anchor_ref,
        evidence={
            "merkle_proof": merkle_proof,
            "chain_continuity": True,
            "external_anchor": anchor_ref
        }
    )
```

### 3.7 Regulatory Alignment

| Regulation | Requirement | VCP ERASURE Support |
|------------|-------------|---------------------|
| **GDPR Art. 17** | Right to erasure | ✅ Crypto-shredding + ERASURE event |
| **GDPR Art. 17(3)(b)** | Legal retention exemption | ✅ Retention period check |
| **MiFID II Art. 16(7)** | 5-year minimum retention | ✅ RETENTION_EXPIRED reason code |
| **PDPA (Singapore)** | Retention limitation | ✅ SUBJECT_REQUEST reason code |
| **EDPB Guidelines 02/2025** | "Beyond use" acceptable | ✅ Crypto-shredding pattern |

---

## 4. Version Compatibility Matrix

### 4.1 Purpose

Define formal compatibility guarantees between VCP versions to ensure implementers understand upgrade paths and interoperability constraints.

### 4.2 Change Type

**Informative** — Documentation addition.

### 4.3 Data Format Compatibility

| Producer Version | Consumer Version | Compatibility | Notes |
|------------------|------------------|---------------|-------|
| v1.0 | v1.0 | ✅ Full | - |
| v1.0 | v1.1 | ✅ Full | v1.1 accepts all v1.0 events |
| v1.0 | v1.2 | ✅ Full | v1.2 accepts all v1.0 events |
| v1.1 | v1.0 | ⚠️ Partial | New fields (PolicyID, VCP-XREF) ignored |
| v1.1 | v1.1 | ✅ Full | - |
| v1.1 | v1.2 | ✅ Full | v1.2 accepts all v1.1 events |
| v1.2 | v1.0 | ⚠️ Partial | ERASURE, new fields ignored |
| v1.2 | v1.1 | ⚠️ Partial | ERASURE events unknown to v1.1 |
| v1.2 | v1.2 | ✅ Full | - |

### 4.4 Verification Compatibility

| Proof Version | Verifier Version | Compatibility | Notes |
|---------------|------------------|---------------|-------|
| v1.0 proof | v1.2 verifier | ✅ Full | All proofs backward compatible |
| v1.1 proof | v1.2 verifier | ✅ Full | - |
| v1.2 proof | v1.0 verifier | ⚠️ Partial | New proof types fail gracefully |
| v1.2 proof | v1.1 verifier | ⚠️ Partial | ERASURE proofs unknown |

### 4.5 Certification Compatibility

| Implementation | VC-Certified v1.0 | VC-Certified v1.1 | VC-Certified v1.2 |
|----------------|-------------------|-------------------|-------------------|
| v1.0 compliant | ✅ Eligible | ⚠️ Requires External Anchor | ⚠️ Requires External Anchor + RECOVERY constraints |
| v1.1 compliant | ✅ Eligible | ✅ Eligible | ⚠️ Requires RECOVERY constraints |
| v1.2 compliant | ✅ Eligible | ✅ Eligible | ✅ Eligible |

### 4.6 Algorithm Deprecation Timeline

| Algorithm | v1.0 Status | v1.1 Status | v1.2 Status | Planned Removal |
|-----------|-------------|-------------|-------------|-----------------|
| **Ed25519** | DEFAULT | DEFAULT | DEFAULT | - |
| **ECDSA_SECP256K1** | SUPPORTED | SUPPORTED | SUPPORTED | - |
| **RSA_2048** | DEPRECATED | DEPRECATED | DEPRECATED | v2.0 |
| **DILITHIUM2** | FUTURE | FUTURE | EXPERIMENTAL | - |
| **FALCON512** | FUTURE | FUTURE | EXPERIMENTAL | - |

### 4.7 Feature Availability by Version

| Feature | v1.0 | v1.1 | v1.2 |
|---------|------|------|------|
| Hash Chain (PrevHash) | REQUIRED | OPTIONAL | OPTIONAL |
| Merkle Tree | REQUIRED | REQUIRED | REQUIRED |
| External Anchor (Platinum) | REQUIRED | REQUIRED | REQUIRED |
| External Anchor (Gold) | RECOMMENDED | REQUIRED | REQUIRED |
| External Anchor (Silver) | OPTIONAL | REQUIRED | REQUIRED |
| Policy Identification | - | REQUIRED | REQUIRED |
| VCP-XREF | - | OPTIONAL | OPTIONAL |
| ERASURE Event | - | - | OPTIONAL |
| RECOVERY Constraints | - | - | REQUIRED (for VC-Certified) |
| SCITT Alignment Fields | - | - | OPTIONAL |
| Multi-Actor XREF | - | - | OPTIONAL (MUST rules when used) |

---

## 5. SCITT Alignment Fields

### 5.1 Purpose

Align VCP with IETF SCITT (Supply Chain Integrity, Transparency and Trust) architecture to enable interoperability with SCITT Transparency Services and leverage COSE Receipt format.

### 5.2 Change Type

**Normative** — Optional field additions for SCITT interoperability.

> **Clarification (v1.2-draft-02)**: SCITT alignment fields are OPTIONAL for general VCP implementations. However, implementations claiming **VCP-SCITT Conformance Profile** compliance MUST include these fields. This profile-based approach prevents partial implementation issues.

### 5.3 Conformance Profiles (NEW in v1.2-draft-02)

| Profile | SCITTAlignment Fields | Use Case |
|---------|----------------------|----------|
| **VCP Base** | OPTIONAL | Standard VCP implementation |
| **VCP-SCITT** | REQUIRED | IETF SCITT interoperability |
| **VCP-Regulatory** | RECOMMENDED | Regulatory reporting scenarios |

### 5.4 Terminology Mapping

| VCP Concept | SCITT Concept | Alignment |
|-------------|---------------|-----------|
| VCP Event | Signed Statement | VCP Event encoded as COSE_Sign1 |
| VCP Chain | Append-Only Log | Equivalent structure |
| Merkle Proof | COSE Receipt | VCP adopts Receipt format |
| External Anchor | Transparency Service | VCP anchor = SCITT registration |
| PolicyID | Registration Policy | Direct mapping |
| EventHash | Statement Hash | Equivalent |

### 5.5 SCITTAlignment Schema

```json
{
  "Header": {
    "EventID": "uuid-v7",
    "EventType": "string",
    "Timestamp": "int64",
    "TimestampISO": "string",
    "SCITTAlignment": {
      "Version": "1.2",
      "ConformanceProfile": "enum",      // VCP_BASE | VCP_SCITT | VCP_REGULATORY
      "StatementID": "string",           // SCITT Statement identifier
      "TransparencyServiceID": "string", // SCITT TS identifier
      "ReceiptFormat": "COSE_RECEIPT",   // Receipt format used
      "RegistrationPolicy": {
        "PolicyID": "string",            // Maps to VCP PolicyID
        "Issuer": "string",
        "IssuedAt": "int64"
      }
    }
  }
}
```

### 5.6 Profile Requirements

| Field | VCP Base | VCP-SCITT | VCP-Regulatory |
|-------|----------|-----------|----------------|
| `SCITTAlignment` | OPTIONAL | REQUIRED | RECOMMENDED |
| `ConformanceProfile` | - | REQUIRED | REQUIRED |
| `StatementID` | - | REQUIRED | OPTIONAL |
| `TransparencyServiceID` | - | REQUIRED | OPTIONAL |
| `ReceiptFormat` | - | REQUIRED | OPTIONAL |
| `RegistrationPolicy` | - | REQUIRED | REQUIRED |

### 5.7 COSE Receipt Integration

```
┌─────────────────────────────────────────────────────────────────────┐
│  VCP Event → SCITT Receipt Flow                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  VCP Event Generation                                               │
│  ┌─────────────────────────────────────┐                           │
│  │  {                                   │                           │
│  │    "Header": { ... },                │                           │
│  │    "VCP-TRADE": { ... }              │                           │
│  │  }                                   │                           │
│  └─────────────────┬───────────────────┘                           │
│                    │                                                │
│                    ▼                                                │
│  COSE_Sign1 Encoding                                               │
│  ┌─────────────────────────────────────┐                           │
│  │  COSE_Sign1(                         │                           │
│  │    protected: { alg: EdDSA },        │                           │
│  │    unprotected: { },                 │                           │
│  │    payload: canonical(VCP_Event),    │                           │
│  │    signature: Ed25519(payload)       │                           │
│  │  )                                   │                           │
│  └─────────────────┬───────────────────┘                           │
│                    │                                                │
│                    ▼                                                │
│  SCITT Transparency Service Registration                           │
│  ┌─────────────────────────────────────┐                           │
│  │  POST /entries                       │                           │
│  │  Body: COSE_Sign1                    │                           │
│  └─────────────────┬───────────────────┘                           │
│                    │                                                │
│                    ▼                                                │
│  COSE Receipt Returned                                             │
│  ┌─────────────────────────────────────┐                           │
│  │  COSE_Sign1(                         │                           │
│  │    protected: {                      │                           │
│  │      alg: EdDSA,                     │                           │
│  │      vcp_receipt: true               │                           │
│  │    },                                │                           │
│  │    payload: {                        │                           │
│  │      tree_alg: SHA256,               │                           │
│  │      tree_size: 12345,               │                           │
│  │      leaf_index: 12344,              │                           │
│  │      inclusion_proof: [...]          │                           │
│  │    },                                │                           │
│  │    signature: TS_signature           │                           │
│  │  )                                   │                           │
│  └─────────────────────────────────────┘                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Latency Budget Clarification

### 6.1 Purpose

VCP v1.0/v1.1 specifies "<10µs per event" for Platinum tier without defining what operations are included. This update provides explicit latency budgets for critical and non-critical paths.

### 6.2 Change Type

**Normative** — Clarification of existing requirements.

### 6.3 Critical Path Definition

**Critical Path**: Operations that add latency to the trading execution path.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Critical Path (MUST complete before trade execution proceeds)      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Trading System                                                     │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │   Event     │→ │  Canonical  │→ │   Hash      │→ │  Queue    │  │
│  │  Capture    │  │  Transform  │  │ Calculation │  │  Write    │  │
│  │   <1µs     │  │    <2µs     │  │    <3µs     │  │   <1µs    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │
│                                                                     │
│  Total Critical Path: <7µs (target) / <10µs (maximum)              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Non-Critical Path**: Operations that can be performed asynchronously.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Non-Critical Path (Asynchronous, does not block trading)          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │  Signature  │→ │   Merkle    │→ │  External   │→ │  Storage  │  │
│  │ Generation  │  │    Tree     │  │   Anchor    │  │  Persist  │  │
│  │   <50µs    │  │  <100ms     │  │  <10min     │  │  <100ms   │  │
│  │  (HSM)     │  │  (batched)  │  │  (async)    │  │  (async)  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.4 Tier-Specific Latency Requirements

| Operation | Platinum | Gold | Silver |
|-----------|----------|------|--------|
| **Event Capture** | <1µs | <10µs | <1ms |
| **Canonical Transform** | <2µs | <100µs | <10ms |
| **Hash Calculation** | <3µs | <500µs | <50ms |
| **Queue Write** | <1µs | <100µs | <10ms |
| **Critical Path Total** | <10µs | <1ms | <100ms |
| **Signature (async)** | <50µs (HSM) | <1ms | <100ms |
| **Merkle Build (batch)** | <100ms/1K events | <1s/1K events | <10s/1K events |
| **External Anchor** | <10 min | <1 hour | <24 hours |

### 6.5 Measurement Methodology

```yaml
LatencyMeasurement:
  Metric: "99th percentile"
  SampleSize: "≥1,000,000 events"
  Environment:
    Platinum: "Collocated or <1ms network latency"
    Gold: "Cloud or dedicated server"
    Silver: "Any environment"
  Exclusions:
    - "Network latency to broker (external)"
    - "Disk I/O for durable storage (async)"
    - "External anchor confirmation (async)"
  Inclusions:
    - "All critical path operations"
    - "Memory allocation"
    - "Thread synchronization"
```

### 6.6 Reference Hardware Specification

For benchmark reproducibility:

| Component | Platinum Reference | Gold Reference | Silver Reference |
|-----------|-------------------|----------------|------------------|
| **CPU** | Intel Xeon Platinum 8380 | Intel Xeon Gold 6330 | Any modern x86_64 |
| **Memory** | 256GB DDR4 ECC | 64GB DDR4 | 8GB+ |
| **Storage** | NVMe SSD (Intel Optane) | NVMe SSD | SSD or HDD |
| **HSM** | Thales Luna Network HSM 7 | Software HSM (SoftHSM2) | Software signing |
| **Network** | 25Gbps+ | 10Gbps | 1Gbps+ |
| **OS** | Linux 5.15+ (PREEMPT_RT) | Linux 5.x | Any supported OS |

---

## 7. Anchor Target Continuity Plan

### 7.1 Purpose

Define procedures for handling anchor target unavailability, migration, and failover to ensure continuous audit trail integrity.

### 7.2 Change Type

**Normative** — Operational requirement addition.

### 7.3 Trigger Conditions and Response Times

#### 7.3.1 Base Response Requirements

| Condition | Severity | Response Time |
|-----------|----------|--------------|
| **Temporary Outage** | Medium | Queue and retry |
| **Planned Discontinuation** | High | Migrate within 30 days |
| **Unplanned Discontinuation** | Critical | Migrate within 7 days |
| **Security Compromise** | Critical | Immediate migration |
| **Fork/Chain Split** | High | Evaluate within 24 hours |
| **Verification Failure Rate >1%** | Medium | Investigate within 48 hours |

#### 7.3.2 Tier-Specific RTO/RPO (NEW in v1.2-draft-02)

Given different anchor frequencies across tiers, response requirements MUST be proportional:

| Tier | Anchor Frequency | Max Acceptable Outage | Failover Deadline | RPO |
|------|-----------------|----------------------|-------------------|-----|
| **Platinum** | 10 min | 1 anchor cycle (10 min) | 30 min | 10 min of events |
| **Gold** | 1 hour | 2 anchor cycles (2 hours) | 4 hours | 1 hour of events |
| **Silver** | 24 hours | 2 anchor cycles (48 hours) | 7 days | 24 hours of events |

> **RTO** = Recovery Time Objective (max time to restore anchoring)  
> **RPO** = Recovery Point Objective (max acceptable data without anchor)

#### 7.3.3 Automatic Failover Requirements

| Tier | Auto-Failover | Trigger | Target |
|------|--------------|---------|--------|
| **Platinum** | REQUIRED | >1 anchor cycle failure | Pre-configured secondary |
| **Gold** | RECOMMENDED | >2 anchor cycle failures | Pre-configured secondary |
| **Silver** | OPTIONAL | Manual intervention acceptable | Any acceptable target |

### 7.4 Migration Procedure

```
┌─────────────────────────────────────────────────────────────────────┐
│  Anchor Target Migration Procedure                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Phase 1: Pre-Migration (T-7 days minimum)                         │
│  ─────────────────────────────────────────                         │
│  □ Identify replacement anchor target                               │
│  □ Verify replacement meets tier requirements                       │
│  □ Test connectivity and integration                                │
│  □ Log ANCHOR_MIGRATION_PLANNED event                              │
│                                                                     │
│  Phase 2: Dual-Anchoring (T-0 to T+7 days minimum)                 │
│  ────────────────────────────────────────────────                  │
│  □ Log ANCHOR_MIGRATION_START event                                │
│  □ Anchor to BOTH old and new targets                              │
│  □ Verify successful anchoring on new target                       │
│  □ Monitor for discrepancies                                        │
│                                                                     │
│  Phase 3: Cutover (T+7 days)                                       │
│  ─────────────────────────────                                     │
│  □ Cease anchoring to old target                                   │
│  □ Mark old anchor as LEGACY in AnchorRecord                       │
│  □ Continue anchoring to new target only                           │
│                                                                     │
│  Phase 4: Completion (T+14 days)                                   │
│  ────────────────────────────────                                  │
│  □ Verify all events properly anchored on new target               │
│  □ Log ANCHOR_MIGRATION_COMPLETE event                             │
│  □ Update PolicyID to reflect new anchor target                    │
│  □ Archive old anchor verification data                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.5 Migration Event Schema

```json
{
  "EventType": "SYS_ANCHOR_MIGRATION",
  "MigrationDetails": {
    "MigrationID": "uuid",
    "Phase": "enum",                    // PLANNED | START | CUTOVER | COMPLETE
    "OldAnchorTarget": {
      "Type": "string",
      "Identifier": "string",
      "LastAnchorTimestamp": "int64",
      "Status": "enum"                  // ACTIVE | LEGACY | DEPRECATED
    },
    "NewAnchorTarget": {
      "Type": "string",
      "Identifier": "string",
      "FirstAnchorTimestamp": "int64",
      "Status": "enum"                  // PENDING | ACTIVE
    },
    "Reason": {
      "Code": "enum",                   // PLANNED_UPGRADE | DISCONTINUATION | SECURITY | COST
      "Description": "string"
    },
    "DualAnchorPeriod": {
      "StartTimestamp": "int64",
      "EndTimestamp": "int64",
      "OverlapEventCount": "int32"
    },
    "TierSpecificRTO": {
      "Tier": "enum",
      "MaxOutageDuration": "int64",
      "FailoverDeadline": "int64"
    }
  }
}
```

### 7.6 Fallback Strategy

| Priority | Anchor Target | Activation Condition |
|----------|---------------|---------------------|
| **Primary** | Configured anchor (per PolicyID) | Normal operation |
| **Secondary** | Pre-configured fallback | Primary unavailable > tier-specific threshold |
| **Tertiary** | OpenTimestamps (Bitcoin) | Secondary unavailable > 2× threshold |
| **Emergency** | Local attested storage + manual notarization | All automated anchors unavailable |

### 7.7 Local AnchorRecord Retention

Implementations MUST retain local copies of all AnchorRecords:

```yaml
AnchorRecordRetention:
  MinimumPeriod: "Regulatory retention period + 2 years"
  Format: "JSON with cryptographic signatures"
  Storage: "Append-only with integrity verification"
  Purpose:
    - "Verification when anchor target unavailable"
    - "Evidence for regulatory audit"
    - "Migration verification"
    - "Dispute resolution"
```

### 7.8 Failover Automation Criteria (NEW in v1.2-draft-03)

> **Purpose**: Define objective, automatable criteria for triggering anchor failover to meet tier-specific RTO requirements.

#### 7.8.1 Automatic Failover Decision Tree

```
┌─────────────────────────────────────────────────────────────────────┐
│  Anchor Failover Decision Tree                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [Anchor Attempt]                                                  │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────┐                                               │
│  │ Success?        │──Yes──▶ [Continue Normal Operation]           │
│  └────────┬────────┘                                               │
│           │ No                                                      │
│           ▼                                                         │
│  ┌─────────────────┐                                               │
│  │ Retry Count     │                                               │
│  │ < Tier Limit?   │──Yes──▶ [Wait Backoff Period] ──▶ [Retry]    │
│  └────────┬────────┘                                               │
│           │ No                                                      │
│           ▼                                                         │
│  ┌─────────────────┐                                               │
│  │ Secondary       │                                               │
│  │ Configured?     │──No───▶ [Alert + Queue Locally]              │
│  └────────┬────────┘                                               │
│           │ Yes                                                     │
│           ▼                                                         │
│  ┌─────────────────┐                                               │
│  │ Log FAILOVER    │                                               │
│  │ _START Event    │                                               │
│  └────────┬────────┘                                               │
│           │                                                         │
│           ▼                                                         │
│  [Switch to Secondary Anchor]                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### 7.8.2 Tier-Specific Failover Parameters

| Parameter | Platinum | Gold | Silver |
|-----------|----------|------|--------|
| **Max Retry Count** | 3 | 5 | 10 |
| **Initial Backoff** | 10 sec | 1 min | 10 min |
| **Max Backoff** | 2 min | 10 min | 2 hours |
| **Failover Trigger** | 3 consecutive failures OR >10 min total | 5 failures OR >2 hours | 10 failures OR >24 hours |
| **Auto-Failover** | REQUIRED | RECOMMENDED | OPTIONAL |
| **Manual Override** | Allowed with justification | Allowed | Default |

#### 7.8.3 Failover Event Schema

```json
{
  "EventType": "SYS_ANCHOR_FAILOVER",
  "FailoverDetails": {
    "FailoverID": "uuid",
    "TriggerCondition": {
      "FailureCount": "int32",
      "TotalDowntimeSec": "int64",
      "LastSuccessfulAnchor": "int64",
      "ErrorCodes": ["string"]
    },
    "PrimaryAnchor": {
      "Type": "string",
      "Identifier": "string",
      "LastAttemptTimestamp": "int64",
      "LastErrorMessage": "string"
    },
    "SecondaryAnchor": {
      "Type": "string",
      "Identifier": "string",
      "ActivationTimestamp": "int64"
    },
    "QueuedEvents": {
      "Count": "int32",
      "FirstEventID": "uuid",
      "LastEventID": "uuid"
    },
    "AutomatedDecision": "boolean",
    "OperatorOverride": {
      "Overridden": "boolean",
      "OperatorRoleID": "string",
      "Justification": "string"
    }
  }
}
```

#### 7.8.4 Secondary Anchor Pre-Registration

Implementations targeting Platinum or Gold tier SHOULD pre-register secondary anchors:

```yaml
SecondaryAnchorConfiguration:
  # Primary: Ethereum Mainnet
  Primary:
    Type: BLOCKCHAIN
    Identifier: "ethereum:mainnet"
    Classification: CLASS_A
  
  # Secondary: RFC 3161 TSA (auto-failover target)
  Secondary:
    Type: TSA
    Identifier: "https://timestamp.digicert.com"
    Classification: CLASS_B
    PreValidated: true
    LastHealthCheck: "2026-01-06T00:00:00Z"
  
  # Tertiary: OpenTimestamps (manual fallback)
  Tertiary:
    Type: PUBLIC_SERVICE
    Identifier: "opentimestamps.org"
    Classification: CLASS_B
    ManualActivationOnly: true
```

#### 7.8.5 Health Check Requirements

| Tier | Health Check Frequency | Method |
|------|----------------------|--------|
| **Platinum** | Every anchor cycle (10 min) | Active probe + passive monitoring |
| **Gold** | Every 30 minutes | Active probe |
| **Silver** | Every 6 hours | Passive monitoring acceptable |

**Health Check Metrics:**

| Metric | Healthy | Degraded | Unhealthy |
|--------|---------|----------|-----------|
| **Anchor Latency** | <30 sec | 30 sec - 5 min | >5 min |
| **Success Rate (24h)** | >99% | 95-99% | <95% |
| **Confirmation Delay** | <2× expected | 2-5× expected | >5× expected |

---

## 8. Reference Implementation Benchmarks

### 8.1 Purpose

Provide empirical performance data for VCP implementations to guide deployment decisions and validate specification requirements.

### 8.2 Change Type

**Informative** — Appendix addition.

### 8.3 Test Environment

| Component | Specification |
|-----------|--------------|
| **Cloud Instance** | AWS c6i.xlarge (4 vCPU, 8GB RAM) |
| **OS** | Ubuntu 22.04 LTS |
| **Python Version** | 3.11.4 |
| **C++ Compiler** | GCC 12.2 |
| **VCP Implementation** | vcp-core-py v1.2.0, vcp-core-cpp v1.2.0 |

### 8.4 Throughput Benchmarks

| Implementation | Tier | Events/Second | Latency (p99) |
|----------------|------|---------------|---------------|
| **vcp-core-py** | Silver | 50,000 | 85ms |
| **vcp-core-py** | Gold | 120,000 | 0.8ms |
| **vcp-core-cpp** | Gold | 450,000 | 0.3ms |
| **vcp-core-cpp** | Platinum | 1,200,000 | 8µs |
| **vcp-mql-bridge** | Silver | 5,000 | 150ms |

### 8.5 Merkle Tree Construction

| Event Count | vcp-core-py | vcp-core-cpp |
|-------------|-------------|--------------|
| 100 | 1.2ms | 0.08ms |
| 1,000 | 12ms | 0.9ms |
| 10,000 | 145ms | 11ms |
| 100,000 | 1.8s | 130ms |
| 1,000,000 | 22s | 1.5s |

### 8.6 Crypto-Shredding Overhead

| Operation | Base Latency | With Encryption | Overhead |
|-----------|--------------|-----------------|----------|
| Event Creation | 45µs | 53µs | +18% |
| Hash Calculation | 12µs | 14µs | +17% |
| Storage Write | 200µs | 235µs | +18% |

### 8.7 Storage Requirements

| Component | Size per Event | Notes |
|-----------|----------------|-------|
| **Header** | ~200 bytes | Fixed |
| **VCP-TRADE** | ~500 bytes | Typical trading event |
| **Signature (Ed25519)** | 64 bytes | Fixed |
| **Signature (ML-DSA-44)** | ~2,420 bytes | Post-quantum |
| **Merkle Proof** | ~800 bytes | For 1M event tree |
| **Encryption Metadata** | ~180 bytes | VCP-PRIVACY |

### 8.8 External Anchoring Costs (January 2026 Estimates)

| Anchor Target | Cost per Anchor | Typical Frequency | Monthly Cost (Gold) |
|---------------|-----------------|-------------------|---------------------|
| **Ethereum Mainnet** | $2-10 | 10 min | $8,640-43,200 |
| **Polygon PoS** | $0.01-0.05 | 10 min | $43-216 |
| **Bitcoin (OpenTimestamps)** | $0 (aggregated) | 24 hours | $0 |
| **RFC 3161 TSA** | $0.10-0.50 | 1 hour | $72-360 |
| **AWS QLDB** | $0.001/tx | 1 hour | $0.72 |

---

## 9. Multi-Actor Chain Linking Extension

### 9.1 Purpose

Extend VCP-XREF (v1.1) to support chain linking across more than two parties, enabling audit trails for complex trading scenarios involving multiple intermediaries.

### 9.2 Change Type

**Normative** — Extension to VCP-XREF module.

> **Clarification (v1.2-draft-02)**: Multi-Actor VCP-XREF is an **OPTIONAL extension**. However, when an implementation uses Multi-Actor XREF, it MUST comply with the requirements defined in this section. This is consistent with RFC 2119 terminology where optional features have mandatory rules when adopted.

### 9.3 Use Cases

| Scenario | Actors | Chain Linking Requirement |
|----------|--------|--------------------------|
| **Simple Trade** | Trader → Broker | 2-party (v1.1 VCP-XREF) |
| **Routed Order** | Trader → Broker → Exchange | 3-party chain |
| **SOR Execution** | Trader → SOR → [Exchange A, B, C] | 1-to-many fan-out |
| **Prime Brokerage** | Client → Executing Broker → Prime Broker → Custodian | 4-party chain |
| **Regulatory Reporting** | Trader → Broker → ARM → Regulator | 4-party with observer |

### 9.4 Multi-Actor Schema Extension

```json
{
  "VCP-XREF": {
    "Version": "1.2",
    "CrossReferenceID": "uuid",
    "ChainTopology": "enum",           // BILATERAL | LINEAR | FAN_OUT | FAN_IN | MESH
    "PartyRole": "enum",               // INITIATOR | INTERMEDIARY | TERMINAL | OBSERVER
    "PartyIndex": "int32",             // Position in chain (0 = initiator)
    "CounterpartyID": "string",
    "UpstreamParty": {
      "PartyID": "string",
      "EventHash": "string",
      "ReceivedTimestamp": "int64"
    },
    "DownstreamParties": [
      {
        "PartyID": "string",
        "ForwardedTimestamp": "int64",
        "ExpectedAck": "boolean"
      }
    ],
    "ChainMetadata": {
      "TotalParties": "int32",
      "ChainID": "uuid",               // Unique identifier for entire chain
      "OriginatorID": "string",        // PartyID of INITIATOR
      "TerminalIDs": ["string"]        // PartyIDs of TERMINAL nodes
    },
    "ReconciliationStatus": "enum",
    "DiscrepancyDetails": { ... }
  }
}
```

### 9.5 Chain Topology Types

#### 9.5.1 LINEAR (Sequential)

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Trader   │───▶│  Broker  │───▶│ Exchange │───▶│ Clearing │
│ (INIT)   │    │ (INTER)  │    │ (INTER)  │    │ (TERM)   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
   Index 0        Index 1         Index 2         Index 3
```

#### 9.5.2 FAN_OUT (One-to-Many)

```
                              ┌──────────────┐
                         ┌───▶│ Exchange A   │
                         │    │ (TERMINAL)   │
┌──────────┐    ┌────────┴─┐  └──────────────┘
│ Trader   │───▶│   SOR    │
│ (INIT)   │    │ (INTER)  │  ┌──────────────┐
└──────────┘    └────────┬─┘  │ Exchange B   │
                         └───▶│ (TERMINAL)   │
                              └──────────────┘
```

#### 9.5.3 FAN_IN (Many-to-One)

```
┌──────────────┐
│ Price Feed A │───┐
│ (INIT)       │   │    ┌──────────────┐    ┌──────────┐
└──────────────┘   ├───▶│ Aggregator   │───▶│ Trader   │
┌──────────────┐   │    │ (INTER)      │    │ (TERM)   │
│ Price Feed B │───┘    └──────────────┘    └──────────┘
│ (INIT)       │
└──────────────┘
```

### 9.6 Requirements (When Multi-Actor XREF is Used)

| Requirement | Level | Notes |
|-------------|-------|-------|
| Multi-Actor VCP-XREF adoption | OPTIONAL | Extension to v1.1 VCP-XREF |
| ChainTopology field | MUST | Required when >2 parties |
| ChainID | MUST | Unique across all participants |
| UpstreamParty.EventHash | MUST | For INTERMEDIARY/TERMINAL roles |
| External Anchor | MUST | Each party anchors independently |
| ChainMetadata.TotalParties | SHOULD | Aids verification |
| DownstreamParties[].ExpectedAck | SHOULD | Enables completeness check |

### 9.7 Cross-Chain Verification

```python
def verify_multi_party_chain(
    chain_id: str,
    party_events: Dict[str, List[VCPEvent]]
) -> ChainVerificationResult:
    """
    Verify integrity across all parties in a multi-actor chain.
    
    Args:
        chain_id: Unique identifier for the chain
        party_events: Dict mapping PartyID to their VCP events
    
    Returns:
        ChainVerificationResult with status and discrepancies
    """
    
    discrepancies = []
    
    # Step 1: Verify each party's internal chain integrity
    for party_id, events in party_events.items():
        if not verify_party_chain(events):
            discrepancies.append({
                "type": "INTERNAL_CHAIN_BREAK",
                "party": party_id
            })
    
    # Step 2: Verify cross-party linkage
    for party_id, events in party_events.items():
        for event in events:
            xref = event.get("VCP-XREF", {})
            
            # Verify upstream reference
            if upstream := xref.get("UpstreamParty"):
                upstream_party = upstream["PartyID"]
                expected_hash = upstream["EventHash"]
                
                if upstream_party in party_events:
                    actual_event = find_event_by_hash(
                        party_events[upstream_party], 
                        expected_hash
                    )
                    if not actual_event:
                        discrepancies.append({
                            "type": "UPSTREAM_HASH_MISMATCH",
                            "party": party_id,
                            "upstream_party": upstream_party,
                            "expected_hash": expected_hash
                        })
            
            # Verify downstream acknowledgments
            for downstream in xref.get("DownstreamParties", []):
                if downstream["ExpectedAck"]:
                    downstream_party = downstream["PartyID"]
                    if downstream_party in party_events:
                        ack_found = find_acknowledgment(
                            party_events[downstream_party],
                            event["Header"]["EventID"]
                        )
                        if not ack_found:
                            discrepancies.append({
                                "type": "MISSING_DOWNSTREAM_ACK",
                                "party": party_id,
                                "downstream_party": downstream_party
                            })
    
    # Step 3: Verify chain completeness
    topology = determine_topology(party_events)
    completeness = verify_topology_completeness(topology, party_events)
    
    if discrepancies:
        return ChainVerificationResult(
            status="DISCREPANCY",
            discrepancies=discrepancies,
            completeness=completeness
        )
    
    return ChainVerificationResult(
        status="VERIFIED",
        completeness=completeness,
        total_parties=len(party_events),
        total_events=sum(len(e) for e in party_events.values())
    )
```

---

## 10. Silver Tier Implementation Guidance (NEW in v1.2-draft-03)

### 10.1 Purpose

Address concerns that v1.2's enhanced requirements (External Anchor, RECOVERY constraints, RTO/RPO) may create excessive implementation burden for smaller organizations such as retail brokers and prop trading firms using MT4/MT5.

### 10.2 Design Philosophy

> **Principle**: SDK complexity should be inversely proportional to tier level. Silver Tier implementations should achieve v1.2 compliance with minimal configuration.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Complexity Distribution by Tier                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Platinum:  [SDK: 30%] ←───────────────────────→ [Custom: 70%]     │
│             Deep customization, HSM integration, sub-10µs tuning   │
│                                                                     │
│  Gold:      [SDK: 60%] ←─────────────→ [Custom: 40%]               │
│             Standard config + some customization                    │
│                                                                     │
│  Silver:    [SDK: 90%] ←→ [Custom: 10%]                            │
│             "It just works" - minimal configuration                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 10.3 SDK Default Behaviors for Silver Tier

The official VCP SDKs (`vcp-core-py`, `vcp-mql-bridge`) SHALL provide sensible defaults that achieve v1.2 Silver compliance out-of-the-box:

| v1.2 Requirement | SDK Default Behavior | Override Required? |
|------------------|---------------------|-------------------|
| **External Anchor** | OpenTimestamps (free, Bitcoin-backed) | No |
| **Anchor Frequency** | Every 24 hours (batch) | No |
| **RECOVERY Constraints** | Auto-enforced (1000 event SKIP limit) | No |
| **Anchor Continuity** | Local queue + retry with exponential backoff | No |
| **Failover** | Manual (alert only) | No |
| **Latency Budget** | No enforcement (Silver allows <100ms) | No |
| **ERASURE Support** | Included but optional | No |
| **Multi-Actor XREF** | Disabled by default | Yes (opt-in) |

### 10.4 Minimal Silver Configuration

```python
# vcp-core-py: Minimal Silver Tier configuration
from vcp import VCPLogger

# This single line achieves v1.2 Silver compliance
logger = VCPLogger(tier="silver")

# That's it. The SDK handles:
# - OpenTimestamps anchoring (24h batch)
# - RECOVERY constraint enforcement
# - Local anchor queue with retry
# - Automatic SKIP limit (1000 events)
```

```mql5
// vcp-mql-bridge: Minimal Silver Tier configuration
#include <VCP/VCPBridge.mqh>

// Initialize with defaults
VCPBridge bridge;
bridge.Init("silver");  // v1.2 Silver compliant

// Log trading events normally
bridge.LogOrder(ticket, symbol, type, lots, price);
```

### 10.5 Silver Tier "Escape Hatches"

For organizations that find even Silver requirements challenging, the SDK provides graceful degradation:

| Scenario | SDK Behavior | Compliance Impact |
|----------|-------------|-------------------|
| **No internet connectivity** | Queue locally, anchor when connected | ✅ Compliant (within 48h) |
| **OpenTimestamps unavailable** | Retry with backoff, alert after 24h | ✅ Compliant (RPO: 24h) |
| **Storage full** | Rotate oldest unanchored events | ⚠️ Warning logged |
| **SKIP limit approached** | Auto-CHECKPOINT before limit | ✅ Compliant |

### 10.6 Migration Path: v1.1 Silver → v1.2 Silver

For existing v1.1 Silver implementations:

```yaml
# v1.1 → v1.2 Silver Migration Checklist
MigrationSteps:
  1_SDK_Update:
    Action: "Update vcp-core-py to ≥1.2.0"
    Effort: "5 minutes"
    Breaking: false
    
  2_Config_Review:
    Action: "Review anchor settings (defaults are compliant)"
    Effort: "15 minutes"
    Breaking: false
    
  3_Test_Run:
    Action: "Run existing integration tests"
    Effort: "30 minutes"
    Breaking: false
    
  4_Certification:
    Action: "Submit for VC-Certified v1.2 Silver"
    Effort: "Documentation only"
    Breaking: false

TotalEffort: "< 1 hour for typical MT4/5 integration"
```

### 10.7 What Silver Tier Does NOT Require

To reduce adoption friction, the following are explicitly **NOT required** for Silver:

| Feature | Silver Requirement | Notes |
|---------|-------------------|-------|
| HSM | ❌ Not required | Software signing acceptable |
| Real-time anchoring | ❌ Not required | 24h batch is compliant |
| Automatic failover | ❌ Not required | Manual acceptable |
| Sub-millisecond latency | ❌ Not required | <100ms is compliant |
| Multi-Actor XREF | ❌ Not required | Optional extension |
| SCITT alignment | ❌ Not required | VCP Base profile sufficient |
| Dedicated infrastructure | ❌ Not required | Shared hosting acceptable |

### 10.8 SDK Support Commitment

VSO commits to maintaining Silver Tier accessibility:

| Commitment | Specification |
|------------|---------------|
| **Free anchor option** | OpenTimestamps integration always available |
| **Zero-config compliance** | Default settings achieve v1.2 Silver |
| **Backward compatibility** | v1.1 Silver configs work with v1.2 SDK |
| **Documentation** | Silver-specific quick start guide |
| **Support** | Community support via GitHub Discussions |

### A.1 Normative Changes (7)

| # | Change | Section | Impact |
|---|--------|---------|--------|
| 1 | VCP-RECOVERY constraint strengthening | §1 | Certification stricter |
| 2 | Blockchain selection criteria | §2 | Normative requirements |
| 3 | ERASURE event type | §3 | New event type |
| 4 | SCITT alignment fields | §5 | Optional interop fields (MUST when profile claimed) |
| 5 | Latency budget clarification | §6 | Requirement clarification |
| 6 | Anchor continuity plan | §7 | Operational requirement |
| 7 | Multi-actor chain linking | §9 | VCP-XREF extension (MUST rules when used) |

### A.2 Informative Changes (3)

| # | Change | Section | Purpose |
|---|--------|---------|---------|
| 1 | Version compatibility matrix | §4 | Upgrade planning |
| 2 | Reference benchmarks | §8 | Performance expectations |
| 3 | Silver Tier implementation guidance | §10 | Adoption accessibility |

> **Note**: Blockchain recommended list (§2.4) is part of the Normative §2 but explicitly marked as Informative appendix within that section.

---

## Appendix B: Migration Guide

### B.1 From v1.1 to v1.2

| Component | Required Action | Effort |
|-----------|-----------------|--------|
| VCP-RECOVERY | Add constraint validation + EmergencyOverride support | Medium |
| External Anchor | Update AnchorTarget schema + EnhancedMonitoring for Class C | Low-Medium |
| Event Types | Add ERASURE support (optional) | Low |
| Header | Add SCITTAlignment (optional, required for VCP-SCITT profile) | Low |
| VCP-XREF | Add multi-actor fields (optional) | Medium |
| Anchor Continuity | Implement tier-specific RTO/RPO | Medium |

### B.2 Go/No-Go Decision Tree (NEW in v1.2-draft-03)

```
┌─────────────────────────────────────────────────────────────────────┐
│  v1.1 → v1.2 Migration Decision Tree                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Q1: Do you currently use VCP-RECOVERY features?                   │
│      │                                                              │
│      ├─ YES → You MUST update RECOVERY handling for v1.2           │
│      │        certification. Effort: 2-3 engineering weeks.        │
│      │                                                              │
│      └─ NO  → No action required. RECOVERY remains optional.       │
│               Proceed to Q2.                                        │
│                                                                     │
│  Q2: What is your target certification tier?                       │
│      │                                                              │
│      ├─ PLATINUM → MUST implement:                                 │
│      │             □ Auto-failover for anchor (§7.3.3)             │
│      │             □ 10-min RTO compliance                         │
│      │             □ EmergencyOverride with 2-person approval      │
│      │             Effort: 4-6 engineering weeks.                  │
│      │                                                              │
│      ├─ GOLD → SHOULD implement:                                   │
│      │         □ Recommended auto-failover                         │
│      │         □ 4-hour RTO compliance                             │
│      │         □ EmergencyOverride (if using RECOVERY)             │
│      │         Effort: 2-4 engineering weeks.                      │
│      │                                                              │
│      └─ SILVER → MINIMAL changes:                                  │
│                  □ Update SDK to v1.2                              │
│                  □ Verify anchor still meets Class C+ criteria     │
│                  □ Manual failover acceptable                      │
│                  Effort: < 1 week (often < 1 day).                 │
│                                                                     │
│  Q3: Do you need GDPR Article 17 compliance?                       │
│      │                                                              │
│      ├─ YES → Implement ERASURE event type (§3)                    │
│      │        Requires: HSM/KMS integration for key destruction    │
│      │        Effort: 4-6 engineering weeks.                       │
│      │                                                              │
│      └─ NO  → ERASURE is optional. No action required.             │
│                                                                     │
│  Q4: Do you need IETF SCITT interoperability?                      │
│      │                                                              │
│      ├─ YES → Implement VCP-SCITT Conformance Profile (§5)         │
│      │        Requires: COSE library integration                   │
│      │        Effort: 2-4 engineering weeks.                       │
│      │                                                              │
│      └─ NO  → VCP Base profile sufficient. No action required.     │
│                                                                     │
│  Q5: Do you have 3+ party trading chains?                          │
│      │                                                              │
│      ├─ YES → Consider Multi-Actor XREF (§9)                       │
│      │        Requires: Coordination with counterparties           │
│      │        Effort: 4-5 engineering weeks.                       │
│      │                                                              │
│      └─ NO  → Bilateral XREF (v1.1) sufficient.                    │
│                                                                     │
│  ════════════════════════════════════════════════════════════════  │
│                                                                     │
│  MIGRATION RECOMMENDATION:                                         │
│                                                                     │
│  □ Silver Tier, no GDPR/SCITT/Multi-Actor:                        │
│    → UPDATE SDK ONLY. Effort: < 1 day. GO.                        │
│                                                                     │
│  □ Gold Tier, no special features:                                 │
│    → RECOVERY + Failover updates. Effort: 2-3 weeks. GO.          │
│                                                                     │
│  □ Platinum Tier OR GDPR compliance needed:                        │
│    → Full implementation cycle. Effort: 6-8 weeks.                │
│    → PLAN CAREFULLY before GO.                                     │
│                                                                     │
│  □ Multi-Actor XREF needed:                                        │
│    → Requires ecosystem coordination.                              │
│    → Consider phased rollout. EVALUATE before GO.                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### B.3 Certification Upgrade Path

```
┌─────────────────────────────────────────────────────────────────────┐
│  VC-Certified v1.1 → v1.2 Upgrade                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: Self-Assessment                                           │
│  □ Review VCP-RECOVERY usage against v1.2 constraints              │
│  □ Verify anchor target meets v1.2 classification criteria         │
│  □ Document latency measurements                                   │
│  □ Evaluate anchor continuity procedures against tier RTO/RPO      │
│                                                                     │
│  Step 2: Implementation Updates                                    │
│  □ Update VCP-RECOVERY with EmergencyOverride support              │
│  □ Add anchor continuity procedures                                │
│  □ Implement tier-specific failover if Platinum                    │
│  □ Update PolicyID to reference v1.2                               │
│                                                                     │
│  Step 3: Testing                                                   │
│  □ Run VCP Conformance Test Suite v1.2                             │
│  □ Verify backward compatibility with v1.1 events                  │
│  □ Test recovery scenarios including EmergencyOverride             │
│  □ Test anchor failover within tier-specific RTO                   │
│                                                                     │
│  Step 4: Certification                                             │
│  □ Submit updated compliance documentation                         │
│  □ Provide test results                                            │
│  □ Receive VC-Certified v1.2 badge                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Appendix C: Changes from Previous Drafts

### C.1 Changes from v1.2-draft-02

| Issue | Resolution | Section |
|-------|------------|---------|
| Silver Tier implementation burden | Added §10 Silver Tier Implementation Guidance with SDK defaults | §10 |
| Emergency Override audit risk | Added CAB Audit Requirements with red flag detection | §1.4.9 |
| Failover criteria undefined | Added Failover Automation Criteria with decision tree | §7.8 |
| Migration guidance insufficient | Added Go/No-Go Decision Tree | Appendix B.2 |
| Implementation cost unknown | Added Implementation Cost Estimates | Appendix D |
| Adoption timeline unclear | Added Phased Adoption Roadmap | Appendix E |

### C.2 Changes from v1.2-draft-01

| Issue | Resolution | Section |
|-------|------------|---------|
| Normative count inconsistency (6 vs 7) | Unified to 7, with explanation | Executive Summary, Appendix A |
| Blockchain 5-year requirement vs Class C <5 years | Moved operational history to classification, not core requirement | §2.3.1, §2.3.2 |
| CHECKPOINT lacks emergency override | Added EmergencyOverride with 2-person approval | §1.4.6, §1.4.7 |
| Anchor continuity lacks tier-specific RTO/RPO | Added tier-specific response times | §7.3.2 |
| ERASURE may contain PII in references | Added privacy guidance for field hashing | §3.5 |
| SCITT fields Normative vs Optional confusion | Introduced Conformance Profiles | §5.2, §5.3 |
| Multi-Actor XREF requirements inconsistent | Clarified "OPTIONAL extension with MUST rules when used" | §9.2, §9.6 |

---

## Appendix D: Implementation Cost Estimates (NEW in v1.2-draft-03)

### D.1 Engineering Effort by Feature

| Change Item | Complexity | Engineering Weeks | Dependencies |
|-------------|-----------|-------------------|--------------|
| **RECOVERY constraints** | Medium | 2-3 weeks | None |
| **Blockchain classification** | Low | 1 week | Ops runbook |
| **ERASURE event** | High | 4-6 weeks | HSM/KMS integration |
| **Compatibility matrix** | Low | Documentation only | None |
| **SCITT alignment** | Medium-High | 2-4 weeks | COSE library |
| **Latency budgets** | Low | Benchmarking + docs | None |
| **Continuity plan** | Medium | 2-3 weeks | Architecture review |
| **Multi-actor XREF** | High | 4-5 weeks | Party coordination |
| **Silver SDK updates** | Low | 1 week | SDK maintainer |

### D.2 Effort by Tier and Scenario

| Scenario | Silver | Gold | Platinum |
|----------|--------|------|----------|
| **Minimal v1.2 compliance** | <1 week | 2-3 weeks | 4-6 weeks |
| **+ GDPR/ERASURE** | +4-6 weeks | +4-6 weeks | +4-6 weeks |
| **+ SCITT interop** | +2-4 weeks | +2-4 weeks | +2-4 weeks |
| **+ Multi-Actor XREF** | +4-5 weeks | +4-5 weeks | +4-5 weeks |
| **Full feature adoption** | 11-16 weeks | 12-18 weeks | 14-21 weeks |

### D.3 Infrastructure Cost Impact

| Component | Silver | Gold | Platinum |
|-----------|--------|------|----------|
| **Anchor costs (monthly)** | $0 (OTS) | $72-360 (TSA) | $8K-43K (ETH) |
| **HSM (if ERASURE)** | Cloud KMS ~$50/mo | Cloud KMS ~$100/mo | Dedicated HSM ~$2K/mo |
| **Additional storage** | +10% | +15% | +20% |
| **Monitoring/alerting** | Existing tools | Dedicated dashboard | 24/7 NOC integration |

### D.4 Team Composition Recommendations

| Tier | Minimum Team | Recommended Team |
|------|-------------|------------------|
| **Silver** | 1 developer (part-time) | 1 developer + 1 QA |
| **Gold** | 2 developers | 2 developers + 1 QA + 1 DevOps |
| **Platinum** | 3 developers + 1 architect | 4 developers + 2 QA + 2 DevOps + 1 security |

---

## Appendix E: Phased Adoption Roadmap (NEW in v1.2-draft-03)

### E.1 Recommended Implementation Phases

```
┌─────────────────────────────────────────────────────────────────────┐
│  v1.2 Phased Adoption Roadmap                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PHASE 1: Foundation (Q1 2026)                                     │
│  ────────────────────────────                                      │
│  Priority: HIGH                                                    │
│  Features:                                                          │
│    ✓ VCP-RECOVERY constraints                                      │
│    ✓ Blockchain classification criteria                            │
│    ✓ Anchor continuity plan (basic)                                │
│  Deliverables:                                                      │
│    • Updated SDK with v1.2 defaults                                │
│    • Conformance Test Suite v1.2                                   │
│    • Migration guide for v1.1 → v1.2                               │
│  Target: All existing VC-Certified implementations                 │
│                                                                     │
│  PHASE 2: Regulatory Compliance (Q2-Q3 2026)                       │
│  ──────────────────────────────────────────                        │
│  Priority: HIGH (for EU operations)                                │
│  Features:                                                          │
│    ✓ ERASURE event type                                            │
│    ✓ Advanced anchor continuity (auto-failover)                    │
│    ✓ VCP-Regulatory conformance profile                            │
│  Deliverables:                                                      │
│    • GDPR compliance toolkit                                       │
│    • HSM integration guide                                         │
│    • Regulatory mapping documentation                              │
│  Target: EU-based prop firms, brokers with EU clients              │
│                                                                     │
│  PHASE 3: Interoperability (Q3-Q4 2026)                            │
│  ─────────────────────────────────────                             │
│  Priority: MEDIUM                                                  │
│  Features:                                                          │
│    ✓ SCITT alignment (VCP-SCITT profile)                           │
│    ✓ Multi-Actor XREF                                              │
│    ✓ Advanced verification APIs                                    │
│  Deliverables:                                                      │
│    • COSE integration library                                      │
│    • Multi-party coordination protocol                             │
│    • Cross-organization audit guide                                │
│  Target: Institutional deployments, multi-party trading chains     │
│                                                                     │
│  PHASE 4: Optimization (Q1 2027+)                                  │
│  ───────────────────────────────                                   │
│  Priority: ONGOING                                                 │
│  Features:                                                          │
│    ○ Post-quantum algorithm support                                │
│    ○ Performance optimizations                                     │
│    ○ Advanced analytics integration                                │
│  Deliverables:                                                      │
│    • PQC migration guide                                           │
│    • Benchmark reports                                             │
│    • Best practices documentation                                  │
│  Target: Future-proofing for all implementations                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### E.2 Phase Dependencies

```
Phase 1 (Foundation)
    │
    ├──────────────────┐
    ▼                  ▼
Phase 2 (Regulatory)  Phase 3 (Interop)
    │                  │
    └──────────────────┘
            │
            ▼
    Phase 4 (Optimization)
```

### E.3 Adoption Priority by Organization Type

| Organization Type | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|-------------------|---------|---------|---------|---------|
| **Prop Trading Firm** | REQUIRED | HIGH (EU) | LOW | OPTIONAL |
| **Retail Broker** | REQUIRED | HIGH (EU) | MEDIUM | OPTIONAL |
| **Institutional Broker** | REQUIRED | HIGH | HIGH | MEDIUM |
| **Exchange/Venue** | REQUIRED | HIGH | REQUIRED | HIGH |
| **Audit Firm/CAB** | REQUIRED | REQUIRED | HIGH | MEDIUM |
| **RegTech Provider** | REQUIRED | HIGH | REQUIRED | HIGH |

### E.4 Success Criteria by Phase

| Phase | Success Metric | Target |
|-------|----------------|--------|
| **Phase 1** | Existing VC-Certified implementations upgraded | >80% within 6 months |
| **Phase 2** | GDPR-compliant implementations | >50% of EU operations |
| **Phase 3** | Multi-party audit trails operational | ≥3 production deployments |
| **Phase 4** | PQC-ready implementations | >30% within 12 months of Phase 4 start |

---

## Contact Information

**VeritasChain Standards Organization (VSO)**  
Website: https://veritaschain.org  
Email: standards@veritaschain.org  
GitHub: https://github.com/veritaschain  
Technical Support: technical@veritaschain.org

---

## License

This specification is licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).

---

*End of VCP v1.2 Change Proposal (Revision 3)*
