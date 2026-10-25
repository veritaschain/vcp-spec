/* Regression controls for the internal report crosscheck, not new evidence. */
'use strict';
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const cp = require('node:child_process');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
if (!process.argv[2]) throw new Error('Usage: node test_crosscheck.cjs <Python report.json>');
const input = fs.readFileSync(process.argv[2]);
const original = JSON.parse(input);
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'numeric-binding-crosscheck-'));
const results = [];
function run(name, mutate, requiredSuccess) {
  const report = structuredClone(original);
  mutate(report);
  const file = path.join(temporary, name + '.json');
  fs.writeFileSync(file, JSON.stringify(report));
  const executed = cp.spawnSync(process.execPath, [path.join(__dirname, 'crosscheck.cjs'), file], {encoding:'utf8', timeout:30000});
  assert.ifError(executed.error);
  assert.equal(executed.signal, null);
  assert.equal(executed.status === 0, requiredSuccess, name + '\n' + executed.stderr);
  if (requiredSuccess) assert.equal(JSON.parse(executed.stdout).internal_byte_and_crypto_crosscheck, 'PASS');
  else assert.match(executed.stderr, /AssertionError/, name + ': must reject by assertion, not infrastructure failure');
  results.push({name, exit_code:executed.status, expected_acceptance:requiredSuccess, matched:true});
}
const row = (r, id) => r.cases.find(c => c.id === id);
try {
  run('unmodified-positive-control', () => {}, true);
  run('invented-unavailable-signature', r => { row(r,'event-malformed-signature').actual.trace.event_signature = '00'.repeat(64); }, false);
  run('changed-comparison-reference', r => { row(r,'one-ns-stale-statements').reference = 'nonexistent-case'; }, false);
  run('missing-available-signature', r => { delete row(r,'anchor-count-json-number').actual.trace.anchor_signature; }, false);
  run('invented-invalid-anchor-message', r => { row(r,'anchor-count-json-number').actual.trace.anchor_signature_message_hash = '00'.repeat(32); }, false);
  run('changed-byte-relation', r => { row(r,'one-ns-stale-statements').relations.event_hash = 'SAME'; }, false);
  run('swapped-diagnostic-availability', r => {
    const a = row(r,'baseline').actual.trace, b = row(r,'duplicate-event-key').actual.trace;
    b.diagnostic_jcs_hex = a.diagnostic_jcs_hex; b.diagnostic_jcs_hash = a.diagnostic_jcs_hash;
    delete a.diagnostic_jcs_hex; delete a.diagnostic_jcs_hash;
  }, false);
  run('false-independent-reproduction-claim', r => { row(r,'baseline').actual.independent_reproduction = 'established'; }, false);
} finally {
  fs.rmSync(temporary, {recursive:true, force:true});
}
assert.equal(results.length, 8);
console.log(JSON.stringify({status:'UNADOPTED', independent_reproduction:'not_established',
  report_sha256:crypto.createHash('sha256').update(input).digest('hex'), node:process.version,
  tests:8, all_controls_matched:true, results}, null, 2));
