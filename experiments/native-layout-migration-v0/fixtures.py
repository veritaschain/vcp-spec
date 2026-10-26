"""Deterministic PUBLIC TEST KEYS and synthetic input construction only.

The checker never imports this module and never receives private seeds.
Expected outcomes below are authored assertions, not checker output.
"""
import base64
import copy
import hashlib
import json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import checker as ck
from schema_builder import CONTRACT, SOURCE, POLICIES

HERE=Path(__file__).resolve().parent
ROLES=('source','event-signature','anchor-signature','attestation')
# PUBLIC SYNTHETIC MATERIAL. No organizational or production identity.
SEEDS={r:hashlib.sha256(('PUBLIC TEST KEY native-layout-migration-v0 '+r).encode()).digest() for r in ROLES}
KEYS={r:Ed25519PrivateKey.from_private_bytes(s) for r,s in SEEDS.items()}

def rawjson(value):return (json.dumps(value,ensure_ascii=True,indent=2,allow_nan=False)+'\n').encode()
def sign(role,raw):return base64.b64encode(KEYS[role].sign(ck.DOMAINS[role]+raw)).decode()
def expectation(**changes):return {k:changes.get(k,'PASS') for k in ck.AXES}
def layout_failure():return {k:'FAIL' if k=='layout' else 'UNASSESSED' for k in ck.AXES}

def attest(b,c):
    s={'ContractID':CONTRACT,'SignatureAlgorithm':'Ed25519','KeyID':c['Keys']['attestation']['KeyID'],
       'DerivationPlanDigest':ck.dh('plan',b['DerivationPlan']),
       'SourceManifestDigest':b['DerivationPlan']['SourceManifestDigest'],
       'TargetArtifactDigest':ck.digest(ck.jcs(ck.target_artifact(b))),
       'CreatedAtNs':'1792886401000000000',
       'Support':'synthetic internal execution; no external evaluator',
       'ConversionRule':'research-exact-ms-to-s-preserve-decimals-v0'}
    b['MigrationAttestation']={'Statement':s,'Signature':sign('attestation',ck.jcs(s))}

def seal(b,c,rechain=True):
    hashes=[]
    for i,env in enumerate(b['Events']):
        e=env['Commitment'];h=e['Header']
        if rechain:
            e['ChainMode']='start' if i==0 else 'linked';e['PreviousEventHash']=None if i==0 else hashes[-1]
        eh=ck.dh('event',e);hashes.append(eh)
        s={'ContractID':CONTRACT,'SignatureAlgorithm':'Ed25519','KeyID':c['Keys']['event-signature']['KeyID'],
           'EventHash':eh,**{k:h[k] for k in ('EventID','ActorID','ChainID')}}
        env['Statement']=s;env['Signature']=sign('event-signature',ck.jcs(s))
    es=[e['Commitment'] for e in b['Events']];first=es[0]
    a={'ContractID':CONTRACT,'SignatureAlgorithm':'Ed25519','KeyID':c['Keys']['anchor-signature']['KeyID'],
       'ActorID':first['Header']['ActorID'],'ChainID':first['Header']['ChainID'],
       'RegistrationPolicyBinding':first['RegistrationPolicyBinding'],'NumericPolicyBinding':first['NumericPolicyBinding'],
       'TreeScheme':'research-rfc6962-digest-leaf-v0','EventCount':str(len(es)),
       'FirstEventID':first['Header']['EventID'],'LastEventID':es[-1]['Header']['EventID'],
       'MerkleRoot':'sha256:'+ck.tree(hashes).hex(),'RecordedAtNs':'1792886400000000000','IntendedTarget':'synthetic-unconnected'}
    b['Anchor']={'Statement':a,'Signature':sign('anchor-signature',ck.jcs(a))}
    b['InclusionEvidence']=[{'EventID':e['Header']['EventID'],'LeafIndex':str(i),'Path':ck.path(hashes,i)} for i,e in enumerate(es)]
    attest(b,c)

def link_plan(b):
    pd=ck.dh('plan',b['DerivationPlan'])
    for e,entry in zip(b['Events'],b['DerivationPlan']['Entries']):
        e['Commitment']['Origin']={'Kind':'derived','DerivationPlanDigest':pd,'SourceEntryID':entry['SourceEntryID']}

