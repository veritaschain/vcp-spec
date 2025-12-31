# VCP Specification v1.1

**VeritasChain Protocol (VCP)** — The open standard for cryptographic audit trails in algorithmic trading systems.

> *"Verify, Don't Trust"*

---

## Overview

VCP v1.1 introduces **Completeness Guarantees**, extending tamper-evidence to ensure that third parties can cryptographically verify not only that events were not altered, but that **no required events were omitted**.

This is a **protocol-compatible / certification-stricter** update from v1.0.

## Key Changes in v1.1

| Change | Impact |
|--------|--------|
| **Three-Layer Architecture** | Clearer separation of integrity mechanisms |
| **External Anchor → REQUIRED** | All tiers now require external anchoring |
| **PrevHash → OPTIONAL** | Simplifies implementation without sacrificing verifiability |
| **Policy Identification → REQUIRED** | Enables multi-tier, multi-policy deployments |
| **VCP-XREF Dual Logging** | OPTIONAL extension for cross-party verification |
| **Error Event Types** | Standardized ERR_* events for consistent error recording |
| **Sidecar Architecture Reference** | Clear integration patterns (Appendix F) |

## Documents

| Language | File | Status |
|----------|------|--------|
| 🇬🇧 English | [VCP-Specification-v1_1_en.md](VCP-Specification-v1_1_en.md) | ✅ Production Ready |
| 🇯🇵 日本語 | [VCP-Specification-v1_1_ja.md](VCP-Specification-v1_1_ja.md) | ✅ Production Ready |
| 🇨🇳 中文 | [VCP-Specification-v1_1_zh.md](VCP-Specification-v1_1_zh.md) | ✅ Production Ready |
| 📄 PDF | [VCP-Specification-v1_1_en.pdf](VCP-Specification-v1_1_en.pdf) | ✅ Available |

## Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 3: External Verifiability                                    │
│  ├─ Digital Signature: REQUIRED                                     │
│  ├─ Timestamp: REQUIRED                                             │
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

## Conformance Tiers

| Tier | Target | Clock Sync | External Anchor | Precision |
|------|--------|------------|-----------------|-----------|
| **Platinum** | HFT/Exchanges | PTPv2 (<1µs) | Every 10 min | NANOSECOND |
| **Gold** | Prop/Institutional | NTP (<1ms) | Every 1 hour | MICROSECOND |
| **Silver** | Retail/MT4/5 | Best effort | Every 24 hours | MILLISECOND |

## Migration from v1.0

VCP v1.1 is **fully backward compatible** at the protocol level. Existing v1.0 implementations continue to work.

For **v1.1 VC-Certified** status:

| Your Tier | Required Changes |
|-----------|-----------------|
| Silver | Add External Anchoring (daily), Add Policy Identification |
| Gold | Add Policy Identification |
| Platinum | Add Policy Identification |

### Grace Period

| Requirement | Deadline |
|-------------|----------|
| External Anchor (Silver) | 2026-06-25 |
| Policy Identification | 2026-03-25 |

## Quick Start

### Minimal Silver Implementation

```python
from vcp import VCPEvent, MerkleTree, OpenTimestamps

# Create event with Policy Identification
event = VCPEvent(
    event_type="ORD",
    policy_id="com.example:silver-mt5-001",
    conformance_tier="SILVER"
)

# Add to Merkle tree
tree.add(event.event_hash)

# Daily anchor (REQUIRED in v1.1)
if should_anchor():
    anchor_record = OpenTimestamps.stamp(tree.root)
    event.set_anchor_reference(anchor_record)
```

### VCP-XREF Dual Logging (Optional)

```python
# Trader side
trader_event = VCPEvent(
    event_type="ORD",
    xref=VCPXRef(
        cross_reference_id=uuid4(),
        party_role="INITIATOR",
        counterparty_id="broker.example.com"
    )
)

# Broker side (references same ID)
broker_event = VCPEvent(
    event_type="ACK",
    xref=VCPXRef(
        cross_reference_id=trader_event.xref.cross_reference_id,
        party_role="COUNTERPARTY",
        counterparty_id="trader.example.com"
    )
)
```

## Related Resources

- **IETF Internet-Draft**: [draft-kamimura-scitt-vcp](https://datatracker.ietf.org/doc/draft-kamimura-scitt-vcp/)
- **Website**: [veritaschain.org](https://veritaschain.org)
- **Developer Docs**: [docs.veritaschain.org](https://docs.veritaschain.org)
- **VC-Certified Program**: [veritaschain.org/certification](https://veritaschain.org/certification)

## License

This specification is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Contact

**VeritasChain Standards Organization (VSO)**  
- Email: standards@veritaschain.org  
- GitHub: [github.com/veritaschain](https://github.com/veritaschain)  
- Support: support@veritaschain.org

---

*"Encoding Trust in the Algorithmic Age"*
