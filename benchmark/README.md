# AI Decision Auditability Benchmark (v1.0)

> **Consistency note — 25 October 2026 (informative).** The documents in this
> directory have not been re-reviewed against VAP v1.2. Known inconsistencies:
>
> - [SCORING.md](./SCORING.md) is headed "Version 2.0" and "Normative (Canonical
>   Reference)", while this README gives the benchmark as released v1.0. Which
>   version and status apply has not been settled.
> - SCORING.md and [IMPROVEMENT.md](./IMPROVEMENT.md) call the benchmark the
>   "VAP Scorecard". VAP v1.2 defines no scorecard; the benchmark is not part of
>   the VAP specification, and a score is not a VAP or VCP conformance result.
> - IMPROVEMENT.md cites VCP sections by names that do not exist in any VCP
>   specification version (for example "§4.2 (MerkleAnchor)", "§3.3
>   (HashChain)", "§5.3 (ResponsibilityFields)", "§6.4 (KeyLifecycle)"). Use
>   the VCP specification's own section headings instead. The "one reference
>   profile" label on those lines means one example, not a VAP reference
>   profile.
> - IMPROVEMENT.md described VCP as "one example of a complete, open-standard
>   implementation" and as "one reference implementation". Under VAP v1.2
>   §10.4, VCP's alignment with VAP v1.2 is under review and full conformance
>   has not been established; that subsection was corrected on 25 October 2026.
>
> The PDF files are unchanged.

This directory contains the official **AI Decision Auditability Benchmark** published by the  
**VeritasChain Standards Organization (VSO)**.

This benchmark is:

- **NOT** an implementation guide  
- **NOT** a product  
- **NOT** a certification scheme  

It is a **vendor-neutral evaluation standard** for assessing the *auditability and evidence quality* of AI and algorithmic decision systems.

---

## Purpose

As AI systems increasingly move toward autonomous decision-making, regulators and auditors face a structural challenge:

> Can AI-driven decisions be independently verified by a third party, without relying on vendor trust?

This benchmark provides a **common, repeatable measure** to answer that question.

---

## Primary Use Cases

- Pre-audit diagnostics and scoping  
- AI assurance methodology and consistency across engagements  
- Regulatory evidence quality assessment  
- Repeatable client-facing audit pre-assessment  

---

## Benchmark Components

This directory includes the following official documents:

- **Scorecard**  
  Defines *what* is evaluated (10 criteria, 20-point scale)

- **PoC / Assessment Guide**  
  Defines *how* the benchmark can be applied in approximately 3 hours

- **Evidence Pack Template**  
  Defines *how results are submitted* as third-party audit or regulatory evidence

- **EU AI Act Mapping Annex**  
  Maps benchmark criteria to EU AI Act Articles 12, 13, 14, and 17, and MiFID II / RTS requirements

---

## Implementation Guidance (Non-Normative)

In addition to the normative scoring criteria, this benchmark provides
informational implementation guidance describing common technical
approaches for improving assessment scores.

- **IMPROVEMENT.md** — Non-normative guidance on how organizations may
  achieve higher scores through various technical approaches.
- This guidance is **not a requirement**, **not an endorsement**, and
  **multiple implementations are valid**.
- References to specific specifications (including VCP) are provided
  as **example implementation profiles only**.

→ See: [IMPROVEMENT.md](./IMPROVEMENT.md)

---

## Theoretical Foundation

The benchmark is grounded in open cryptographic principles and cross-jurisdictional regulatory analysis.

A formal theoretical paper explaining **why open cryptographic standards are structurally necessary for AI auditability** is available on Zenodo:

- **Why Open Cryptographic Standards Matter for AI Auditability:  
  Formal Analysis and Regulatory Alignment**  
  https://zenodo.org/records/17947483

This paper introduces the *Verification Paradox* and demonstrates why proprietary audit systems cannot provide true third-party verifiability by design.

---

## Relationship to VCP and VAP

- **VCP (VeritasChain Protocol)** provides a concrete, domain-specific implementation profile for algorithmic trading systems.
- **VAP (Verifiable AI Provenance Framework)** generalizes these principles across high-risk AI domains.
- This **Benchmark** serves as a vendor-neutral *measurement layer* for auditability, independent of any specific implementation.

---

## Status and Governance

- Status: **Released (v1.0)**  
- Maintained by: **VeritasChain Standards Organization (VSO)**  
- License: **CC BY 4.0 International**

Feedback from audit, assurance, compliance, and regulatory professionals — including critical perspectives — is welcome.