def refresh_sources(b,c):
    b['SourceManifest']={'SourceFormat':SOURCE,
      'Entries':[{'EntryID':s['EntryID'],'RawSHA256':ck.digest(bytes.fromhex(s['OriginalHex'])),
                  'SignatureSHA256':ck.digest(base64.b64decode(s['Signature']))} for s in b['SourceArtifacts']],
      'Evidence':[{'ArtifactID':e['ArtifactID'],'RawSHA256':ck.digest(bytes.fromhex(e['OriginalHex']))} for e in b['PreservedEvidence']]}
    c['SourceManifestDigest']=ck.digest(ck.jcs(b['SourceManifest']))
    b['DerivationPlan']['SourceManifestDigest']=c['SourceManifestDigest'];link_plan(b);seal(b,c)

def source_change(b,c,fn):
    row=b['SourceArtifacts'][0];s=ck.strict_json(bytes.fromhex(row['OriginalHex']));fn(s)
    raw=rawjson(s);row['OriginalHex']=row['RetainedHex']=raw.hex()
    row['Signature']=row['RetainedSignature']=sign('source',raw)
    refresh_sources(b,c)

def base():
    c={'ContractID':CONTRACT,'SourceManifestDigest':None,
       'Keys':{r:{'KeyID':'urn:vcp-research:key:layout:'+r,'PublicKey':k.public_key().public_bytes_raw().hex()} for r,k in KEYS.items()},
       'ActorID':'urn:vcp-research:converter','ChainID':'urn:vcp-research:derived-chain',
       'SourceActorID':'urn:vcp-research:source-actor','SourceChainID':'urn:vcp-research:source-chain',
       'Policies':{r:ck.binding(rawjson(p)) for r,p in POLICIES.items()}}
    b={'ContractID':CONTRACT,'Policies':{r:rawjson(p).hex() for r,p in POLICIES.items()},'SourceArtifacts':[],
       'PreservedEvidence':[], 'Events':[]}
    for aid,raw in [('old-proof',b'SYNTHETIC ORIGINAL ROOT/PROOF BYTES\r\n00ff'),
                    ('old-receipt',b'SYNTHETIC UNCONNECTED RECEIPT; NOT AN EXTERNAL TIME ATTESTATION\n')]:
        b['PreservedEvidence'].append({'ArtifactID':aid,'OriginalHex':raw.hex(),'RetainedHex':raw.hex()})
    for i in range(3):
        ns=1792886400000000000+i
        source={'Format':SOURCE,'EventID':'urn:vcp-research:source-event:'+str(i),
          'ActorID':c['SourceActorID'],'ChainID':c['SourceChainID'],'SequenceNum':i,
          'TimestampInt':ns,'TimestampISO':ck.ns_iso(ns),'TimeBasis':'unix_no_leap',
          'Units':{'TimestampInt':'ns','DurationMs':'ms','ToleranceMs':'ms','Confidence':'ratio','LatencyUs':'us'},
          'DurationMs':'1000','ToleranceMs':'10','Confidence':['01.00','-0','0.75'][i],'LatencyUs':'0.001'}
        raw=rawjson(source);entry='source-'+str(i)
        b['SourceArtifacts'].append({'EntryID':entry,'OriginalHex':raw.hex(),'RetainedHex':raw.hex(),
            'Signature':sign('source',raw),'RetainedSignature':sign('source',raw)})
        h={'EventID':'urn:vcp-research:target-event:'+str(i),'ActorID':c['ActorID'],'ChainID':c['ChainID'],
           'SequenceNum':str(i),'EventType':'RESEARCH_LAYOUT_ONLY','PolicyID':c['Policies']['registration']['PolicyID'],
           'TimestampInt':str(ns),'TimestampISO':ck.ns_iso(ns)}
        e={'ContractID':CONTRACT,'EventHashAlgorithm':'SHA-256','Header':h,
           'Payload':{'VCP-ANCHOR':{'FailoverDetails':{'TriggerCondition':{'TotalDowntimeSec':'1'}}},
                      'VCP-XREF':{'SharedEventKey':{'ToleranceMs':'10'}},
                      'VCP-GOV':{'ConfidenceScore':source['Confidence'],'PerformanceMetadata':{'LatencyImpact':'0.001'}}},
           'PolicyIdentification':{'PolicyID':h['PolicyID'],'Version':'0'},
           'RegistrationPolicyBinding':copy.deepcopy(c['Policies']['registration']),
           'NumericPolicyBinding':copy.deepcopy(c['Policies']['numeric']),
           'Origin':{},'ChainMode':'start','PreviousEventHash':None}
        b['Events'].append({'Commitment':e})
    b['DerivationPlan']={'ContractID':CONTRACT,'PlanID':'urn:vcp-research:plan:three-events',
       'SourceManifestDigest':'','SourceFormat':SOURCE,'TargetActorID':c['ActorID'],'TargetChainID':c['ChainID'],
       'RegistrationPolicyBinding':copy.deepcopy(c['Policies']['registration']),
       'NumericPolicyBinding':copy.deepcopy(c['Policies']['numeric']),
       'ConversionRule':'research-exact-ms-to-s-preserve-decimals-v0',
       'Entries':[{'SourceEntryID':'source-'+str(i),'TargetEventID':'urn:vcp-research:target-event:'+str(i)} for i in range(3)]}
    refresh_sources(b,c);return b,c

