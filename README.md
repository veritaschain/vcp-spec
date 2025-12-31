![VCP Version](https://img.shields.io/badge/VCP-v1.1-blue)
![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-green)

# VeritasChain Protocol (VCP)

**VeritasChain Protocol (VCP)** is an open, vendor-neutral standard for  
**cryptographically verifiable audit trails** in algorithmic and AI-driven
trading systems.

VCP enables regulators, auditors, and market participants to  
**verify — not merely trust —** the integrity, completeness, and ordering of
trading decisions, orders, executions, and risk controls.

This repository is maintained by the  
**VeritasChain Standards Organization (VSO)**.

---

## 📌 Canonical Specification Location (IMPORTANT)

The **canonical (normative) specification** of VCP is located under:

```text
/spec/
 ├─ v1.0/
 └─ v1.1/

- Each version directory contains the authoritative specification (`SPEC.md`)
- Files outside `/spec/` are **non-normative**
- HTML, PDF, or translated documents (if any) are provided **for convenience only**

**If there is any conflict, the content under `/spec/` always prevails.**

---

## 📘 Available Versions

### ▶ Current Stable
- **v1.1** — latest specification with strengthened integrity guarantees  
  → `/spec/v1.1/`

### ▶ Legacy
- **v1.0** — initial released version  
  → `/spec/v1.0/`

Migration notes and compatibility considerations are documented inside each
version directory.

---

## 🎯 Purpose

VCP defines a globally consistent audit format that allows third parties to
mathematically verify:

- Algorithmic **signals and decisions**
- **Order lifecycle** events (submit, acknowledge, execute, cancel)
- **Risk controls** and parameter snapshots
- **AI governance metadata** (model identity, decision factors, approvals)
- **Time synchronization** and event ordering

VCP is designed to support compliance with:

- MiFID II / MiFID III (algorithmic trading & timestamping)
- EU AI Act (Article 12 logging and accountability)
- GDPR (crypto-shredding and privacy-preserving auditability)
- SEC CAT (Rule 613) and similar global regimes

---

## 🧩 Protocol Modules

- **VCP-CORE** — Event headers, timestamps, security metadata  
- **VCP-TRADE** — Trading and execution payloads  
- **VCP-GOV** — Algorithm governance and AI transparency  
- **VCP-RISK** — Risk parameters and control triggers  
- **VCP-PRIVACY** — Pseudonymization and crypto-shredding  
- **VCP-RECOVERY** — Chain disruption and consistency recovery  

---

## 🧪 Reference Implementation

A **non-certified reference implementation** is available separately:

https://github.com/veritaschain/vcp-rta-reference

This implementation is provided for demonstration and testing purposes only
and does **not** imply certification or regulatory approval.

---

## 🔒 License

The VeritasChain Protocol specification is licensed under:

**Creative Commons Attribution 4.0 International (CC BY 4.0)**

You may copy, redistribute, and adapt the specification with proper attribution
to **VeritasChain Standards Organization (VSO)**.

---

## 🏛 Maintainer

**VeritasChain Standards Organization (VSO)**  
Website: https://veritaschain.org  
Email: standards@veritaschain.org  
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
