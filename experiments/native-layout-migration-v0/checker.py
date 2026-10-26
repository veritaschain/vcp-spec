"""Read-only research subset checker; no current VCP format is accepted here."""
import argparse
import base64
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path

import rfc8785
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft202012Validator

from schema_builder import CONTRACT, SOURCE, POLICIES

HERE=Path(__file__).resolve().parent
MAX63=2**63-1
MAX31=2**31-1
EPOCH=datetime(1970,1,1,tzinfo=timezone.utc)
DOMAINS={k:('VCP RESEARCH native-layout-migration v0 '+k+'\x00').encode()
         for k in ('event','event-signature','anchor-signature','plan','attestation','source')}
AXES=('layout','source_retention','source_authentication','source_interpretation',
      'policy_binding','numeric_time','cryptographic_integrity','batch_binding',
      'inclusion_evidence','derivation_binding')
SCHEMA=json.loads((HERE/'candidate.schema.json').read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR=Draft202012Validator(SCHEMA)

class Finding(Exception):
    def __init__(self,status,message):
        super().__init__(message)
        self.status,self.message=status,message

def need(condition,message,status='FAIL'):
    if not condition: raise Finding(status,message)

INPUT_ERRORS=(ValueError,KeyError,TypeError,OverflowError,UnicodeError,RecursionError)

def findings(functions):
    found=[]
    for fn in functions:
        try:fn()
        except Finding as e:found.append(e)
        except INPUT_ERRORS as e:
            found.append(Finding('FAIL',type(e).__name__+': '+str(e)[:160]))
    return found

def finish(found):
    if found:raise Finding(aggregate([e.status for e in found]),'; '.join(e.message for e in found))

def collect(functions):finish(findings(functions))

def strict_json(raw):
    need(type(raw) is bytes and len(raw)<=8_000_000,'JSON input size/type')
    def pairs(items):
        out={}
        for k,v in items:
            need(k not in out,'duplicate JSON key: '+k)
            out[k]=v
        return out
    def bad(_): raise Finding('FAIL','non-JSON constant')
    return json.loads(raw.decode('utf8'),object_pairs_hook=pairs,parse_constant=bad)

def jcs(x): return rfc8785.dumps(x)
def digest(raw): return 'sha256:'+hashlib.sha256(raw).hexdigest()
def dh(role,x): return digest(DOMAINS[role]+jcs(x))
def same(a,b):
    if type(a) is not type(b): return False
    if type(a) is dict: return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if type(a) is list: return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return a==b

def hexbytes(s):
    need(type(s) is str and len(s)%2==0 and re.fullmatch('[0-9a-f]*',s) is not None,'noncanonical hex')
    return bytes.fromhex(s)

def sigbytes(s):
    raw=base64.b64decode(s,validate=True)
    need(len(raw)==64 and base64.b64encode(raw).decode()==s,'noncanonical signature')
    return raw

def uint(s,maximum=MAX63,minimum=0):
    need(type(s) is str and len(s)<=19 and re.fullmatch('0|[1-9][0-9]*',s) is not None,'unsigned decimal string grammar')
    v=int(s);need(minimum<=v<=maximum,'quantity outside candidate range');return v

def decimal(s,ratio=False):
    need(type(s) is str and len(s)<=40 and re.fullmatch(r'-?[0-9]+(?:\.[0-9]+)?',s) is not None,'decimal grammar')
    pieces=s.lstrip('-').split('.')
    need(len(pieces[0])<=20 and (len(pieces)==1 or len(pieces[1])<=18),'decimal capacity')
    n=Fraction(s);need(n>=0 and (not ratio or n<=1),'decimal quantity range');return n

def convert(value,source_unit,target_unit,maximum=MAX63):
    """Selected exact integer-destination rules; never infer a unit or round."""
    factors={('ms','s'):Fraction(1,1000),('s','ns'):Fraction(10**9),
             ('ms','ns'):Fraction(10**6),('us','ns'):Fraction(1000)}
    need((source_unit,target_unit) in factors,'unit conversion not selected','UNASSESSED')
    n=decimal(value) if source_unit=='us' else Fraction(uint(value))
    result=n*factors[source_unit,target_unit]
    need(result.denominator==1,'inexact integer-destination conversion','UNASSESSED')
    need(0<=result.numerator<=maximum,'conversion exceeds destination capacity','UNASSESSED')
    return str(result.numerator)

def iso_ns(s,source=False):
    pattern=(r'([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})'
             r'\.([0-9]{1,9})(Z|[+-][0-9]{2}:[0-9]{2})')
    m=re.fullmatch(pattern,s) if type(s) is str else None
    need(m is not None,'ISO syntax')
    y,mo,d,h,mi,se=map(int,m.groups()[:6]);frac,offset=m.group(7,8)
    need(se<=60,'ISO second range')
    if not source:need(len(frac)==9 and offset=='Z','candidate requires nine UTC fractional digits')
    # Validate the calendar and offset even when the second needs an unmapped
    # leap rule. Invalid dates/seconds must not masquerade as unsupported time.
    delta=datetime(y,mo,d,h,mi,min(se,59),tzinfo=timezone.utc)-EPOCH
    seconds=delta.days*86400+delta.seconds
    if offset!='Z':
        oh,om=int(offset[1:3]),int(offset[4:6]);need(oh<=23 and om<=59,'offset range')
        need(offset!='-00:00','unknown local offset','UNASSESSED')
        seconds-=(1 if offset[0]=='+' else -1)*(oh*3600+om*60)
    need(se<60,'leap mapping unavailable','UNASSESSED')
    return seconds*10**9+int(frac.ljust(9,'0'))

def ns_iso(v):
    need(type(v) is int and 0<=v<=MAX63,'TIME_NS range')
    seconds,nanos=divmod(v,10**9)
    return (EPOCH+timedelta(seconds=seconds)).strftime('%Y-%m-%dT%H:%M:%S')+f'.{nanos:09d}Z'

def leaf(h):
    need(type(h) is str and re.fullmatch('sha256:[0-9a-f]{64}',h) is not None,'digest encoding')
    return hashlib.sha256(b'\x00'+hexbytes(h[7:])).digest()

def tree(hashes):
    if not hashes:return hashlib.sha256(b'').digest()
    if len(hashes)==1:return leaf(hashes[0])
    k=1<<((len(hashes)-1).bit_length()-1)
    return hashlib.sha256(b'\x01'+tree(hashes[:k])+tree(hashes[k:])).digest()

def path(hashes,index):
    need(0<=index<len(hashes),'proof index')
    if len(hashes)==1:return []
    k=1<<((len(hashes)-1).bit_length()-1)
    if index<k:return path(hashes[:k],index)+['sha256:'+tree(hashes[k:]).hex()]
    return path(hashes[k:],index-k)+['sha256:'+tree(hashes[:k]).hex()]

def target_artifact(bundle):
    return {k:bundle[k] for k in ('Events','Anchor','InclusionEvidence')}

def binding(raw):
    policy=strict_json(raw)
    return {'PolicyID':policy['PolicyID'],'PolicyVersion':policy['PolicyVersion'],'PolicyDigest':digest(raw)}

def context_check(c):
    need(type(c) is dict and set(c)=={'ContractID','SourceManifestDigest','Keys','ActorID','ChainID','SourceActorID','SourceChainID','Policies'},'trust context fields')
    need(c['ContractID']==CONTRACT,'unsupported context','UNASSESSED')
    need(type(c['Keys']) is dict and set(c['Keys'])=={'source','event-signature','anchor-signature','attestation'},'key roles')
    need(type(c['Policies']) is dict and set(c['Policies'])=={'registration','numeric'},'policy roles')
    def identity(v):need(type(v) is str and 1<=len(v)<=128,'configured identity type/length')
    def pin(v):need(type(v) is str and re.fullmatch('sha256:[0-9a-f]{64}',v) is not None,'configured digest encoding')
    for name in ('ActorID','ChainID','SourceActorID','SourceChainID'):identity(c[name])
    if c['SourceManifestDigest'] is not None:pin(c['SourceManifestDigest'])
    for row in c['Keys'].values():
        if row is None:continue
        need(type(row) is dict and set(row)=={'KeyID','PublicKey'},'configured key fields')
        identity(row['KeyID']);need(len(hexbytes(row['PublicKey']))==32,'public key length')
    for row in c['Policies'].values():
        if row is None:continue
        need(type(row) is dict and set(row)=={'PolicyID','PolicyVersion','PolicyDigest'},'configured policy fields')
        identity(row['PolicyID']);need(row['PolicyVersion']=='0','unsupported configured policy version','UNASSESSED');pin(row['PolicyDigest'])
    jcs(c)

def verify_sig(role,message,signature,context,key_id=None):
    raw_signature=sigbytes(signature)
    row=context['Keys'][role]
    need(row is not None,'no configured '+role+' key','UNASSESSED')
    need(type(row) is dict and set(row)=={'KeyID','PublicKey'},'configured key fields')
    if key_id is not None:need(key_id==row['KeyID'],'key role/identity not selected','UNASSESSED')
    key=hexbytes(row['PublicKey']);need(len(key)==32,'public key length')
    try:Ed25519PublicKey.from_public_bytes(key).verify(raw_signature,DOMAINS[role]+message)
    except InvalidSignature:raise Finding('FAIL',role+' signature does not verify')

def source_rows(b):
    return [strict_json(hexbytes(e['OriginalHex'])) for e in b['SourceArtifacts']]

def source_assessment(s,c):
    """Evaluate independently mapped fields; an unknown is not an early success.

    A different format or extended shape stays wholly uninterpreted. Within the
    selected source shape, retain known values and findings separately so an
    unsupported time/conversion cannot suppress another field or row's failure.
    """
    allowed={'Format','EventID','ActorID','ChainID','SequenceNum','TimestampInt','TimestampISO','TimeBasis','Units','DurationMs','ToleranceMs','Confidence','LatencyUs'}
    need(type(s) is dict and set(s)==allowed,'unmapped source member/inner approval','UNASSESSED')
    need(s['Format']==SOURCE,'unknown source format','UNASSESSED')
    values={}
    def identity():
        need(type(s['EventID']) is str and bool(s['EventID']),'source event identity')
        values['EventID']=s['EventID']
    def sequence():
        need(type(s['SequenceNum']) is int and 0<=s['SequenceNum']<=MAX63,'source sequence type/range')
        values['SequenceNum']=str(s['SequenceNum'])
    units={'TimestampInt':'ns','DurationMs':'ms','ToleranceMs':'ms','Confidence':'ratio','LatencyUs':'us'}
    def unit(field):
        need(type(s['Units']) is dict and set(s['Units'])==set(units),'source unit fields not mapped','UNASSESSED')
        need(s['Units'][field]==units[field],'source '+field+' unit not mapped','UNASSESSED')
    def time():
        unit('TimestampInt')
        need(type(s['TimestampInt']) is int,'source integer value unavailable','UNASSESSED')
        need(s['TimeBasis']=='unix_no_leap','source time basis not mapped','UNASSESSED')
        need(iso_ns(s['TimestampISO'],source=True)==s['TimestampInt'],'source ISO/ns mismatch')
        need(0<=s['TimestampInt']<=MAX63,'source instant unsupported by target','UNASSESSED')
        values.update(TimestampInt=str(s['TimestampInt']),TimestampISO=ns_iso(s['TimestampInt']))
    def quantity(field,target,parse):
        unit(field);value=parse(s[field]);values[target]=value
    found=findings([
        lambda:need(s['ActorID']==c['SourceActorID'] and s['ChainID']==c['SourceChainID'],'source context mismatch'),
        identity,sequence,time,
        lambda:quantity('DurationMs','DurationSec',lambda v:convert(v,'ms','s')),
        lambda:quantity('ToleranceMs','ToleranceMs',lambda v:(uint(v,MAX31),v)[1]),
        lambda:quantity('Confidence','Confidence',lambda v:(decimal(v,True),v)[1]),
        lambda:quantity('LatencyUs','LatencyUs',lambda v:(decimal(v),v)[1])])
    return values,found

def interpret_source(s,c):
    values,found=source_assessment(s,c);finish(found);return values

def aggregate(statuses):
    return 'FAIL' if 'FAIL' in statuses else ('UNASSESSED' if 'UNASSESSED' in statuses else 'PASS')

def check(bundle,context):
    results={k:{'status':'UNASSESSED','detail':'not evaluated'} for k in AXES}
    def run(axis,fn):
        try:fn();results[axis]={'status':'PASS','detail':'covered checks passed'}
        except Finding as e:results[axis]={'status':e.status,'detail':e.message}
        except INPUT_ERRORS as e:
            results[axis]={'status':'FAIL','detail':type(e).__name__+': '+str(e)[:160]}
    def layout():
        context_check(context)
        errors=list(VALIDATOR.iter_errors(bundle))
        need(not errors, '; '.join('/'.join(map(str,e.absolute_path))+': '+e.message[:100] for e in errors[:3]))
        jcs(bundle)  # Reject non-Unicode/surrogate values before any preimage is computed.
    run('layout',layout)
    if results['layout']['status']=='PASS':
        b,c=bundle,context
        events=[e['Commitment'] for e in b['Events']]
        hashes=[dh('event',e) for e in events]
        plan=b['DerivationPlan']; pd=dh('plan',plan)
        def retention():
            actual=[]
            for e in b['SourceArtifacts']:
                raw=hexbytes(e['OriginalHex']);retained=hexbytes(e['RetainedHex'])
                need(raw==retained,'original bytes not retained')
                need(sigbytes(e['Signature'])==sigbytes(e['RetainedSignature']),'original signature not retained')
                actual.append({'EntryID':e['EntryID'],'RawSHA256':digest(raw),'SignatureSHA256':digest(sigbytes(e['Signature']))})
            need(len({e['EntryID'] for e in actual})==len(actual),'duplicate source entry')
            need(same(actual,b['SourceManifest']['Entries']),'source manifest/list mismatch')
            evidence=[]
            for e in b['PreservedEvidence']:
                raw=hexbytes(e['OriginalHex'])
                need(raw==hexbytes(e['RetainedHex']),'opaque original evidence not retained')
                evidence.append({'ArtifactID':e['ArtifactID'],'RawSHA256':digest(raw)})
            need(len({e['ArtifactID'] for e in evidence})==len(evidence),'duplicate evidence artifact')
            need(same(evidence,b['SourceManifest']['Evidence']),'original evidence inventory mismatch')
            need(c['SourceManifestDigest'] is not None,'received manifest not pinned','UNASSESSED')
            need(digest(jcs(b['SourceManifest']))==c['SourceManifestDigest'],'source differs from pinned received manifest')
        run('source_retention',retention)
        run('source_authentication',lambda:collect([lambda e=e:verify_sig('source',hexbytes(e['OriginalHex']),e['Signature'],c) for e in b['SourceArtifacts']]))
        source_values=[]
        def source_interpretation():
            found=[]
            for row in b['SourceArtifacts']:
                value={}
                def evaluate():
                    nonlocal value
                    value,problems=source_assessment(strict_json(hexbytes(row['OriginalHex'])),c)
                    found.extend(problems)
                found.extend(findings([evaluate]));source_values.append(value)
            ids=[v['EventID'] for v in source_values if 'EventID' in v]
            seq=[int(v['SequenceNum']) for v in source_values if 'SequenceNum' in v]
            found.extend(findings([
                lambda:need(len(set(ids))==len(ids),'duplicate original EventID'),
                lambda:need(all(a<z for a,z in zip(seq,seq[1:])),'original order/sequence mismatch')]))
            finish(found)
        run('source_interpretation',source_interpretation)
        def policies():
            def one(role,member):
                raw=hexbytes(b['Policies'][role]);v=strict_json(raw)
                need(type(v) is dict,'policy must be a JSON object')
                need(v.get('Role')==role,'policy role mismatch')
                value=binding(raw)
                for event in events:need(same(event[member],value),'event policy bytes not bound')
                need(same(plan[member],value) and same(b['Anchor']['Statement'][member],value),'plan/anchor policy binding')
                need(c['Policies'][role] is not None,'no configured policy','UNASSESSED')
                need(same(c['Policies'][role],value),'unselected policy','UNASSESSED')
                need(same(v,POLICIES[role]),'policy semantics not implemented','UNASSESSED')
            checks=[lambda role=role,member=member:one(role,member)
                    for role,member in [('registration','RegistrationPolicyBinding'),('numeric','NumericPolicyBinding')]]
            # Exact policy byte digest selection, not incoming policy fields, fixes rules.
            def identity(event):
                need(event['Header']['PolicyID']==event['RegistrationPolicyBinding']['PolicyID'],'Header registration identity')
                ident=event['PolicyIdentification']
                if ident is not None:need(ident['PolicyID']==event['Header']['PolicyID'] and ident['Version']=='0','PolicyIdentification binding')
            collect(checks+[lambda e=e:identity(e) for e in events])
        run('policy_binding',policies)
        def numeric():
            def one(e):
                h=e['Header'];p=e['Payload']
                collect([
                    lambda:need(iso_ns(h['TimestampISO'])==uint(h['TimestampInt']),'target ISO/ns mismatch'),
                    lambda:uint(h['TimestampInt']),lambda:uint(h['SequenceNum']),
                    lambda:uint(p['VCP-ANCHOR']['FailoverDetails']['TriggerCondition']['TotalDowntimeSec']),
                    lambda:uint(p['VCP-XREF']['SharedEventKey']['ToleranceMs'],MAX31),
                    lambda:decimal(p['VCP-GOV']['ConfidenceScore'],True),
                    lambda:decimal(p['VCP-GOV']['PerformanceMetadata']['LatencyImpact'])])
            collect([lambda e=e:one(e) for e in events]+[
                lambda:uint(b['Anchor']['Statement']['RecordedAtNs']),
                lambda:uint(b['MigrationAttestation']['Statement']['CreatedAtNs'])])
        run('numeric_time',numeric)
        def crypto():
            checks=[]
            for env,h in zip(b['Events'],hashes):
                def one(env=env,h=h):
                    s=env['Statement'];hdr=env['Commitment']['Header']
                    need(s['EventHash']==h,'event hash mismatch')
                    need(all(s[k]==hdr[k] for k in ('EventID','ActorID','ChainID')),'event statement identity binding')
                    collect([
                        lambda:need(hdr['ActorID']==c['ActorID'] and hdr['ChainID']==c['ChainID'],'unselected actor/chain','UNASSESSED'),
                        lambda:verify_sig('event-signature',jcs(s),env['Signature'],c,s['KeyID'])])
                checks.append(one)
            for role,name in [('anchor-signature','Anchor'),('attestation','MigrationAttestation')]:
                checks.append(lambda role=role,name=name:verify_sig(role,jcs(b[name]['Statement']),b[name]['Signature'],c,b[name]['Statement']['KeyID']))
            collect(checks)
        run('cryptographic_integrity',crypto)
        def batch():
            a=b['Anchor']['Statement'];hs=[e['Header'] for e in events]
            need(uint(a['EventCount'],MAX31,1)==len(events),'complete batch count mismatch')
            need(len({h['EventID'] for h in hs})==len(hs),'duplicate target EventID')
            need(a['FirstEventID']==hs[0]['EventID'] and a['LastEventID']==hs[-1]['EventID'],'batch endpoints')
            need(a['MerkleRoot']=='sha256:'+tree(hashes).hex(),'ordered root mismatch')
            for i,e in enumerate(events):
                need(e['Header']['ActorID']==a['ActorID'] and e['Header']['ChainID']==a['ChainID'],'mixed actor/chain')
                need(e['ChainMode']==('start' if i==0 else 'linked'),'chain mode')
                need(e['PreviousEventHash']==(None if i==0 else hashes[i-1]),'chain predecessor')
                need(same(e['RegistrationPolicyBinding'],a['RegistrationPolicyBinding']) and same(e['NumericPolicyBinding'],a['NumericPolicyBinding']),'mixed policies')
            need(all(uint(x['SequenceNum'])<uint(z['SequenceNum']) for x,z in zip(hs,hs[1:])),'target sequence order')
        run('batch_binding',batch)
        def proofs():
            need(len(b['InclusionEvidence'])==len(events),'proof inventory')
            for i,(proof,event) in enumerate(zip(b['InclusionEvidence'],events)):
                need(uint(proof['LeafIndex'],MAX31-1)==i and i<uint(b['Anchor']['Statement']['EventCount'],MAX31,1),'proof index/count')
                need(proof['EventID']==event['Header']['EventID'],'proof event identity')
                need(same(proof['Path'],path(hashes,i)),'proof path mismatch')
        run('inclusion_evidence',proofs)
        def derivation():
            need(plan['SourceManifestDigest']==digest(jcs(b['SourceManifest'])),'plan source-manifest binding')
            need(plan['TargetActorID']==c['ActorID'] and plan['TargetChainID']==c['ChainID'],'plan target context')
            need(c['ChainID']!=c['SourceChainID'],'target chain must be distinct')
            source_ids=[e['EntryID'] for e in b['SourceArtifacts']]
            target_ids=[e['Header']['EventID'] for e in events]
            expected_entries=[{'SourceEntryID':s,'TargetEventID':t} for s,t in zip(source_ids,target_ids)]
            need(len(source_ids)==len(events) and same(plan['Entries'],expected_entries),'one-to-one source/target inventory/order')
            for e,entry in zip(events,plan['Entries']):
                need(same(e['Origin'],{'Kind':'derived','DerivationPlanDigest':pd,'SourceEntryID':entry['SourceEntryID']}),'protected origin/plan link')
            att=b['MigrationAttestation']['Statement']
            need(att['DerivationPlanDigest']==pd and att['SourceManifestDigest']==plan['SourceManifestDigest'],'attestation source/plan')
            need(att['TargetArtifactDigest']==digest(jcs(target_artifact(b))),'attestation full target-artifact binding')
            # All prerequisites remain required for PASS. A missing pin/key or
            # unmapped field must not hide a known mismatch in supplied evidence.
            checks=[lambda axis=axis:need(results[axis]['status']=='PASS',axis+' prerequisite',results[axis]['status'])
                    for axis in ('source_retention','source_authentication','source_interpretation')]
            ids={v['EventID'] for v in source_values if 'EventID' in v}
            checks.append(lambda:need(not set(target_ids)&ids,'new IDs must not reuse any source EventID'))
            for v,e in zip(source_values,events):
                h=e['Header'];p=e['Payload']
                target={k:h[k] for k in ('TimestampInt','TimestampISO','SequenceNum')}
                target.update(DurationSec=p['VCP-ANCHOR']['FailoverDetails']['TriggerCondition']['TotalDowntimeSec'],
                    ToleranceMs=p['VCP-XREF']['SharedEventKey']['ToleranceMs'],
                    Confidence=p['VCP-GOV']['ConfidenceScore'],LatencyUs=p['VCP-GOV']['PerformanceMetadata']['LatencyImpact'])
                checks.extend(lambda k=k,v=v,target=target:need(target[k]==v[k],'derived '+k+' value/lexeme mismatch')
                              for k in target if k in v)
            collect(checks)
        run('derivation_binding',derivation)
    return {'status':'UNADOPTED','independent_reproduction':'not_established','native_conformance':'UNASSESSED',
      'covered_checks':aggregate([v['status'] for v in results.values()]),'checks':results,
      'always_unassessed':['complete_native_schema','production_authority','external_time_and_receipts',
                          'inner_approvals','other_time_bases','independence']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle',type=Path);parser.add_argument('--context',type=Path,required=True)
    args=parser.parse_args()
    try:out=check(strict_json(args.bundle.read_bytes()),strict_json(args.context.read_bytes()))
    except (Finding,ValueError,TypeError,UnicodeError,RecursionError,OSError) as e:
        out={'status':'UNADOPTED','covered_checks':'FAIL','error':str(e),'native_conformance':'UNASSESSED','independent_reproduction':'not_established'}
    print(json.dumps(out,indent=2));return 0 if out['covered_checks']=='PASS' else (2 if out['covered_checks']=='UNASSESSED' else 1)

if __name__=='__main__':raise SystemExit(main())