def vectors():
    cases=[]
    def add(name,fn=None,expected=None,reason=''):
        b,c=base()
        if fn:fn(b,c)
        cases.append({'id':name,'reason':reason,'bundle':b,'context':c,'expected':expected or expectation()})
    add('three-event-exact-migration',reason='Different policy roles, three ordered events, exact ms-to-s and preserved decimal lexemes.')
    def target_change(fn):
        def f(b,c):fn(b['Events'][0]['Commitment']);seal(b,c)
        return f
    def src(fn):return lambda b,c:source_change(b,c,fn)
    def fractional_latency(b,c):
        b['Events'][0]['Commitment']['Payload']['VCP-GOV']['PerformanceMetadata']['LatencyImpact']='0.0001'
        source_change(b,c,lambda s:s.update(LatencyUs='0.0001'))
    add('fractional-ns-latency-remains-us',fractional_latency,
        reason='Preserving decimal microseconds is valid here even when a separate integer-ns conversion is unsupported.')
    add('source-ratio-is-not-percent',src(lambda s:s.update(Confidence='75')),
        expectation(source_interpretation='FAIL',derivation_binding='FAIL'),
        reason='75 labeled ratio is invalid under the identified source rule; it is not divided by 100.')
    add('source-offset-equivalence',src(lambda s:s.update(TimestampISO='2026-10-25T09:00:00.000000000+09:00')),
        reason='Known source offset changes spelling, not the instant; original bytes remain retained.')
    def boundary(value):
        def f(b,c):
            for i,row in enumerate(b['SourceArtifacts']):
                s=ck.strict_json(bytes.fromhex(row['OriginalHex']));ns=value
                s.update(TimestampInt=ns,TimestampISO=ck.ns_iso(ns))
                raw=rawjson(s);row.update(OriginalHex=raw.hex(),RetainedHex=raw.hex(),Signature=sign('source',raw),RetainedSignature=sign('source',raw))
                b['Events'][i]['Commitment']['Header'].update(TimestampInt=str(ns),TimestampISO=ck.ns_iso(ns))
            refresh_sources(b,c)
        return f
    add('epoch-zero',boundary(0));add('maximum-time-ns',boundary(ck.MAX63))
    def null_policy(b,c):
        for env in b['Events']:env['Commitment']['PolicyIdentification']=None
        seal(b,c)
    add('explicit-null-policy-identification',null_policy,reason='This selected subset allows null; both separate policy bindings remain mandatory.')
    for name,fn in [
        ('iso-in-payload',lambda e:e['Payload'].update(TimestampISO=e['Header'].pop('TimestampISO'))),
        ('missing-header-iso',lambda e:e['Header'].pop('TimestampISO')),
        ('json-number-timestamp',lambda e:e['Header'].update(TimestampInt=1)),
        ('boolean-sequence',lambda e:e['Header'].update(SequenceNum=True)),
        ('unknown-clock-member',lambda e:e['Header'].update(ClockStatus='SYNCED')),
        ('unknown-module',lambda e:e['Payload'].update(**{'VCP-UNKNOWN':{}})),
        ('stripped-origin',lambda e:e.pop('Origin')),
        ('capture-relabel',lambda e:e['Origin'].update(Kind='capture')),
        ('fake-validation-flag',lambda e:e.update(signature_valid=True)),
    ]:
        add(name,lambda b,c,fn=fn:fn(b['Events'][0]['Commitment']),layout_failure(),reason='Closed research shape rejects this input; not a statement that every such native extension is invalid.')
    add('target-wrong-year-resigned',target_change(lambda e:e['Header'].update(TimestampISO='2025-10-25T00:00:00.000000000Z')),
        expectation(numeric_time='FAIL',derivation_binding='FAIL'))
    add('target-ns-overflow-resigned',target_change(lambda e:e['Header'].update(TimestampInt=str(ck.MAX63+1))),
        expectation(numeric_time='FAIL',derivation_binding='FAIL'))
    add('target-confidence-out-of-range',target_change(lambda e:e['Payload']['VCP-GOV'].update(ConfidenceScore='1.01')),
        expectation(numeric_time='FAIL',derivation_binding='FAIL'))
    add('decimal-lexeme-normalized-resigned',target_change(lambda e:e['Payload']['VCP-GOV'].update(ConfidenceScore='1')),
        expectation(derivation_binding='FAIL'))
    add('duration-relabelled-resigned',target_change(lambda e:e['Payload']['VCP-ANCHOR']['FailoverDetails']['TriggerCondition'].update(TotalDowntimeSec='1000')),
        expectation(derivation_binding='FAIL'))
    add('milliseconds-silently-converted-resigned',target_change(lambda e:e['Payload']['VCP-XREF']['SharedEventKey'].update(ToleranceMs='10000000')),
        expectation(derivation_binding='FAIL'))
    add('microsecond-lexeme-normalized',target_change(lambda e:e['Payload']['VCP-GOV']['PerformanceMetadata'].update(LatencyImpact='0.0010')),
        expectation(derivation_binding='FAIL'))
    add('source-wrong-year',src(lambda s:s.update(TimestampISO='2025-10-25T00:00:00.000000000Z')),
        expectation(source_interpretation='FAIL',derivation_binding='FAIL'))
    for name,fn in [
      ('source-inexact-ms-to-seconds',lambda s:s.update(DurationMs='1001')),
      ('source-unit-unknown',lambda s:s['Units'].update(DurationMs='unknown')),
      ('source-smear-unmapped',lambda s:s.update(TimeBasis='smear-unspecified')),
      ('source-leap-unmapped',lambda s:s.update(TimestampISO='2016-12-31T23:59:60.000000000Z')),
      ('source-rounded-float',lambda s:s.update(TimestampInt=1792886400000000000.0)),
      ('source-inner-approval-unmapped',lambda s:s.update(Approval={'Signature':'opaque original approval'})),
      ('source-negative-epoch',lambda s:s.update(TimestampInt=-1,TimestampISO='1969-12-31T23:59:59.999999999Z')),
      ('source-above-target-range',lambda s:s.update(TimestampInt=ck.MAX63+1,TimestampISO='2262-04-11T23:47:16.854775808Z')),
      ('source-unknown-format',lambda s:s.update(Format='unidentified')),
    ]:
        add(name,src(fn),expectation(source_interpretation='UNASSESSED',derivation_binding='UNASSESSED'))
    add('retained-source-byte-changed',lambda b,c:b['SourceArtifacts'][0].update(RetainedHex='00'),
        expectation(source_retention='FAIL',derivation_binding='FAIL'))
    add('retained-source-signature-changed',lambda b,c:b['SourceArtifacts'][0].update(RetainedSignature=base64.b64encode(bytes(64)).decode()),
        expectation(source_retention='FAIL',derivation_binding='FAIL'))
    add('retained-receipt-changed',lambda b,c:b['PreservedEvidence'][1].update(RetainedHex='00'),
        expectation(source_retention='FAIL',derivation_binding='FAIL'))
    add('old-proof-omitted',lambda b,c:b['PreservedEvidence'].pop(0),
        expectation(source_retention='FAIL',derivation_binding='FAIL'))
    add('missing-received-manifest-pin',lambda b,c:c.update(SourceManifestDigest=None),
        expectation(source_retention='UNASSESSED',derivation_binding='UNASSESSED'))
    def coherent_source_replacement(b,c):
        old=c['SourceManifestDigest'];source_change(b,c,lambda s:s.update(DurationMs='2000'));c['SourceManifestDigest']=old
    add('coherent-source-replacement',coherent_source_replacement,expectation(source_retention='FAIL',derivation_binding='FAIL'),
        reason='Even re-signed replacement plus new manifest must not match the independently retained receipt pin.')
    def wrong_origin(b,c):
        b['Events'][0]['Commitment']['Origin']['SourceEntryID']='source-1';seal(b,c)
    add('origin-source-entry-swapped',wrong_origin,expectation(derivation_binding='FAIL'))
    def reuse_id(b,c):
        tid='urn:vcp-research:source-event:0';b['Events'][0]['Commitment']['Header']['EventID']=tid
        b['DerivationPlan']['Entries'][0]['TargetEventID']=tid;link_plan(b);seal(b,c)
    add('original-event-id-reused',reuse_id,expectation(derivation_binding='FAIL'))
    def changed_plan(b,c):b['DerivationPlan']['PlanID']='changed-without-origin-update';attest(b,c)
    add('plan-changed-origin-stale',changed_plan,expectation(derivation_binding='FAIL'))
    def swapped_events(b,c):
        b['Events'][0],b['Events'][1]=b['Events'][1],b['Events'][0];seal(b,c)
    add('source-order-changed',swapped_events,expectation(batch_binding='FAIL',derivation_binding='FAIL'))
    def stale_chain(b,c):
        b['Events'][1]['Commitment']['PreviousEventHash']='sha256:'+'0'*64;seal(b,c,rechain=False)
    add('middle-event-wrong-predecessor',stale_chain,expectation(batch_binding='FAIL'))
    def drop_target(b,c):b['Events'].pop();attest(b,c)
    add('partial-target-presented-as-complete',drop_target,expectation(batch_binding='FAIL',inclusion_evidence='FAIL',derivation_binding='FAIL'))
    def bad_proof(b,c):b['InclusionEvidence'][2]['LeafIndex']='3';attest(b,c)
    add('proof-index-equals-count',bad_proof,expectation(inclusion_evidence='FAIL'))
    def bad_path(b,c):b['InclusionEvidence'][0]['Path'].append('sha256:'+'0'*64);attest(b,c)
    add('extra-proof-node',bad_path,expectation(inclusion_evidence='FAIL'))
    def sigbad(b,c):b['Events'][0]['Signature']=base64.b64encode(bytes(64)).decode();attest(b,c)
    add('bad-event-signature',sigbad,expectation(cryptographic_integrity='FAIL'))
    def attbad(b,c):
        b['MigrationAttestation']['Statement']['TargetArtifactDigest']='sha256:'+'0'*64
        b['MigrationAttestation']['Signature']=sign('attestation',ck.jcs(b['MigrationAttestation']['Statement']))
    add('resigned-false-target-manifest',attbad,expectation(derivation_binding='FAIL'))
    add('missing-event-key',lambda b,c:c['Keys'].update({'event-signature':None}),expectation(cryptographic_integrity='UNASSESSED'))
    add('missing-source-key',lambda b,c:c['Keys'].update(source=None),expectation(source_authentication='UNASSESSED',derivation_binding='UNASSESSED'))
    def fail_unknown(b,c):c['Keys']['event-signature']=None;b['SourceArtifacts'][0]['RetainedHex']='00'
    add('failure-precedes-unassessed',fail_unknown,expectation(cryptographic_integrity='UNASSESSED',source_retention='FAIL',derivation_binding='FAIL'))
    add('unbound-policy-newline',lambda b,c:b['Policies'].update(numeric=(bytes.fromhex(b['Policies']['numeric'])+b'\n').hex()),expectation(policy_binding='FAIL'))
    def unsupported_policy(b,c):
        p=copy.deepcopy(POLICIES['numeric']);p['TimeBasis']='TAI'
        raw=rawjson(p);b['Policies']['numeric']=raw.hex();bind=ck.binding(raw);c['Policies']['numeric']=bind
        b['DerivationPlan']['NumericPolicyBinding']=bind
        for env in b['Events']:env['Commitment']['NumericPolicyBinding']=bind
        link_plan(b);seal(b,c)
    add('configured-but-unimplemented-policy',unsupported_policy,expectation(policy_binding='UNASSESSED'),reason='Allowlisting an incoming digest cannot add interpretation support.')
    add('registration-header-id-mismatch',target_change(lambda e:e['Header'].update(PolicyID=e['NumericPolicyBinding']['PolicyID'])),expectation(policy_binding='FAIL'))
    # Final-review counterexamples: authored assertions, not inferred outcomes.
    add('policy-array',lambda b,c:b['Policies'].update(numeric=rawjson([]).hex()),expectation(policy_binding='FAIL'),
        reason='A non-object policy must produce a finding, not an uncaught AttributeError.')
    add('source-second-99',src(lambda s:s.update(TimestampISO='2026-10-25T00:00:99.000000000Z')),
        expectation(source_interpretation='FAIL',derivation_binding='FAIL'),reason='Invalid seconds are not an unmapped leap second.')
    add('inexact-duration-hides-invalid-ratio',src(lambda s:s.update(DurationMs='1001',Confidence='75')),
        expectation(source_interpretation='FAIL',derivation_binding='FAIL'),reason='An unknown conversion must not suppress a known invalid ratio.')
    def unknown_other_mismatch(b,c):
        source_change(b,c,lambda s:s.update(TimeBasis='smear-unspecified'))
        b['Events'][1]['Commitment']['Payload']['VCP-XREF']['SharedEventKey']['ToleranceMs']='11';seal(b,c)
    add('unknown-source-hides-other-derived-mismatch',unknown_other_mismatch,
        expectation(source_interpretation='UNASSESSED',derivation_binding='FAIL'),reason='A supported row still proves a mismatch when another row is partly unassessed.')
    def unknown_same_mismatch(b,c):
        source_change(b,c,lambda s:s.update(TimeBasis='smear-unspecified'))
        e=b['Events'][0]['Commitment'];e['Header']['TimestampISO']='2016-12-31T23:59:60.000000000Z'
        e['Payload']['VCP-GOV']['ConfidenceScore']='75';seal(b,c)
    add('unknown-time-hides-same-event-invalid-ratio',unknown_same_mismatch,
        expectation(source_interpretation='UNASSESSED',numeric_time='FAIL',derivation_binding='FAIL'),
        reason='Known numeric failure and mismatch survive an unsupported time in the same event.')
    def null_actor(b,c):
        c['SourceActorID']=None
        for row in b['SourceArtifacts']:
            s=ck.strict_json(bytes.fromhex(row['OriginalHex']));s['ActorID']=None;raw=rawjson(s)
            row.update(OriginalHex=raw.hex(),RetainedHex=raw.hex(),Signature=sign('source',raw),RetainedSignature=sign('source',raw))
        refresh_sources(b,c)
    add('null-source-actor-context',null_actor,layout_failure(),reason='Matching null identities are malformed configuration, not a selected source actor.')
    def malformed_signature(b,c):
        b['Events'][0]['Signature']='!'*88;c['Keys']['event-signature']=None;attest(b,c)
    add('missing-key-malformed-signature',malformed_signature,expectation(cryptographic_integrity='FAIL'),
        reason='Missing authority does not make a known malformed signature encoding unassessed.')
    return cases

