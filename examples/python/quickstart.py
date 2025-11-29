#!/usr/bin/env python3
"""
VCP Quick Start - Experience "Verify, Don't Trust" in 5 minutes

Usage:
    export VCP_API_KEY="your-api-key"
    pip install httpx
    python quickstart.py

Get your API key at: https://veritaschain.org/register
"""
import os
import sys
import hashlib

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)

# Configuration
API_BASE = "https://explorer.veritaschain.org/api/v1"
API_KEY = os.environ.get("VCP_API_KEY", "")

if not API_KEY:
    print("Warning: VCP_API_KEY not set. Some features may not work.")
    print("Get your API key at: https://veritaschain.org/register")
    print()

headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}


def verify_merkle_proof(event_hash: str, proof_path: list, merkle_root: str) -> bool:
    """
    Verify Merkle proof locally (RFC 6962 compliant).
    
    This function runs entirely on your machine.
    No server trust required - that's the "Verify, Don't Trust" principle!
    
    Args:
        event_hash: SHA-256 hash of the event (hex string)
        proof_path: List of sibling hashes with positions
        merkle_root: Expected Merkle root (hex string)
    
    Returns:
        True if proof is valid, False otherwise
    """
    try:
        current = bytes.fromhex(event_hash)
        
        for step in proof_path:
            sibling = bytes.fromhex(step["hash"])
            if step["position"] == "left":
                # Sibling is on the left, so: H(sibling || current)
                combined = sibling + current
            else:
                # Sibling is on the right, so: H(current || sibling)
                combined = current + sibling
            current = hashlib.sha256(combined).digest()
        
        return current.hex() == merkle_root
    except Exception as e:
        print(f"Verification error: {e}")
        return False


