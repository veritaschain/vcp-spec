# VAP Scorecard Scoring Criteria

**Document ID:** VSO-BENCHMARK-SCORE-001  
**Version:** 2.0  
**Status:** Normative (Canonical Reference)  
**Maintainer:** VeritasChain Standards Organization (VSO)

---

## Implementation Neutrality Statement

> **This benchmark is implementation-agnostic.**
>
> No specific technology, protocol, library, or data structure is mandated. Scores are based solely on whether the **required outcome** (the cryptographic or audit property) is demonstrably achieved—not on how it is achieved.
>
> Reference implementations (such as VeritasChain Protocol) exist as **illustrative examples only** and do not represent the only acceptable approach. Implementations using different technologies are equally valid if they achieve the same outcome properties.

---

## Overview

This document defines the official scoring criteria for the Verifiable AI Provenance (VAP) Scorecard. These criteria assess the auditability of AI-driven and algorithmic decision systems based on **outcomes achieved**, not specific implementations used.

The VAP Scorecard evaluates 10 criteria, each scored 0-2, for a maximum score of 20.

---

## Scoring Scale

| Score | Meaning |
|-------|---------|
| **0** | Not implemented or fundamentally inadequate |
| **1** | Partially implemented; gaps remain |
| **2** | Fully implemented; required outcome demonstrably achieved |

---

## Grade Thresholds

| Score Range | Grade | Interpretation |
|-------------|-------|----------------|
| 16-20 | **Strong** | System demonstrates robust auditability |
| 11-15 | **Moderate** | Auditability present with notable gaps |
| 6-10 | **Limited** | Significant auditability deficiencies |
| 0-5 | **Inadequate** | Auditability fundamentally insufficient |

---

## Criteria Definitions

### Criterion 1: Third-Party Verifiability

**Question:** Can an external party independently verify the audit trail?

**Required Outcome for Score 2:**
- An external party can verify integrity **without access to internal systems**
- Verification produces **reproducible results** from exported data and public information alone
- Cryptographic proofs enable **mathematical certainty**, not trust-based assurance

| Score | Requirements |
|-------|--------------|
| 0 | No external verification possible. Audit trail is opaque to third parties. |
| 1 | Partial verification via exported logs, but verification depends on trust in the exporting system (no cryptographic proof). |
| 2 | **Cryptographically verifiable by third parties using only exported data and public commitments.** Verification is reproducible and independent of system access. |

**Examples of acceptable approaches (non-exhaustive):**
- Merkle tree inclusion proofs with published roots
- Hash-linked records with public anchor points
- Cryptographic accumulators with membership proofs
- Trusted timestamping services (e.g., RFC 3161)
- Blockchain-anchored commitments
- Any other cryptographic commitment scheme with public verification

**Regulatory Relevance:** EU AI Act, MiFID II, SEC 17a-4

---

### Criterion 2: Tamper Evidence

**Question:** Can unauthorized modifications be detected?

**Required Outcome for Score 2:**
- Any modification to records is **cryptographically detectable**
- Detection does **not require comparison with an external backup**
- Tamper evidence is **inherent in the data structure itself**

| Score | Requirements |
|-------|--------------|
| 0 | No tamper detection mechanism. Data can be modified without trace. |
| 1 | Basic integrity checks exist but detection requires trusted reference data or is not cryptographically robust. |
| 2 | **Modifications are cryptographically detectable from the data structure alone.** No trusted reference copy required. |

**Examples of acceptable approaches (non-exhaustive):**
- Cryptographic hash chains (each record references previous hash)
- Authenticated data structures (e.g., authenticated skip lists, Merkle trees)
- Commitment schemes with binding properties
- Immutable append-only ledgers with cryptographic linking

**Regulatory Relevance:** EU AI Act, SEC 17a-4

---

### Criterion 3: Sequence Fixation

**Question:** Is the chronological order of events immutably recorded?

**Required Outcome for Score 2:**
- Event ordering is **cryptographically provable**
- Backdating or reordering is **detectable**
- Sequence proofs are **independently verifiable**

| Score | Requirements |
|-------|--------------|
| 0 | No sequence guarantee. Events can be reordered or backdated without detection. |
| 1 | Timestamps exist but sequence integrity depends on system trust (not cryptographically enforced). |
| 2 | **Chronological order is cryptographically fixed and independently verifiable.** Reordering attempts are detectable. |