UNIT_CASES=[
 ('ms-to-s-exact','1000','ms','s','PASS','1'),
 ('ms-to-s-inexact','1001','ms','s','UNASSESSED',None),
 ('one-second-ns','1','s','ns','PASS','1000000000'),
 ('zero-seconds','0','s','ns','PASS','0'),
 ('seconds-destination-overflow',str(ck.MAX63),'s','ns','UNASSESSED',None),
 ('millisecond-max31',str(ck.MAX31),'ms','ns','PASS','2147483647000000'),
 ('microsecond-fraction-exact','0.001','us','ns','PASS','1'),
 ('microsecond-fraction-inexact','0.0001','us','ns','UNASSESSED',None),
 ('negative-duration','-1','ms','s','FAIL',None),
 ('boolean-duration',True,'ms','s','FAIL',None),
 ('unknown-unit','1000','unknown','s','UNASSESSED',None),
 ('percent-not-automatic','75','percent','ratio','UNASSESSED',None),
 ('integer-leading-zero','01000','ms','s','FAIL',None),
 ('duration-newline','1000\n','ms','s','FAIL',None),
]

def document():
    return {'status':'UNADOPTED','independent_reproduction':'not_established',
       'cases':vectors(),'unit_cases':[dict(zip(('id','value','source_unit','target_unit','expected_status','expected_value'),r)) for r in UNIT_CASES]}

if __name__=='__main__':
    path=HERE/'data/cases.json'
    path.write_bytes(rawjson(document()))
    b,c=base();(HERE/'data/example-bundle.json').write_bytes(rawjson(b));(HERE/'data/example-context.json').write_bytes(rawjson(c))
    print('Generated deterministic synthetic inputs; expectations are authored explicitly.')
