/* Internal second code path: restricted JCS bytes, SHA-256 and Ed25519.
 * Not a native parser, semantic validator or independent third-party run. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const root = __dirname;
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const digest = b => 'sha256:' + sha(b);
const domain = n => Buffer.from('VCP-RESEARCH-20261024-V0/' + n + '\0', 'ascii');
const read = n => JSON.parse(fs.readFileSync(path.join(root, n), 'utf8'));
const fixture = read('data/cases.json');
const manifest = read('manifest.json');
const reportPath = process.argv[2];
if (!reportPath) throw new Error('Usage: node crosscheck.cjs <Python report.json>');
const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
// This restricted encoder covers the ASCII-key synthetic objects in this suite,
// not arbitrary RFC 8785 input. JSON numbers are allowed only for diagnostic JCS.
function jcs(value, diagnostic = false) {
  if (value === null || typeof value === 'boolean' || typeof value === 'string') return JSON.stringify(value);
  if (typeof value === 'number') {
    assert(diagnostic && Number.isSafeInteger(value), 'candidate numbers forbidden');
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return '[' + value.map(v => jcs(v, diagnostic)).join(',') + ']';
  assert(value && typeof value === 'object');
  return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + jcs(value[k], diagnostic)).join(',') + '}';
}
const rawJcs = (v, d = false) => Buffer.from(jcs(v, d), 'utf8');
const prefixed = (name, v) => Buffer.concat([domain(name), rawJcs(v)]);
function publicKey(role) {
  const seed = crypto.createHash('sha256').update('PUBLIC TEST MATERIAL numeric-byte-binding-v0 ' + role).digest();
  const privateKey = crypto.createPrivateKey({key: Buffer.concat([Buffer.from('302e020100300506032b657004220420', 'hex'), seed]), format:'der', type:'pkcs8'});
  const key = crypto.createPublicKey(privateKey);
  const raw = key.export({format:'der', type:'spki'}).subarray(-32).toString('hex');
  assert.equal(raw, fixture.test_keys[role].public_key_hex);
  assert.equal(seed.toString('hex'), fixture.test_keys[role].public_test_seed_hex);
  return key;
}
const keys = {event:publicKey('event'), anchor:publicKey('anchor')};
assert.equal(fixture.cases.length, 45);
assert.equal(report.cases.length, 45);
assert.equal(report.experiment, fixture.experiment);
assert.equal(report.source_commit, fixture.source_commit);
assert.equal(report.status, 'UNADOPTED');
assert.equal(report.independent_reproduction, 'not_established');
assert.equal(report.manifest_sha256, sha(fs.readFileSync(path.join(root, 'manifest.json'))));
assert.deepEqual(report.experiment_files, manifest.files);
for (const [name, hash] of Object.entries(manifest.files)) assert.equal(sha(fs.readFileSync(path.join(root, name))), hash);
const expectedIds = fixture.cases.map(c => c.id);
assert.equal(new Set(expectedIds).size, 45);
assert.deepEqual(report.cases.map(c => c.id), expectedIds);
let signatures = 0, eventHashes = 0, externalHashes = 0, diagnostics = 0;
const actualCounts = {}, recomputedTraces = {};
for (let i = 0; i < fixture.cases.length; i++) {
  const c = fixture.cases[i], r = report.cases[i], b = c.bundle, expected = {};
  assert.equal(r.reference, c.reference, c.id + ': reference');
  assert.deepEqual(r.expected, c.expected, c.id);
  assert.deepEqual(r.actual.checks, c.expected.checks, c.id);
  assert.equal(r.actual.covered_checks_result, c.expected.covered_checks_result);
  assert.equal(r.matched, true);
  assert.equal(r.actual.status, 'UNADOPTED');
  assert.equal(r.actual.independent_reproduction, 'not_established');
  for (const key of ['native_vcp_conformance', 'real_identity_and_authorization', 'external_receipt_and_time']) {
    assert.equal(r.actual[key], 'not_assessed');
  }
  assert.equal(r.actual.transport_used_for_semantics, false);
  actualCounts[r.actual.covered_checks_result] = (actualCounts[r.actual.covered_checks_result] || 0) + 1;
  // The fixed fixture expectations select available byte operations; report
  // field presence must never decide what is checked. Shape/semantic outcomes
  // are still not independently derived by this restricted byte crosscheck.
  if (c.expected.checks.event_shape === 'PASS') {
    const event = JSON.parse(b.event_json), canonical = rawJcs(event), preimage = prefixed('EVENT', event);
    expected.event_jcs_hex = canonical.toString('hex');
    expected.event_preimage_hex = preimage.toString('hex');
    expected.event_hash = digest(preimage);
    const leaf = digest(Buffer.concat([Buffer.from([0]), Buffer.from(sha(preimage), 'hex')]));
    expected.leaf_hash = leaf;
    expected.root_hash = leaf; // This suite supplies exactly one event.
    eventHashes++;
  }
  if (c.expected.checks.event_parse === 'PASS') {
    const bytes = rawJcs(JSON.parse(b.event_json), true);
    expected.diagnostic_jcs_hex = bytes.toString('hex');
    expected.diagnostic_jcs_hash = sha(bytes);
    diagnostics++;
  }
  expected.policy_digest = digest(Buffer.from(b.policy_hex, 'hex'));
  for (const role of ['event', 'anchor']) {
    const encodingValid = c.expected.checks[role + '_signature_encoding'] === 'PASS';
    let sig;
    if (encodingValid) {
      sig = Buffer.from(b[role + '_signature'], 'base64');
      assert.equal(sig.length, 64);
      assert.equal(sig.toString('base64'), b[role + '_signature']);
      expected[role + '_signature'] = sig.toString('hex');
    }
    const shape = role === 'event' ? 'event_statement_shape' : 'anchor_shape';
    if (c.expected.checks[shape] === 'PASS') {
      const preimage = prefixed(role.toUpperCase() + '-SIGNATURE', b[role + '_statement']);
      expected[role + '_signature_preimage_hex'] = preimage.toString('hex');
      expected[role + '_signature_message_hash'] = sha(preimage);
      if (encodingValid) {
        const valid = crypto.verify(null, preimage, keys[role], sig);
        assert.equal(r.actual.checks[role + '_crypto'], valid ? 'PASS' : 'FAIL', c.id + ':' + role);
        signatures++;
      } else assert.equal(r.actual.checks[role + '_crypto'], 'UNASSESSED');
    } else assert.equal(r.actual.checks[role + '_crypto'], 'UNASSESSED');
  }
  if (c.expected.checks.anchor_shape === 'PASS' && c.expected.checks.anchor_signature_encoding === 'PASS') {
    const preimage = prefixed('EXTERNAL-COMMITMENT', {AnchorStatement:b.anchor_statement, Signature:b.anchor_signature});
    expected.external_preimage_hex = preimage.toString('hex');
    expected.external_commitment = digest(preimage);
    assert.equal(r.actual.checks.external_binding, b.external_commitment === digest(preimage) ? 'PASS' : 'FAIL');
    externalHashes++;
  }
  assert.deepEqual(r.actual.trace, expected, c.id + ': complete byte trace');
  recomputedTraces[c.id] = expected;
}
for (let i = 0; i < fixture.cases.length; i++) {
  const c = fixture.cases[i], r = report.cases[i], observed = {};
  const trace = recomputedTraces[c.id], reference = recomputedTraces[c.reference];
  assert(reference, 'unknown reference');
  for (const name of Object.keys(c.expected.relations)) {
    observed[name] = !(name in trace) || !(name in reference) ? 'UNAVAILABLE' :
      trace[name] === reference[name] ? 'SAME' : 'CHANGED';
  }
  assert.deepEqual(observed, c.expected.relations, c.id + ': fixture relations');
  assert.deepEqual(r.relations, observed, c.id + ': report relations');
}
assert.equal(eventHashes, 40);
assert.equal(signatures, 88);
assert.equal(externalHashes, 44);
assert.equal(diagnostics, 44);
assert.deepEqual(report.summary.covered_checks_counts, actualCounts);
assert.equal(report.summary.case_count, 45);
assert.deepEqual(report.summary.mismatches, []);
assert.equal(report.summary.all_expected_results_matched_and_regressions_passed, true);
assert.equal(report.regressions.tests_run, 20);
assert.equal(report.regressions.success_without_skips_or_expected_failures, true);
console.log(JSON.stringify({status:'UNADOPTED', independent_reproduction:'not_established',
  experiment:fixture.experiment, node:process.version, openssl:process.versions.openssl,
  report_sha256:sha(fs.readFileSync(reportPath)), crosscheck_sha256:sha(fs.readFileSync(__filename)),
  cases:45, candidate_event_hashes:eventHashes, actual_ed25519_checks:signatures,
  external_commitments:externalHashes, diagnostic_jcs:diagnostics, byte_relations_checked:450,
  internal_byte_and_crypto_crosscheck:'PASS', semantic_crosscheck:'not_performed'}, null, 2));
