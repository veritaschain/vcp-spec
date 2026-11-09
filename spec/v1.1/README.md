# VCP Specification v1.1

**VeritasChain Protocol (VCP)** — The open standard for cryptographic audit trails in algorithmic trading systems.

> *"Verify, Don't Trust"*

---

> **Superseded by [v1.2](../v1.2/)** (specification GA declared 2026-07-06; tag `v1.2.0`, 2026-10-09). Compatibility from v1.1 to v1.2 is not unconditional: the v1.2 schema rejects some v1.0/v1.1 event types and header fields, so not every v1.1 event validates under v1.2 (see the v1.2 [known issues](../v1.2/README.md#known-issues-in-v12-informative) and [GA-CONSISTENCY.md](../v1.2/GA-CONSISTENCY.md)). Original v1.1 records keep their original validation context and signed bytes; do not rewrite them to satisfy the v1.2 schema. VCP v1.1's integrity alignment with VAP v1.2 is under review (VAP v1.2 §10.4). v1.1 has no tagged release in this repository.
>
> The historical v1.1 specification text retains its original header "Status: Production Ready"; read it as a specification publication status, not implementation production readiness. The snapshot and digests below distinguish the historical bytes from current-branch copies with later notices.
>
> *Corrected 2026-10-28.* This notice previously read: "(Production Ready, GA 2026-07-06) — protocol-compatible with v1.1; all v1.1 events and anchors remain valid and verifiable under v1.2."

---

## Overview

VCP v1.1 introduces completeness verification (§1.1 "Completeness Guarantees"), extending tamper-evidence so that third parties can cryptographically verify not only that events were not altered, but that **no required events were omitted** after anchoring — verifiable at anchor time and at batch granularity, not continuously (events never recorded remain undetectable).

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
| 🇬🇧 English | [VCP-Specification-v1_1_en.md](VCP-Specification-v1_1_en.md) | Published 2025-12-30 (normative) |
| 🇯🇵 日本語 | [VCP-Specification-v1_1_ja.md](VCP-Specification-v1_1_ja.md) | Translation (convenience only; English prevails) |
| 🇨🇳 中文 | [VCP-Specification-v1_1_zh.md](VCP-Specification-v1_1_zh.md) | Translation (convenience only; English prevails) |
| 📄 PDF | [VCP-Specification-v1_1_en.pdf](VCP-Specification-v1_1_en.pdf) | Available |

## Historical source snapshot and digests

Recorded 10 November 2026. Commit
[`48fc17955708d234232ce9aa7e248927832e095f`](https://github.com/veritaschain/vcp-spec/commit/48fc17955708d234232ce9aa7e248927832e095f)
added the version-directory files on 31 December 2025. The following SHA-256
values identify the exact Markdown bytes at that historical commit. This is an
archival reference, not a newly created release, tag, adoption decision or claim
that this snapshot resolves the known integrity issues.

| Historical file | SHA-256 |
|---|---|
| [VCP-Specification-v1_1_en.md](https://github.com/veritaschain/vcp-spec/blob/48fc17955708d234232ce9aa7e248927832e095f/spec/v1.1/VCP-Specification-v1_1_en.md) | `4224c41dd121aa8018b5f38284c5c56889b405c53023ee93472800b49b6f4050` |
| [VCP-Specification-v1_1_ja.md](https://github.com/veritaschain/vcp-spec/blob/48fc17955708d234232ce9aa7e248927832e095f/spec/v1.1/VCP-Specification-v1_1_ja.md) | `d56705604320c51c3543c59ae8f73a5357ecb776a9ce56b237c9b046b6a3802c` |
| [VCP-Specification-v1_1_zh.md](https://github.com/veritaschain/vcp-spec/blob/48fc17955708d234232ce9aa7e248927832e095f/spec/v1.1/VCP-Specification-v1_1_zh.md) | `6b09d62667b1bc8c0bf50be2ad84693d24561f8fa035f8f25dd1bc8f78c6bdb4` |

The current-branch files include later historical notices and are not
byte-identical to this snapshot. Cite the commit and digest when identifying a
historical v1.1 source; specify the implementation's actual validation rules
separately. Preserve existing signed records. No `v1.1.0` tag is created here.

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
- **Explorer API reference**: [veritaschain.org/vcp/explorer-api](https://veritaschain.org/vcp/explorer-api/)
- **VC-Certified Program**: [veritaschain.org/certified](https://veritaschain.org/certified/)

## License

This specification is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Contact

**VeritasChain Standards Organization (VSO)**  
- Email: standards@veritaschain.org  
- GitHub: [github.com/veritaschain](https://github.com/veritaschain)  
- Support: support@veritaschain.org

---

*"Encoding Trust in the Algorithmic Age"*
