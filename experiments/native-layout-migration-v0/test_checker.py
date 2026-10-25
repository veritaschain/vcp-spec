"""Counterexample and preservation controls, additional to the frozen case matrix."""
import copy
import json
import hashlib
import unittest
from pathlib import Path
import checker as ck
import fixtures as fx
from schema_builder import build

class Controls(unittest.TestCase):
    def setUp(self):self.b,self.c=fx.base()
    def result(self):return ck.check(self.b,self.c)
    def test_schema_reproduces(self):self.assertEqual(build(),ck.SCHEMA)
    def test_frozen_inputs_reproduce(self):
        self.assertEqual(fx.rawjson(fx.document()),(fx.HERE/'data/cases.json').read_bytes())
    def test_checker_does_not_mutate_inputs(self):
        before=copy.deepcopy((self.b,self.c));self.result();self.assertTrue(ck.same(before[0],self.b));self.assertTrue(ck.same(before[1],self.c))
    def test_no_false_independence_or_native_conformance(self):
        r=self.result();self.assertEqual(r['covered_checks'],'PASS');self.assertEqual(r['native_conformance'],'UNASSESSED');self.assertEqual(r['independent_reproduction'],'not_established')
    def test_original_integer_precision_above_binary64(self):
        raws=[bytes.fromhex(s['OriginalHex']) for s in self.b['SourceArtifacts']]
        ns=[ck.strict_json(s)['TimestampInt'] for s in raws]
        self.assertEqual(ns[1]-ns[0],1);self.assertEqual(float(ns[1]),float(ns[0]))
        self.assertEqual(self.result()['covered_checks'],'PASS')
    def test_merkle_three_leaves_is_not_duplicate_last(self):
        hs=[ck.digest(bytes([i])) for i in range(3)]
        a,b,c=[hashlib.sha256(b'\0'+bytes.fromhex(h[7:])).digest() for h in hs]
        manual=hashlib.sha256(b'\1'+hashlib.sha256(b'\1'+a+b).digest()+c).digest()
        self.assertEqual(ck.tree(hs),manual);self.assertNotEqual(ck.tree(hs),ck.tree(hs+[hs[-1]]))
    def test_empty_tree_is_not_an_empty_batch(self):
        self.assertEqual(ck.tree([]),hashlib.sha256(b'').digest());self.b['Events']=[]
        self.assertEqual(self.result()['checks']['layout']['status'],'FAIL')
    def test_duplicate_keys_are_rejected_at_nested_level(self):
        with self.assertRaises(ck.Finding):ck.strict_json(b'{"outer":{"x":1,"x":2}}')
    def test_non_json_nan_is_rejected(self):
        with self.assertRaises(ck.Finding):ck.strict_json(b'{"x":NaN}')
    def test_bool_and_number_are_distinct(self):
        self.assertFalse(ck.same({'x':True},{'x':1}));self.assertFalse(ck.same({'x':1},{'x':1.0}))
    def test_hex_whitespace_is_not_silently_accepted(self):
        self.b['SourceArtifacts'][0]['RetainedHex']+='\n'
        self.assertEqual(self.result()['checks']['source_retention']['status'],'FAIL')
    def test_unpaired_surrogate_fails_without_crash(self):
        self.b['Events'][0]['Commitment']['Header']['EventID']='\ud800'
        self.assertEqual(self.result()['covered_checks'],'FAIL')
    def test_unknown_policy_does_not_hide_other_role_failure(self):
        self.c['Policies']['registration']=None
        self.b['Policies']['numeric']=(bytes.fromhex(self.b['Policies']['numeric'])+b'\n').hex()
        r=self.result();self.assertEqual(r['checks']['policy_binding']['status'],'FAIL')
        self.assertIn('no configured policy',r['checks']['policy_binding']['detail'])
        self.assertIn('not bound',r['checks']['policy_binding']['detail'])
    def test_unknown_time_does_not_hide_other_event_failure(self):
        self.b['Events'][0]['Commitment']['Header']['TimestampISO']='2016-12-31T23:59:60.000000000Z'
        self.b['Events'][1]['Commitment']['Header']['TimestampInt']=str(ck.MAX63+1)
        fx.seal(self.b,self.c)
        self.assertEqual(self.result()['checks']['numeric_time']['status'],'FAIL')
    def test_signature_domain_role_substitution_fails(self):
        e=self.b['Events'][0];e['Signature']=fx.sign('anchor-signature',ck.jcs(e['Statement']));fx.attest(self.b,self.c)
        self.assertEqual(self.result()['checks']['cryptographic_integrity']['status'],'FAIL')
    def test_source_bad_signature_is_actually_verified(self):
        row=self.b['SourceArtifacts'][0];row['Signature']=row['RetainedSignature']=fx.sign('source',b'other bytes')
        fx.refresh_sources(self.b,self.c)
        r=self.result();self.assertEqual(r['checks']['source_retention']['status'],'PASS')
        self.assertEqual(r['checks']['source_authentication']['status'],'FAIL');self.assertEqual(r['checks']['derivation_binding']['status'],'FAIL')
    def test_anchor_signature_is_actually_verified(self):
        self.b['Anchor']['Signature']=fx.sign('anchor-signature',b'wrong bytes');fx.attest(self.b,self.c)
        self.assertEqual(self.result()['checks']['cryptographic_integrity']['status'],'FAIL')
    def test_attestation_signature_is_actually_verified(self):
        self.b['MigrationAttestation']['Signature']=fx.sign('attestation',b'wrong bytes')
        self.assertEqual(self.result()['checks']['cryptographic_integrity']['status'],'FAIL')
    def test_plan_cannot_introduce_target_digest_cycle(self):
        self.b['DerivationPlan']['TargetArtifactDigest']='sha256:'+'0'*64
        self.assertEqual(self.result()['checks']['layout']['status'],'FAIL')
    def test_receipt_preservation_is_not_receipt_authentication(self):
        r=self.result();self.assertEqual(r['checks']['source_retention']['status'],'PASS')
        self.assertIn('external_time_and_receipts',r['always_unassessed'])
    def test_reading_original_signature_is_not_new_authority(self):
        self.c['Keys']['event-signature']=None
        r=self.result();self.assertEqual(r['checks']['source_authentication']['status'],'PASS')
        self.assertEqual(r['checks']['cryptographic_integrity']['status'],'UNASSESSED')
    def test_signed_zero_and_one_are_not_the_same(self):
        self.assertEqual(ck.decimal('-0'),ck.decimal('0'));self.assertNotEqual(ck.decimal('-0'),ck.decimal('1'))
        self.assertEqual(ck.decimal('01.00'),ck.decimal('1'));self.assertNotEqual(ck.jcs('01.00'),ck.jcs('1'))
    def test_known_offset_and_unknown_offset_are_different(self):
        self.assertEqual(ck.iso_ns('1970-01-01T09:00:00.0+09:00',True),0)
        with self.assertRaises(ck.Finding) as e:ck.iso_ns('1970-01-01T00:00:00.0-00:00',True)
        self.assertEqual(e.exception.status,'UNASSESSED')
    def test_output_schema_is_not_current_schema(self):
        self.b['Events'][0]['Commitment']['ContractID']='v1.2'
        self.assertEqual(self.result()['checks']['layout']['status'],'FAIL')
    def test_wrong_context_key_cannot_pass(self):
        self.c['Keys']['event-signature']['PublicKey']=self.c['Keys']['source']['PublicKey']
        self.assertEqual(self.result()['checks']['cryptographic_integrity']['status'],'FAIL')

if __name__=='__main__':unittest.main()