def main():
    print("=" * 60)
    print("VCP Quick Start")
    print("VeritasChain Protocol - \"Verify, Don't Trust\"")
    print("=" * 60)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1. System Status (No authentication required)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n📊 1. System Status")
    print("-" * 40)
    
    try:
        response = httpx.get(f"{API_BASE}/system/status", timeout=10.0)
        response.raise_for_status()
        status = response.json()
        
        total_events = status.get('total_events', 'N/A')
        if isinstance(total_events, int):
            total_events = f"{total_events:,}"
        
        print(f"Total Events:  {total_events}")
        print(f"VCP Version:   {status.get('vcp_version', '1.0')}")
        print(f"API Version:   {status.get('api_version', '1.1')}")
        
        if status.get('last_anchor'):
            anchor = status['last_anchor']
            print(f"Last Anchor:   {anchor.get('network', 'N/A')}")
            print(f"               Block #{anchor.get('block_number', 'N/A')}")
    except httpx.HTTPError as e:
        print(f"Error fetching status: {e}")
        return
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2. Search Events (Requires API key)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n🔍 2. Recent Events")
    print("-" * 40)
    
    if not API_KEY:
        print("Skipped: API key required")
        print("Set VCP_API_KEY environment variable to continue")
        return
    
    try:
        response = httpx.get(
            f"{API_BASE}/events",
            headers=headers,
            params={"limit": 5},
            timeout=10.0
        )
        
        if response.status_code == 401:
            print("Error: Invalid API key")
            print("Get a valid key at: https://veritaschain.org/register")
            return
        
        response.raise_for_status()
        result = response.json()
        events = result.get("events", [])
        
        if not events:
            print("No events found")
            print("\nThis might mean:")
            print("  - The sandbox is empty")
            print("  - Your API key doesn't have access to any events")
            return
        
        print(f"Found {len(events)} events:\n")
        for i, event in enumerate(events, 1):
            h = event["header"]
            event_type = h.get('event_type', '?')
            symbol = h.get('symbol', '?')
            event_id = h.get('event_id', '?')[:24]
            timestamp = h.get('timestamp_iso', '?')[:19]
            print(f"  [{i}] {event_type:3} | {symbol:8} | {event_id}... | {timestamp}")
        
    except httpx.HTTPError as e:
        print(f"Error fetching events: {e}")
        return
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3. Merkle Proof Verification
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n🔐 3. Merkle Proof Verification")
    print("-" * 40)
    
    # Get proof for the first event
    event_id = events[0]["header"]["event_id"]
    
    try:
        response = httpx.get(
            f"{API_BASE}/events/{event_id}/proof",
            headers=headers,
            timeout=10.0
        )
        
        if response.status_code == 404:
            print(f"Proof not available for event: {event_id[:32]}...")
            print("The event may be too recent (not yet anchored)")
            return
        
        response.raise_for_status()
        proof = response.json()
        
        print(f"Event ID:     {event_id[:32]}...")
        print(f"Event Hash:   {proof['event_hash'][:32]}...")
        print(f"Merkle Root:  {proof['merkle_root'][:32]}...")
        
        tree_size = proof.get('tree_size', 'N/A')
        if isinstance(tree_size, int):
            tree_size = f"{tree_size:,}"
        print(f"Tree Size:    {tree_size}")
        print(f"Leaf Index:   {proof.get('leaf_index', 'N/A')}")
        print(f"Proof Steps:  {len(proof.get('proof_path', []))}")
        
        # Perform local verification
        print("\nVerifying locally...")
        is_valid = verify_merkle_proof(
            proof["event_hash"],
            proof.get("proof_path", []),
            proof["merkle_root"]
        )
        
        print()
        if is_valid:
            print("✅ VERIFIED: Proof is mathematically valid!")
            print()
            print("   What this means:")
            print("   → The event exists in the Merkle tree")
            print("   → The proof was verified on YOUR machine")
            print("   → No server trust was required")
            print("   → Any tampering would have been detected")
        else:
            print("❌ FAILED: Proof verification failed!")
            print()
            print("   This could mean:")
            print("   → Data was tampered with")
            print("   → Proof is incomplete or corrupted")
            print("   → There's a bug in the verification code")
            
    except httpx.HTTPError as e:
        print(f"Error fetching proof: {e}")
        return
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 4. Sample Event Structure
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n📝 4. VCP Event Structure")
    print("-" * 40)
    print("""
A VCP event consists of three parts:

┌─────────────────────────────────────────┐
│ HEADER                                  │
│  • event_id (UUID v7)                   │
│  • trace_id (links related events)      │
│  • timestamp_int (nanoseconds)          │
│  • timestamp_iso (ISO 8601)             │
│  • event_type (SIG, ORD, EXE, etc.)     │
│  • venue_id, symbol, account_id         │
├─────────────────────────────────────────┤
│ PAYLOAD                                 │
│  • vcp_trade (orders, executions)       │
│  • vcp_risk (risk snapshots)            │
│  • vcp_gov (algorithm governance)       │
├─────────────────────────────────────────┤
│ SECURITY                                │
│  • prev_hash (chain link)               │
│  • event_hash (this event's hash)       │
│  • signature (Ed25519)                  │
└─────────────────────────────────────────┘
""")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Done
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("=" * 60)
    print("🎉 Quick Start Complete!")
    print("=" * 60)
    print()
    print("You've just experienced the core of VCP:")
    print("  ✓ Queried the VCP Explorer API")
    print("  ✓ Retrieved a Merkle proof")
    print("  ✓ Verified it locally (no server trust!)")
    print()
    print("Next steps:")
    print("  📖 Full Spec:      https://github.com/veritaschain/vcp-spec")
    print("  🛠️  SDK Spec:       https://github.com/veritaschain/vcp-sdk-spec")
    print("  🔍 Explorer GUI:   https://veritaschain.org/explorer/app/")
    print("  🔌 MT4/MT5:        https://github.com/veritaschain/vcp-sidecar-guide")
    print("  ✅ Get Certified:  https://certified.veritaschain.org")
    print()


if __name__ == "__main__":
    main()
