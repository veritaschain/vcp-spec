# VCP Quick Start Guide

> Experience VeritasChain Protocol in 5 minutes — no SDK installation required

<p align="center">
  <img src="https://img.shields.io/badge/Time-5%20minutes-blue?style=flat-square" alt="Time"/>
  <img src="https://img.shields.io/badge/SDK-Not%20Required-green?style=flat-square" alt="No SDK"/>
  <img src="https://img.shields.io/badge/VCP-v1.0-blue?style=flat-square" alt="VCP"/>
</p>

---

## 📋 Prerequisites

1. **API Key** — See the [Explorer API page](https://veritaschain.org/vcp/explorer-api/) (no self-service registration page is currently published)
2. **Python 3.10+** or **Node.js 18+** (or just `curl`)

```bash
# Set your API key
export VCP_API_KEY="your-api-key"
```

---

## 🚀 Option 1: curl (Fastest)

No installation required. Just copy and paste:

```bash
# 1. Check system status (no auth required)
curl -s https://explorer.veritaschain.org/api/v1/system/status | jq

# 2. Search recent events
curl -s -H "Authorization: Bearer $VCP_API_KEY" \
  "https://explorer.veritaschain.org/api/v1/events?limit=5" | jq

# 3. Get Merkle proof for an event
curl -s -H "Authorization: Bearer $VCP_API_KEY" \
  "https://explorer.veritaschain.org/api/v1/events/{event_id}/proof" | jq
```

---

## 🐍 Option 2: Python

### Step 1: Install dependency

```bash
pip install httpx
```

### Step 2: Run the quickstart script

```bash
# Download and run
curl -O https://raw.githubusercontent.com/veritaschain/vcp-spec/main/examples/python/quickstart.py
python quickstart.py
```

Or create `quickstart.py` manually:

```python
"""
VCP Quick Start - Experience "Verify, Don't Trust" in 5 minutes
"""
import os
import hashlib
import httpx

API_BASE = "https://explorer.veritaschain.org/api/v1"
API_KEY = os.environ.get("VCP_API_KEY", "your-api-key")
headers = {"Authorization": f"Bearer {API_KEY}"}

def main():
    print("=" * 60)
    print("VCP Quick Start")
    print("=" * 60)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1. System Status
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n📊 1. System Status")
    print("-" * 40)
    
    response = httpx.get(f"{API_BASE}/system/status")
    status = response.json()
    
    print(f"Total Events:  {status.get('total_events', 'N/A'):,}")
    print(f"VCP Version:   {status.get('vcp_version', '1.0')}")
    print(f"API Version:   {status.get('api_version', '1.1')}")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2. Search Events
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n🔍 2. Recent Events")
    print("-" * 40)
    
    response = httpx.get(
        f"{API_BASE}/events",
        headers=headers,
        params={"limit": 5}
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - Check your API key")
        return
    
    result = response.json()
    events = result.get("events", [])
    
    for i, event in enumerate(events, 1):
        h = event["header"]
        print(f"  [{i}] {h['event_type']:3} | {h['symbol']:8} | {h['event_id'][:24]}...")
    
    if not events:
        print("  No events found")
        return
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3. Merkle Proof Verification
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n🔐 3. Merkle Proof Verification")
    print("-" * 40)
    
    event_id = events[0]["header"]["event_id"]
    response = httpx.get(f"{API_BASE}/events/{event_id}/proof", headers=headers)
    
    if response.status_code != 200:
        print(f"Could not fetch proof: {response.status_code}")
        return
    
    proof = response.json()
    
    print(f"Event ID:     {event_id[:32]}...")
    print(f"Event Hash:   {proof['event_hash'][:32]}...")
    print(f"Merkle Root:  {proof['merkle_root'][:32]}...")
    print(f"Tree Size:    {proof.get('tree_size', 'N/A'):,}")
    print(f"Proof Steps:  {len(proof.get('proof_path', []))}")
    
    # Client-side verification
    is_valid = verify_merkle_proof(
        proof["event_hash"],
        proof.get("proof_path", []),
        proof["merkle_root"]
    )
    
    print()
    if is_valid:
        print("✅ MATCH against API-supplied root (not independently anchored)")
        print("   → Path folded locally on YOUR machine")
        print("   → Root and path both came from the API")
    else:
        print("❌ NO MATCH: path does not fold to the API-supplied root")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Done
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "=" * 60)
    print("🎉 Quick Start Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  📖 Specification:  https://github.com/veritaschain/vcp-spec")
    print("  🔍 Explorer GUI:   https://veritaschain.org/explorer/app/")
    print("  ℹ️  VC-Certified:   https://veritaschain.org/certified/ (scheme requires CABs independent of VSO; the only registered CAB is not independent)")


def verify_merkle_proof(event_hash: str, proof_path: list, merkle_root: str) -> bool:
    """
    Check the API-supplied audit path against the API-supplied root using the
    VCP v1.2 §6.2 example construction (not RFC 6962; see Known issues P3).
    For an RFC 6962 verifier, see https://github.com/veritaschain/vcp-sdk
    (pre-release, first-party).
    
    This function runs on your machine, but the root it compares against
    comes from the same API; the root is not independently anchored here.
    """
    try:
        current = bytes.fromhex(event_hash)
        
        for step in proof_path:
            sibling = bytes.fromhex(step["hash"])
            if step["position"] == "left":
                combined = sibling + current
            else:
                combined = current + sibling
            current = hashlib.sha256(combined).digest()
        
        return current.hex() == merkle_root
    except Exception:
        return False


if __name__ == "__main__":
    main()
```

### Expected Output

```
============================================================
VCP Quick Start
============================================================

📊 1. System Status
----------------------------------------
Total Events:  12,160,243
VCP Version:   1.0
API Version:   1.1

🔍 2. Recent Events
----------------------------------------
  [1] ORD | EURUSD   | 01934e3a-7b2c-7f93-8f2a...
  [2] EXE | EURUSD   | 01934e3a-7b2d-7f93-8f2a...
  [3] SIG | BTCUSD   | 01934e3a-7b2e-7f93-8f2a...
  [4] ACK | USDJPY   | 01934e3a-7b2f-7f93-8f2a...
  [5] RSK | PORTFOLIO| 01934e3a-7b30-7f93-8f2a...

🔐 3. Merkle Proof Verification
----------------------------------------
Event ID:     01934e3a-7b2c-7f93-8f2a-12345678...
Event Hash:   a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6...
Merkle Root:  xyz789abc123def456ghi789jkl0mno1...
Tree Size:    1,048,576
Proof Steps:  20

✅ MATCH against API-supplied root (not independently anchored)
   → Path folded locally on YOUR machine
   → Root and path both came from the API

============================================================
🎉 Quick Start Complete!
============================================================

Next steps:
  📖 Specification:  https://github.com/veritaschain/vcp-spec
  🔍 Explorer GUI:   https://veritaschain.org/explorer/app/
  ℹ️  VC-Certified:   https://veritaschain.org/certified/ (scheme requires CABs independent of VSO; the only registered CAB is not independent)
```

> **What the local check does (and does not do).** `verify_merkle_proof` checks
> the API-supplied audit path against the API-supplied root using the VCP v1.2
> §6.2 example construction. It is **not** RFC 6962: it starts from the raw
> event hash and applies no `0x00`/`0x01` domain-separation prefixes (research
> observation P3; see
> [Known issues](../README.md#-known-issues-in-v12-informative)). Because the
> root comes from the same API, a match shows internal consistency only, not
> independent anchoring. For an RFC 6962 verifier, see
> [veritaschain/vcp-sdk](https://github.com/veritaschain/vcp-sdk) (pre-release,
> first-party).

---

## 📘 Option 3: TypeScript / Node.js

### Step 1: Setup

```bash
mkdir vcp-quickstart && cd vcp-quickstart
npm init -y
npm install node-fetch@3
```

### Step 2: Create quickstart.ts

```typescript
import crypto from 'crypto';

const API_BASE = 'https://explorer.veritaschain.org/api/v1';
const API_KEY = process.env.VCP_API_KEY || 'your-api-key';

interface ProofStep {
  hash: string;
  position: 'left' | 'right';
}

interface MerkleProof {
  event_hash: string;
  merkle_root: string;
  proof_path: ProofStep[];
  tree_size: number;
}

// Checks the API-supplied audit path against the API-supplied root using the
// VCP v1.2 §6.2 example construction (not RFC 6962; see Known issues P3).
// For an RFC 6962 verifier, see https://github.com/veritaschain/vcp-sdk
// (pre-release, first-party).
function verifyMerkleProof(proof: MerkleProof): boolean {
  try {
    let current = Buffer.from(proof.event_hash, 'hex');
    
    for (const step of proof.proof_path) {
      const sibling = Buffer.from(step.hash, 'hex');
      const combined = step.position === 'left'
        ? Buffer.concat([sibling, current])
        : Buffer.concat([current, sibling]);
      current = crypto.createHash('sha256').update(combined).digest();
    }
    
    return current.toString('hex') === proof.merkle_root;
  } catch {
    return false;
  }
}

async function main() {
  console.log('='.repeat(60));
  console.log('VCP Quick Start - TypeScript');
  console.log('='.repeat(60));
  
  // 1. System Status
  console.log('\n📊 1. System Status');
  const statusRes = await fetch(`${API_BASE}/system/status`);
  const status = await statusRes.json();
  console.log(`Total Events: ${status.total_events?.toLocaleString() ?? 'N/A'}`);
  
  // 2. Search Events
  console.log('\n🔍 2. Recent Events');
  const eventsRes = await fetch(`${API_BASE}/events?limit=5`, {
    headers: { 'Authorization': `Bearer ${API_KEY}` }
  });
  const eventsData = await eventsRes.json();
  
  for (const event of eventsData.events || []) {
    const h = event.header;
    console.log(`  ${h.event_type} | ${h.symbol} | ${h.event_id.slice(0, 24)}...`);
  }
  
  // 3. Merkle Proof
  if (eventsData.events?.length > 0) {
    console.log('\n🔐 3. Merkle Proof Verification');
    const eventId = eventsData.events[0].header.event_id;
    const proofRes = await fetch(`${API_BASE}/events/${eventId}/proof`, {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    });
    const proof: MerkleProof = await proofRes.json();
    
    const isValid = verifyMerkleProof(proof);
    console.log(`\n${isValid ? '✅ MATCH' : '❌ NO MATCH'}: against API-supplied root (not independently anchored)`);
    if (isValid) {
      console.log('   → Path folded locally on YOUR machine; root came from the API');
    }
  }
  
  console.log('\n🎉 Quick Start Complete!');
}

main().catch(console.error);
```

### Step 3: Run

```bash
npx ts-node quickstart.ts
# or
npx tsx quickstart.ts
```

---

## 📊 Event Types Reference

Codes from the VCP v1.0 fixed registry (v1.0 §3.2.1), as used by the Explorer
API samples. The v1.2 schema identifies event types by name; `PRT`, `REJ`, `ALG`,
`AUD`, `REC` and `SNC` are not in its `EventType` enum (see Known issues).

| Code | Type | Description |
|------|------|-------------|
| 1 | `SIG` | Signal/decision generated |
| 2 | `ORD` | Order sent |
| 3 | `ACK` | Order acknowledged |
| 4 | `EXE` | Full execution |
| 5 | `PRT` | Partial fill |
| 6 | `REJ` | Order rejected |
| 7 | `CXL` | Order cancelled |
| 8 | `MOD` | Order modified |
| 9 | `CLS` | Position closed |
| 20 | `ALG` | Algorithm update |
| 21 | `RSK` | Risk parameter change |
| 22 | `AUD` | Audit request |
| 98 | `HBT` | Heartbeat |
| 99 | `ERR` | Error |
| 100 | `REC` | Recovery |
| 101 | `SNC` | Clock sync status |

---

## 🔗 API Endpoints Used

| Endpoint | Auth | Description |
|----------|------|-------------|
| `GET /system/status` | No | System statistics |
| `GET /events` | Yes | Search events |
| `GET /events/:id` | Yes | Get event by ID |
| `GET /events/:id/proof` | Yes | Get Merkle proof |

Full API documentation: [Explorer API Reference](https://github.com/veritaschain/vcp-explorer-api)

---

## ❓ Troubleshooting

### "401 Unauthorized"
```bash
# Check your API key is set
echo $VCP_API_KEY

# Make sure it's exported
export VCP_API_KEY="your-actual-key"
```

### "Connection refused"
- Check your internet connection
- Verify the API is accessible: `curl https://explorer.veritaschain.org/api/v1/system/status`

### "NO MATCH" from the Merkle check
- This is expected if using demo/sample data (the
  [vcp-explorer-api](https://github.com/veritaschain/vcp-explorer-api) README
  states that its server currently returns mock data)
- The quickstart check uses the §6.2 example construction, not RFC 6962, so a
  path from an RFC 6962 tree will not match (research observation P3)

---

## 🔗 Next Steps

| Step | Link |
|------|------|
| 📋 Read Full Specification | [VCP Spec v1.2](../spec/v1.2/VCP-Specification-v1_2_en.md) · [v1.0 (as used by the Explorer API samples)](../VCP-Specification-v1_0_en.md) |
| 🛠️ SDK Development | [SDK Specification](https://github.com/veritaschain/vcp-sdk-spec) |
| 🔍 Explore Events | [VCP Explorer GUI](https://veritaschain.org/explorer/app/) |
| 🔌 MT4/MT5 Integration | [Sidecar Guide](https://github.com/veritaschain/vcp-sidecar-guide) |
| ℹ️ Certification scheme | [VC-Certified](https://veritaschain.org/certified/) — the scheme requires Conformity Assessment Bodies independent of the scheme owner, not VSO; the only registered CAB, VeritasChain Co., Ltd., operates VSO and is not independent |

---

<p align="center">
  <strong>VeritasChain Standards Organization</strong><br/>
  <em>"Verify, Don't Trust"</em>
</p>
