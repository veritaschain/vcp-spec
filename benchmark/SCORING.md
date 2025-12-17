# VAP Scorecard Scoring Criteria

**Document ID:** VSO-BENCHMARK-SCORE-001  
**Version:** 1.0  
**Status:** Normative (Canonical Reference)  
**Maintainer:** VeritasChain Standards Organization (VSO)

---

## Overview

This document defines the official scoring criteria for the Verifiable AI Provenance (VAP) Scorecard. These criteria assess the auditability of AI-driven and algorithmic decision systems.

The VAP Scorecard evaluates 10 criteria, each scored 0-2, for a maximum score of 20.

---

## Scoring Scale

| Score | Meaning |
|-------|---------|
| **0** | Not implemented or fundamentally inadequate |
| **1** | Partially implemented; gaps remain |
| **2** | Fully implemented; meets all technical requirements |

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

| Score | Requirements |
|-------|--------------|
| 0 | No external verification possible. Audit trail is opaque to third parties. |
| 1 | Partial verification via exported logs, but no cryptographic proof of integrity. |
| 2 | Full third-party verification via cryptographic proofs (e.g., Merkle inclusion proofs) and published verification procedures. |

**Regulatory Relevance:** EU AI Act, MiFID II, SEC 17a-4

---

### Criterion 2: Tamper Evidence

**Question:** Can unauthorized modifications be detected?

| Score | Requirements |
|-------|--------------|
| 0 | No tamper detection mechanism. Data can be modified without trace. |
| 1 | Basic integrity checks exist but are not cryptographically robust. |
| 2 | Cryptographic hash chains with published schemas ensure any modification is immediately detectable. |

**Regulatory Relevance:** EU AI Act, SEC 17a-4

---

### Criterion 3: Sequence Fixation

**Question:** Is the chronological order of events immutably recorded?

| Score | Requirements |
|-------|--------------|
| 0 | No sequence guarantee. Events can be reordered or backdated. |
| 1 | Timestamps exist but are not cryptographically linked to prove order. |
| 2 | Time-ordered identifiers (UUID v7 or equivalent) with cryptographic hash chain linking prove exact sequence. |

**Regulatory Relevance:** EU AI Act, MiFID II

---

### Criterion 4: Decision Provenance

**Question:** Can the inputs and rationale behind each decision be traced?

| Score | Requirements |
|-------|--------------|
| 0 | No logging of decision inputs or context. |
| 1 | Partial logging exists (e.g., final decision only, no inputs or confidence). |
| 2 | Complete provenance logged: input features, model/algorithm version, confidence scores, all in structured format. |

**Regulatory Relevance:** EU AI Act Article 12 (core requirement)

---

### Criterion 5: Responsibility Boundaries

**Question:** Is it clear who or what approved, executed, or overrode each action?

| Score | Requirements |
|-------|--------------|
| 0 | No attribution of actions to operators or systems. |
| 1 | Basic operator ID logging exists but lacks distinction between automated and manual actions. |
| 2 | Clear OperatorID, action attribution, and human-override flags recorded for every decision point. |

**Regulatory Relevance:** EU AI Act, MiFID II

---

### Criterion 6: Audit Submission Readiness

**Question:** Can a complete evidence package be exported on demand for regulatory or audit review?

| Score | Requirements |
|-------|--------------|
| 0 | No export capability. Evidence must be manually compiled. |
| 1 | Partial export available but requires manual assembly or lacks cryptographic proofs. |
| 2 | One-click or API-driven export of complete evidence packages in standard format (JSON/PDF) with cryptographic proofs. |

**Regulatory Relevance:** EU AI Act, SEC 17a-4

---

### Criterion 7: Retention & Durability

**Question:** Are records retained for regulatory-required periods with guaranteed integrity?

| Score | Requirements |
|-------|--------------|
| 0 | No retention policy or technical enforcement. |
| 1 | Retention policy exists but no technical enforcement of immutability or durability. |
| 2 | Guaranteed retention (5-7 years minimum) with redundancy, immutability during retention period, and GDPR-compliant deletion capability (crypto-shredding). |

**Regulatory Relevance:** SEC 17a-4, MiFID II, GDPR

---

### Criterion 8: Timestamp Reliability

**Question:** Are timestamps synchronized to a trusted, verifiable time source?

| Score | Requirements |
|-------|--------------|
| 0 | Local system time only. No synchronization to external source. |
| 1 | NTP synchronization exists but no drift monitoring or sync status logging. |
| 2 | NTP/PTP synchronized with drift monitoring and sync status logging, meeting precision requirements (e.g., MiFID II RTS 25). |

**Regulatory Relevance:** MiFID II RTS 25

---

### Criterion 9: Cryptographic Strength

**Question:** Do the cryptographic algorithms meet current security standards?

| Score | Requirements |
|-------|--------------|
| 0 | No cryptography used, or deprecated/broken algorithms (MD5, SHA-1). |
| 1 | Standard algorithms used but implementation not audited or key management informal. |
| 2 | NIST/FIPS compliant algorithms (SHA-256, Ed25519 or equivalent) with proper key management practices. |

**Regulatory Relevance:** SEC 17a-4, MiFID II, NIST guidelines

---

### Criterion 10: Cryptographic Agility

**Question:** Can the system migrate to new cryptographic algorithms as standards evolve?

| Score | Requirements |
|-------|--------------|
| 0 | Algorithms are hardcoded. Migration requires system replacement. |
| 1 | Algorithms are configurable but migration requires significant rework. |
| 2 | Algorithm-agnostic design with versioned signatures, documented migration path, and readiness for post-quantum cryptography. |

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

1. **Evidence-Based:** Scores must be supported by documented evidence
2. **Conservative:** When in doubt, score lower
3. **Binary at Extremes:** Score 0 means "not present"; Score 2 means "fully meets requirements"
4. **Preliminary Status:** All assessments using this scorecard should be marked as preliminary pending formal audit

### Evidence Types

Acceptable evidence includes:
- System architecture documentation
- Sample log files with hash chains
- Merkle proof demonstrations
- Key management policy documents
- Timestamp synchronization configuration
- Export capability demonstrations

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01 | Initial release |

---

## Related Documents

- **IMPROVEMENT.md** — Informational guidance on technical approaches (non-normative)
- **README.md** — Benchmark overview and quick start

---

## License

This document is licensed under CC BY 4.0.

© 2025 VeritasChain Standards Organization (VSO)