**Examples of acceptable approaches (non-exhaustive):**
- Time-ordered identifiers (e.g., UUID v7) with cryptographic chaining
- Verifiable delay functions
- Trusted timestamping authorities (RFC 3161)
- Consensus-based ordering with cryptographic finality
- Sequential hash linking with embedded timestamps

**Regulatory Relevance:** EU AI Act, MiFID II

---

### Criterion 4: Decision Provenance

**Question:** Can the inputs and rationale behind each decision be traced?

**Required Outcome for Score 2:**
- Complete decision context is logged (inputs, model version, parameters)
- Logs are **structured and machine-readable**
- Provenance chain is **traceable from input to output**

| Score | Requirements |
|-------|--------------|
| 0 | No logging of decision inputs or context. |
| 1 | Partial logging exists (e.g., final decision only, no inputs or confidence). |
| 2 | **Complete decision provenance logged in structured format:** input features, model/algorithm version, confidence scores, and decision output. |

**Examples of acceptable approaches (non-exhaustive):**
- Structured JSON/XML logs with defined schema
- W3C PROV-compliant provenance records
- ML pipeline metadata tracking (MLflow, Kubeflow, etc.)
- Decision audit logs with input snapshots
- Custom structured logging with complete field coverage

**Regulatory Relevance:** EU AI Act Article 12 (core requirement)

---

### Criterion 5: Responsibility Boundaries

**Question:** Is it clear who or what approved, executed, or overrode each action?

**Required Outcome for Score 2:**
- Every action is **attributed to a specific operator or system**
- Human interventions are **distinguishable from automated decisions**
- Override events are **explicitly recorded**

| Score | Requirements |
|-------|--------------|
| 0 | No attribution of actions to operators or systems. |
| 1 | Basic operator ID logging exists but lacks clarity on automation vs. manual distinction. |
| 2 | **Clear attribution for every action:** operator/system identity, automation status, and human-override flags are recorded. |

**Examples of acceptable approaches (non-exhaustive):**
- Operator ID fields with role classification
- Human-in-the-loop flags with approval timestamps
- Approval workflow audit trails
- Digital signatures on override actions
- Escalation logging with authorization chain

**Regulatory Relevance:** EU AI Act, MiFID II

---

### Criterion 6: Audit Submission Readiness

**Question:** Can a complete evidence package be exported on demand for regulatory or audit review?

**Required Outcome for Score 2:**
- Complete evidence package exportable **without manual assembly**
- Export includes **cryptographic proofs** (where applicable)
- Format is **standard and machine-readable**

| Score | Requirements |
|-------|--------------|
| 0 | No export capability. Evidence must be manually compiled. |
| 1 | Partial export available but requires manual assembly or lacks integrity proofs. |
| 2 | **On-demand export of complete evidence packages** in standard format, with cryptographic integrity proofs where applicable. |

**Examples of acceptable approaches (non-exhaustive):**
- API-driven evidence export
- One-click audit package generation
- Regulatory report templates with embedded proofs
- Structured data export with hash manifests
- Automated compliance report generation

**Regulatory Relevance:** EU AI Act, SEC 17a-4

---

### Criterion 7: Retention & Durability

**Question:** Are records retained for regulatory-required periods with guaranteed integrity?

**Required Outcome for Score 2:**
- **Technical enforcement** of retention period
- **Integrity maintained** throughout retention
- **Compliant deletion capability** (for GDPR)

| Score | Requirements |
|-------|--------------|
| 0 | No retention policy or technical enforcement. |
| 1 | Retention policy exists but no technical enforcement of integrity or durability. |
| 2 | **Guaranteed retention with technical enforcement:** immutability during retention, redundancy, and compliant deletion capability. |

**Examples of acceptable approaches (non-exhaustive):**
- WORM (Write Once Read Many) storage
- Encryption-based deletion (crypto-shredding)
- Distributed storage with integrity verification
- Immutable backup with retention locks
- Cloud compliance storage tiers

**Regulatory Relevance:** SEC 17a-4, MiFID II, GDPR

---

### Criterion 8: Timestamp Reliability

**Question:** Are timestamps synchronized to a trusted, verifiable time source?

**Required Outcome for Score 2:**
- Synchronization to **authoritative time source**
- **Drift monitoring** with alerting
- **Sync status is logged** and auditable

| Score | Requirements |
|-------|--------------|
| 0 | Local system time only. No synchronization to external source. |
| 1 | Time synchronization exists but no drift monitoring or sync logging. |
| 2 | **Synchronized to trusted time source with drift monitoring and sync status logging.** |

