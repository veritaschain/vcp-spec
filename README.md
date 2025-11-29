![VCP Version](https://img.shields.io/badge/VCP-v1.0-blue)
![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-green)

# VeritasChain Protocol (VCP) — Specification v1.0

## ⚡ Quick Start (5 Minutes)

Try VCP without installing any SDK:
```bash
# Install HTTP client
pip install httpx

# Run quickstart
curl -O https://raw.githubusercontent.com/veritaschain/vcp-spec/main/examples/python/quickstart.py
python quickstart.py
```

The **VeritasChain Protocol (VCP)** is a global open standard for  
**immutable, verifiable, cryptographically-secured audit trails**  
in algorithmic and AI-driven trading systems.

This repository hosts the **official v1.0 normative specification**,  
maintained by the **VeritasChain Standards Organization (VSO)**.

---

## 🎯 Purpose

VCP provides a **globally consistent, tamper-evident audit format** that allows  
exchanges, brokers, prop firms, regulators, and infrastructure providers to  
mathematically verify the truth of every **signal, decision, order, execution,  
and risk control event** in an algorithmic trading system.

It is designed for compliance with **MiFID II, EU AI Act, GDPR, CAT Rule 613**,  
and global algorithmic auditability requirements.

---

## 📘 Documents

### ✔ Normative Specification (English)
- [`VCP-Specification-v1_0_en.md`](./VCP-Specification-v1_0_en.md) — **authoritative reference**

### ✔ Human-Friendly HTML Overview
- [`VCP-Specification-v1_0-styled.html`](./VCP-Specification-v1_0-styled.html)

### ✔ Other Languages
- 日本語 (ja): [`VCP-Specification-v1_0-ja.md`](./VCP-Specification-v1_0-ja.md)
- 简体中文 (zh-CN): [`VCP-Specification-v1_0-zh.md`](./VCP-Specification-v1_0-zh.md)

---

## 📚 What is VCP?

VCP defines the **full lifecycle audit model** for algorithmic trading:

- Universal schema for **trading events**
- **UUID v7** identifiers with time-ordered traceability
- Hash-chain protected **immutable logs**
- **RFC 8785** canonical JSON serialization (JCS)
- **RFC 6962** Merkle Tree anchoring to public chains
- Built-in transparency for **AI decision-making** (model hashes, factors, explainability)
- GDPR-aligned **crypto-shredding**
- Compliance mapping for major global regulations

### Supported Modules
- **VCP-CORE** — Header, timestamps, security metadata  
- **VCP-TRADE** — Order and execution payloads  
- **VCP-GOV** — AI governance and explainability  
- **VCP-RISK** — Risk control parameters & snapshots  
- **VCP-PRIVACY** — Pseudonymization & crypto-shredding  
- **VCP-RECOVERY** — Chain break and consistency recovery  

---

## ✨ Minimal Example (VCP-CORE + TRADE)

```json
{
  "event_id": "01934e3a-7b2c-7f93-8f2a-1234567890ab",
  "timestamp": "2025-11-24T14:02:05.123456Z",
  "event_type": "ORD",
  "symbol": "USDJPY",
  "vcp_trade": {
    "side": "BUY",
    "order_type": "MARKET",
    "price": "156.234",
    "quantity": "1.00"
  }
}
```

This is the minimal valid structure of a VCP event in canonical JSON.

---

## 🧪 Conformance Testing

Official v1.0 conformance tests and example payload collections:

**https://github.com/veritaschain/vcp-conformance-guide**

Includes:
- Event validation suite  
- Canonical JSON checks  
- Merkle proof verifiers  
- End-to-end traceability examples  

---

## 🔒 License

This specification is licensed under  
**Creative Commons Attribution 4.0 International (CC BY 4.0)**.

You may copy, redistribute, or adapt this work  
as long as proper attribution to **VSO** is provided.

See `LICENSE` for full terms.

---

## 🏛 Maintainer

**VeritasChain Standards Organization (VSO)**  
Website: https://veritaschain.org  
Email: info@veritaschain.org  
GitHub: https://github.com/veritaschain

---

## 🤝 Contributions

We welcome:
- Implementation feedback  
- Early-adopter test results  
- Interoperability proposals  
- Suggestions for v1.1 / v2.0 extensions  

Open an Issue or Pull Request to contribute.

---

## 🌍 Acknowledgment

VCP v1.0 was developed with contributions from  
industry practitioners, cryptographers, auditors,  
and multi-model AI deep analysis (GPT, Gemini, Claude).

---

**VeritasChain Protocol — Establishing Truth in Algorithmic Trading.**
