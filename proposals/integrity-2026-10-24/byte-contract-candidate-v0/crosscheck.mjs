// UNADOPTED, internal cross-language byte check. Not a full input/trust validator.
// Uses only public synthetic seeds. Does not import or invoke the Python checker.
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash, createPrivateKey, createPublicKey, sign, verify } from 'node:crypto';

const dir = process.argv[2] ?? join(dirname(fileURLToPath(import.meta.url)), 'data');
const v = JSON.parse(readFileSync(join(dir, 'vectors.json'), 'utf8'));
const trees = readFileSync(join(dir, 'merkle-vectors.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
const counts = {};
function eq(actual, expected, group) {
  if (actual !== expected) throw new Error(`${group}: mismatch`);
  counts[group] = (counts[group] ?? 0) + 1;
}
function canonical(value) {
  if (value === null || typeof value === 'boolean') return JSON.stringify(value);
  if (typeof value === 'string') {
    if (!value.isWellFormed()) throw new Error('lone surrogate');
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (typeof value === 'object') {
    // ECMAScript sort compares UTF-16 code units, as required by JCS.
    return '{' + Object.keys(value).sort().map(k => canonical(k) + ':' + canonical(value[k])).join(',') + '}';
  }
  throw new Error('Numbers unsupported in this closed candidate');
}
const sha = b => createHash('sha256').update(b).digest();
const cat = (...parts) => Buffer.concat(parts);
const domains = {
  event: Buffer.from('VCP-RESEARCH-20261024-V0/EVENT\0'),
  event_signature: Buffer.from('VCP-RESEARCH-20261024-V0/EVENT-SIGNATURE\0'),
  anchor_signature: Buffer.from('VCP-RESEARCH-20261024-V0/ANCHOR-SIGNATURE\0'),
  external: Buffer.from('VCP-RESEARCH-20261024-V0/EXTERNAL-COMMITMENT\0'),
};
const preimage = (kind, obj) => cat(domains[kind], Buffer.from(canonical(obj), 'utf8'));
const leaf = d => sha(cat(Buffer.from([0]), d));
const branch = (a, b) => sha(cat(Buffer.from([1]), a, b));

// An incremental frontier, rather than the Python recursive tree constructor.
function treeRoot(digests) {
  const frontier = [];
  for (const digest of digests) {
    let node = leaf(digest), level = 0;
    while (frontier[level]) {
      node = branch(frontier[level], node);
      frontier[level++] = null;
    }
    frontier[level] = node;
  }
  let root = null;
  for (const node of frontier) if (node) root = root ? branch(node, root) : node;
  return root ?? sha(Buffer.alloc(0));
}
// A recursive size/index-directed proof fold, separate from Python's iterative one.
function fold(digest, index, count, proof) {
  let used = 0;
  function walk(i, n) {
    if (n === 1) return leaf(digest);
    let k = 1;
    while (k * 2 < n) k *= 2;
    const child = i < k ? walk(i, k) : walk(i - k, n - k);
    if (used >= proof.length) throw new Error('short proof');
    const sibling = proof[used++];
    return i < k ? branch(child, sibling) : branch(sibling, child);
  }
  if (index < 0 || index >= count) throw new Error('index');
  const root = walk(index, count);
  if (used !== proof.length) throw new Error('surplus proof');
  return root;
}
const privateKeys = {}, publicKeys = {};
for (const [role, item] of Object.entries(v.public_test_keys)) {
  // RFC 8410 PKCS#8 / SubjectPublicKeyInfo wrappers for raw Ed25519 test keys.
  privateKeys[role] = createPrivateKey({format:'der', type:'pkcs8', key: cat(
    Buffer.from('302e020100300506032b657004220420', 'hex'), Buffer.from(item.PUBLIC_TEST_SEED_HEX, 'hex'))});
  publicKeys[role] = createPublicKey(privateKeys[role]);
  const spki = publicKeys[role].export({format:'der', type:'spki'});
  eq(spki.subarray(-32).toString('hex'), item.public_key_hex, 'derived_public_key');
}
for (const [kind, value] of Object.entries(domains)) eq(value.toString('hex'), v.domain_prefixes_hex[kind], 'domain');
for (const row of [...v.events, ...v.extra_events]) {
  eq(canonical(row.input), row.jcs_utf8, 'event_jcs');
  eq(preimage('event', row.input).toString('hex'), row.preimage_hex, 'event_preimage');
  eq('sha256:' + sha(preimage('event', row.input)).toString('hex'), row.event_hash, 'event_hash');
}
const sigGroups = [['event_signature','event',v.event_signatures], ['anchor_signature','anchor',[v.anchor]]];
for (const [kind, role, rows] of sigGroups) for (const row of rows) {
  const message = preimage(kind, row.statement), signature = Buffer.from(row.signature, 'base64');
  eq(canonical(row.statement), row.jcs_utf8, 'signed_jcs');
  eq(message.toString('hex'), row.preimage_hex, 'signed_preimage');
  eq(verify(null, message, publicKeys[role], signature), true, 'signature_verify');
  eq(sign(null, message, privateKeys[role]).toString('base64'), row.signature, 'signature_generation');
}
for (const test of v.signature_mutations) {
  const isAnchor = test.kind === 'anchor_signature';
  const row = isAnchor ? v.anchor : v.event_signatures[0];
  const obj = structuredClone(row.statement);
  let at = obj;
  for (const p of test.path.slice(0,-1)) at = at[p];
  at[test.path.at(-1)] = test.replacement;
  eq(verify(null, preimage(test.kind,obj), publicKeys[isAnchor?'anchor':'event'], Buffer.from(row.signature,'base64')), false, 'signed_mutation');
}
for (const row of v.signed_inconsistencies)
  eq(verify(null, preimage('anchor_signature', row.statement), publicKeys.anchor, Buffer.from(row.signature,'base64')), true, 'inconsistent_record_raw_signature_only');
const digests = v.events.map(e => Buffer.from(e.event_hash.slice(7), 'hex'));
eq(treeRoot([]).toString('hex'), v.empty_root_hex, 'empty_root');
for (const row of trees) {
  const n = Number(row.count); // SMALL synthetic tree sizes only, never timestamps.
  eq(treeRoot(digests.slice(0,n)).toString('hex'), row.root_hex, 'merkle_root');
  for (const proof of row.proofs) {
    const i = Number(proof.index);
    eq(fold(digests[i], i, n, proof.nodes_hex.map(h=>Buffer.from(h,'hex'))).toString('hex'), row.root_hex, 'merkle_membership');
  }
}
for (const row of v.numeric_vectors) {
  const value = JSON.parse(row.input_json);
  const [lo, hi] = row.field === 'EventCount' ? [1n,2147483647n] : row.field.startsWith('LeafIndex') ? [0n,2n] : [0n,9223372036854775807n];
  // No binary64 conversion on accepted values. Rejected JSON numeric examples
  // may already have lost precision in JSON.parse; their type is rejected first.
  const match = typeof value === 'string' ? /^(?:0|[1-9][0-9]*)$/u.exec(value) : null;
  const good = match !== null && match[0] === value && value.length <= 19 &&
    BigInt(value) >= lo && BigInt(value) <= hi;
  eq(good ? 'accept' : 'reject', row.expected, 'numeric_exact_bigint');
}
const external = preimage('external', {AnchorStatement:v.anchor.statement, Signature:v.anchor.signature});
eq(external.toString('hex'), v.anchor.external_preimage_hex, 'external_preimage');
eq('sha256:' + sha(external).toString('hex'), v.anchor.external_commitment, 'external_commitment');
eq('sha256:' + sha(Buffer.from(v.policy_bytes_hex,'hex')).toString('hex'), v.policy_digest, 'policy_bytes');
process.stdout.write(JSON.stringify({status:'internal byte agreement; not independent reproduction', node:process.version, openssl:process.versions.openssl,
  scope:'known-answer JCS subset, hashes, trees/proofs, raw signatures and decimal fields; not full schema/trust/receipt validation', counts}) + '\n');