**Examples of acceptable approaches (non-exhaustive):**
- NTP with stratum verification and drift logging
- PTP (Precision Time Protocol) for high-precision needs
- GPS-disciplined clocks
- Trusted timestamping services (RFC 3161)
- Atomic clock synchronization

**Regulatory Relevance:** MiFID II RTS 25

---

### Criterion 9: Cryptographic Strength

**Question:** Do the cryptographic algorithms meet current security standards?

**Required Outcome for Score 2:**
- Algorithms comply with **recognized standards** (NIST, FIPS, or equivalent)
- Key management follows **security best practices**
- **No deprecated or known-weak algorithms**

| Score | Requirements |
|-------|--------------|
| 0 | No cryptography used, or deprecated algorithms (MD5, SHA-1 for integrity). |
| 1 | Standard algorithms used but key management is informal or unaudited. |
| 2 | **Standards-compliant algorithms with proper key management.** Implementation follows recognized security guidelines. |

**Examples of acceptable approaches (non-exhaustive):**
- SHA-256/SHA-3 for hashing
- Ed25519, ECDSA, RSA-2048+, or equivalent for signatures
- Hardware security modules (HSM) for key storage
- Documented key rotation procedures
- Audited cryptographic implementations

**Regulatory Relevance:** SEC 17a-4, MiFID II, NIST guidelines

---

### Criterion 10: Cryptographic Agility

**Question:** Can the system migrate to new cryptographic algorithms as standards evolve?

**Required Outcome for Score 2:**
- Algorithm changes do **not require system replacement**
- Cryptographic parameters are **versioned**
- Migration path is **documented**

| Score | Requirements |
|-------|--------------|
| 0 | Algorithms are hardcoded. Migration requires system replacement. |
| 1 | Algorithms are configurable but migration requires significant rework. |
| 2 | **Algorithm-agnostic design:** versioned cryptographic parameters, documented migration procedures, and post-quantum readiness planning. |

**Examples of acceptable approaches (non-exhaustive):**
- Algorithm identifier fields in signed structures
- Pluggable cryptographic backends
- Version negotiation protocols
- Documented post-quantum migration roadmap
- Hybrid classical/PQC signature support

**Regulatory Relevance:** NIST PQC transition guidance

---

## Regulatory Profile Mapping

Different regulatory frameworks emphasize different criteria:

| Criterion | EU AI Act | MiFID II | SEC 17a-4 |
|-----------|-----------|----------|-----------|
| 1. Third-Party Verifiability | ● | ● | ● |
| 2. Tamper Evidence | ● | | ● |
| 3. Sequence Fixation | ● | ● | |
| 4. Decision Provenance | ● | | |
| 5. Responsibility Boundaries | ● | ● | |
| 6. Audit Submission Readiness | ● | | ● |
| 7. Retention & Durability | | ● | ● |
| 8. Timestamp Reliability | | ● | |
| 9. Cryptographic Strength | | ● | ● |
| 10. Cryptographic Agility | | | |

● = Explicitly or implicitly required by regulation

---

## Assessment Guidance

### Scoring Principles

1. **Outcome-Based:** Evaluate whether the required property is achieved, not which technology is used
2. **Evidence-Based:** Scores must be supported by documented evidence
3. **Conservative:** When in doubt, score lower
4. **Implementation-Neutral:** Accept any technology that demonstrably achieves the outcome
5. **Preliminary Status:** All assessments should be marked as preliminary pending formal audit

### Evidence Types

Acceptable evidence includes (examples, not exhaustive):
- System architecture documentation demonstrating the required property
- Sample records showing the cryptographic property in action
- Verification procedure demonstrations
- Key management policy documents
- Timestamp synchronization configuration
- Export capability demonstrations with integrity proofs

---

## Reference Implementations

Reference implementations such as **VeritasChain Protocol (VCP)** exist as **illustrative examples only**. They demonstrate one possible approach to achieving the required outcomes but are not the only valid approach.

Other implementations using different data structures, signature schemes, or architectural patterns are equally valid if they demonstrably achieve the same cryptographic and audit properties specified in each criterion.

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01 | Initial release |
| 2.0 | 2025-12 | Revised for implementation neutrality; outcome-based criteria; added examples as non-exhaustive |

---

## Related Documents

- **IMPROVEMENT.md** — Informational guidance on technical approaches (non-normative)
- **README.md** — Benchmark overview and quick start

---

## License

This document is licensed under CC BY 4.0.

© 2025 VeritasChain Standards Organization (VSO)
