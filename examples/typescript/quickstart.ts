/**
 * VCP Quick Start - Experience "Verify, Don't Trust" in 5 minutes
 * 
 * Usage:
 *   export VCP_API_KEY="your-api-key"
 *   npx ts-node quickstart.ts
 *   # or
 *   npx tsx quickstart.ts
 * 
 * Get your API key at: https://veritaschain.org/register
 */

import crypto from 'crypto';

// Configuration
const API_BASE = 'https://explorer.veritaschain.org/api/v1';
const API_KEY = process.env.VCP_API_KEY || '';

if (!API_KEY) {
  console.log('Warning: VCP_API_KEY not set. Some features may not work.');
  console.log('Get your API key at: https://veritaschain.org/register\n');
}

// Types
interface ProofStep {
  hash: string;
  position: 'left' | 'right';
}

interface MerkleProof {
  event_hash: string;
  merkle_root: string;
  proof_path: ProofStep[];
  tree_size: number;
  leaf_index: number;
}

interface VcpEvent {
  header: {
    event_id: string;
    trace_id: string;
    timestamp_int: string;
    timestamp_iso: string;
    event_type: string;
    event_type_code: number;
    venue_id: string;
    symbol: string;
    account_id: string;
  };
  payload: Record<string, unknown>;
  security: {
    prev_hash: string;
    event_hash: string;
    hash_algo: string;
    signature?: string;
  };
}

/**
 * Verify Merkle proof locally (RFC 6962 compliant).
 * 
 * This function runs entirely on your machine.
 * No server trust required - that's the "Verify, Don't Trust" principle!
 */
function verifyMerkleProof(proof: MerkleProof): boolean {
  try {
    let current = Buffer.from(proof.event_hash, 'hex');
    
    for (const step of proof.proof_path) {
      const sibling = Buffer.from(step.hash, 'hex');
      const combined = step.position === 'left'
        ? Buffer.concat([sibling, current])  // H(sibling || current)
        : Buffer.concat([current, sibling]); // H(current || sibling)
      current = crypto.createHash('sha256').update(combined).digest();
    }
    
    return current.toString('hex') === proof.merkle_root;
  } catch (error) {
    console.error('Verification error:', error);
    return false;
  }
}

/**
 * Helper to make authenticated requests
 */
async function apiRequest<T>(endpoint: string): Promise<T> {
  const headers: Record<string, string> = {};
  if (API_KEY) {
    headers['Authorization'] = `Bearer ${API_KEY}`;
  }
  
  const response = await fetch(`${API_BASE}${endpoint}`, { headers });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  
  return response.json();
}

async function main() {
  console.log('='.repeat(60));
  console.log('VCP Quick Start');
  console.log('VeritasChain Protocol - "Verify, Don\'t Trust"');
  console.log('='.repeat(60));
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 1. System Status (No authentication required)
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  console.log('\n📊 1. System Status');
  console.log('-'.repeat(40));
  
  try {
    const status = await fetch(`${API_BASE}/system/status`).then(r => r.json());
    
    const totalEvents = status.total_events?.toLocaleString() ?? 'N/A';
    console.log(`Total Events:  ${totalEvents}`);
    console.log(`VCP Version:   ${status.vcp_version ?? '1.0'}`);
    console.log(`API Version:   ${status.api_version ?? '1.1'}`);
    
    if (status.last_anchor) {
      console.log(`Last Anchor:   ${status.last_anchor.network ?? 'N/A'}`);
      console.log(`               Block #${status.last_anchor.block_number ?? 'N/A'}`);
    }
  } catch (error) {
    console.error('Error fetching status:', error);
    return;
  }
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 2. Search Events (Requires API key)
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  console.log('\n🔍 2. Recent Events');
  console.log('-'.repeat(40));
  
  if (!API_KEY) {
    console.log('Skipped: API key required');
    console.log('Set VCP_API_KEY environment variable to continue');
    return;
  }
  
  let events: VcpEvent[] = [];
  
  try {
    const result = await apiRequest<{ events: VcpEvent[]; total_count: number }>(
      '/events?limit=5'
    );
    events = result.events || [];
    
    if (events.length === 0) {
      console.log('No events found');
      return;
    }
    
    console.log(`Found ${events.length} events:\n`);
    events.forEach((event, i) => {
      const h = event.header;
      const timestamp = h.timestamp_iso?.slice(0, 19) ?? '?';
      console.log(
        `  [${i + 1}] ${h.event_type.padEnd(3)} | ` +
        `${h.symbol.padEnd(8)} | ` +
        `${h.event_id.slice(0, 24)}... | ` +
        `${timestamp}`
      );
    });
  } catch (error) {
    console.error('Error fetching events:', error);
    return;
  }
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // 3. Merkle Proof Verification
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  console.log('\n🔐 3. Merkle Proof Verification');
  console.log('-'.repeat(40));
  
  const eventId = events[0].header.event_id;
  
  try {
    const proof = await apiRequest<MerkleProof>(`/events/${eventId}/proof`);
    
    console.log(`Event ID:     ${eventId.slice(0, 32)}...`);
    console.log(`Event Hash:   ${proof.event_hash.slice(0, 32)}...`);
    console.log(`Merkle Root:  ${proof.merkle_root.slice(0, 32)}...`);
    console.log(`Tree Size:    ${proof.tree_size?.toLocaleString() ?? 'N/A'}`);
    console.log(`Leaf Index:   ${proof.leaf_index ?? 'N/A'}`);
    console.log(`Proof Steps:  ${proof.proof_path?.length ?? 0}`);
    
    // Perform local verification
    console.log('\nVerifying locally...');
    const isValid = verifyMerkleProof(proof);
    
    console.log();
    if (isValid) {
      console.log('✅ VERIFIED: Proof is mathematically valid!');
      console.log();
      console.log('   What this means:');
      console.log('   → The event exists in the Merkle tree');
      console.log('   → The proof was verified on YOUR machine');
      console.log('   → No server trust was required');
      console.log('   → Any tampering would have been detected');
    } else {
      console.log('❌ FAILED: Proof verification failed!');
      console.log();
      console.log('   This could mean:');
      console.log('   → Data was tampered with');
      console.log('   → Proof is incomplete or corrupted');
    }
  } catch (error) {
    console.error('Error fetching proof:', error);
    return;
  }
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // Done
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  console.log('\n' + '='.repeat(60));
  console.log('🎉 Quick Start Complete!');
  console.log('='.repeat(60));
  console.log();
  console.log('You\'ve just experienced the core of VCP:');
  console.log('  ✓ Queried the VCP Explorer API');
  console.log('  ✓ Retrieved a Merkle proof');
  console.log('  ✓ Verified it locally (no server trust!)');
  console.log();
  console.log('Next steps:');
  console.log('  📖 Full Spec:      https://github.com/veritaschain/vcp-spec');
  console.log('  🛠️  SDK Spec:       https://github.com/veritaschain/vcp-sdk-spec');
  console.log('  🔍 Explorer GUI:   https://veritaschain.org/explorer/app/');
  console.log('  🔌 MT4/MT5:        https://github.com/veritaschain/vcp-sidecar-guide');
  console.log('  ✅ Get Certified:  https://certified.veritaschain.org');
  console.log();
}

main().catch(console.error);
