"""Closed SYNTHETIC subset, not a VCP native schema or an adopted allocation."""
import json
from pathlib import Path

CONTRACT = 'urn:vcp-research:native-layout-migration:2026-10-25:v0'
SOURCE = 'urn:vcp-research:raw-source:2026-10-25:v0'
POLICIES = {
 'registration': {'Role':'registration','PolicyID':'urn:vcp-research:registration:layout-v0',
   'PolicyVersion':'0','ContractID':CONTRACT,'Authority':'PUBLIC TEST KEYS ONLY'},
 'numeric': {'Role':'numeric','PolicyID':'urn:vcp-research:numeric:layout-v0',
   'PolicyVersion':'0','ContractID':CONTRACT,'TimeBasis':'unix_no_leap',
   'Fields':{'Header.TimestampInt':'ns','Header.SequenceNum':'ordinal',
     'Payload.VCP-ANCHOR.FailoverDetails.TriggerCondition.TotalDowntimeSec':'s',
     'Payload.VCP-XREF.SharedEventKey.ToleranceMs':'ms','Payload.VCP-GOV.ConfidenceScore':'ratio',
     'Payload.VCP-GOV.PerformanceMetadata.LatencyImpact':'us'},
   'DecimalEmission':'preserve accepted source lexeme','Rounding':'forbidden'}
}

def obj(properties, optional=()):
    return {'type':'object','additionalProperties':False,'properties':properties,
            'required':[k for k in properties if k not in optional]}

def arr(items, minimum=1, maximum=16):
    return {'type':'array','items':items,'minItems':minimum,'maxItems':maximum}

def ref(name): return {'$ref':'#/$defs/'+name}
def const(value): return {'const':value}
def string(maximum=128): return {'type':'string','minLength':1,'maxLength':maximum}

def build():
    d={
      'id':string(),
      'uint':{'type':'string','pattern':'^(0|[1-9][0-9]*)$','maxLength':19},
      'decimal':{'type':'string','pattern':'^-?[0-9]+(\\.[0-9]+)?$','maxLength':40},
      'iso':{'type':'string','pattern':'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\.[0-9]{9}Z$','maxLength':30},
      'hash':{'type':'string','pattern':'^sha256:[0-9a-f]{64}$','maxLength':71},
      'hex':{'type':'string','pattern':'^([0-9a-f]{2})*$','maxLength':131072},
      'signature':{'type':'string','minLength':88,'maxLength':88},
    }
    d['binding']=obj({'PolicyID':ref('id'),'PolicyVersion':const('0'),'PolicyDigest':ref('hash')})
    d['origin']=obj({'Kind':const('derived'),'DerivationPlanDigest':ref('hash'),'SourceEntryID':ref('id')})
    d['header']=obj({'EventID':ref('id'),'ActorID':ref('id'),'ChainID':ref('id'),
      'SequenceNum':ref('uint'),'EventType':const('RESEARCH_LAYOUT_ONLY'),
      'PolicyID':ref('id'),'TimestampInt':ref('uint'),'TimestampISO':ref('iso')})
    # These paths exercise placement only; this is NOT a complete module/event schema.
    d['payload']=obj({
      'VCP-ANCHOR':obj({'FailoverDetails':obj({'TriggerCondition':obj({'TotalDowntimeSec':ref('uint')})})}),
      'VCP-XREF':obj({'SharedEventKey':obj({'ToleranceMs':ref('uint')})}),
      'VCP-GOV':obj({'ConfidenceScore':ref('decimal'),
          'PerformanceMetadata':obj({'LatencyImpact':ref('decimal')})})})
    d['event']=obj({'ContractID':const(CONTRACT),'EventHashAlgorithm':const('SHA-256'),
      'Header':ref('header'),'Payload':ref('payload'),
      'PolicyIdentification':{'oneOf':[{'type':'null'},obj({'PolicyID':ref('id'),'Version':const('0')})]},
      'RegistrationPolicyBinding':ref('binding'),'NumericPolicyBinding':ref('binding'),
      'Origin':ref('origin'),'ChainMode':{'enum':['start','linked']},
      'PreviousEventHash':{'oneOf':[{'type':'null'},ref('hash')]}})
    common={'ContractID':const(CONTRACT),'SignatureAlgorithm':const('Ed25519'),'KeyID':ref('id')}
    d['event_statement']=obj(dict(common,EventHash=ref('hash'),EventID=ref('id'),ActorID=ref('id'),ChainID=ref('id')))
    d['envelope']=obj({'Commitment':ref('event'),'Statement':ref('event_statement'),'Signature':ref('signature')})
    d['anchor_statement']=obj(dict(common,ActorID=ref('id'),ChainID=ref('id'),
      RegistrationPolicyBinding=ref('binding'),NumericPolicyBinding=ref('binding'),
      TreeScheme=const('research-rfc6962-digest-leaf-v0'),EventCount=ref('uint'),
      FirstEventID=ref('id'),LastEventID=ref('id'),MerkleRoot=ref('hash'),RecordedAtNs=ref('uint'),
      IntendedTarget=const('synthetic-unconnected')))
    d['anchor']=obj({'Statement':ref('anchor_statement'),'Signature':ref('signature')})
    d['proof']=obj({'EventID':ref('id'),'LeafIndex':ref('uint'),'Path':arr(ref('hash'),0,16)})
    d['source_entry']=obj({'EntryID':ref('id'),'OriginalHex':ref('hex'),'RetainedHex':ref('hex'),
      'Signature':ref('signature'),'RetainedSignature':ref('signature')})
    d['manifest_entry']=obj({'EntryID':ref('id'),'RawSHA256':ref('hash'),'SignatureSHA256':ref('hash')})
    d['evidence_entry']=obj({'ArtifactID':ref('id'),'RawSHA256':ref('hash')})
    d['evidence']=obj({'ArtifactID':ref('id'),'OriginalHex':ref('hex'),'RetainedHex':ref('hex')})
    d['manifest']=obj({'SourceFormat':const(SOURCE),'Entries':arr(ref('manifest_entry')),
                       'Evidence':arr(ref('evidence_entry'))})
    d['mapping']=obj({'SourceEntryID':ref('id'),'TargetEventID':ref('id')})
    d['plan']=obj({'ContractID':const(CONTRACT),'PlanID':ref('id'),'SourceManifestDigest':ref('hash'),
      'SourceFormat':const(SOURCE),'TargetActorID':ref('id'),'TargetChainID':ref('id'),
      'RegistrationPolicyBinding':ref('binding'),'NumericPolicyBinding':ref('binding'),
      'ConversionRule':const('research-exact-ms-to-s-preserve-decimals-v0'), 'Entries':arr(ref('mapping'))})
    d['attestation_statement']=obj(dict(common,DerivationPlanDigest=ref('hash'),SourceManifestDigest=ref('hash'),
      TargetArtifactDigest=ref('hash'),CreatedAtNs=ref('uint'),Support=const('synthetic internal execution; no external evaluator'),
      ConversionRule=const('research-exact-ms-to-s-preserve-decimals-v0')))
    d['attestation']=obj({'Statement':ref('attestation_statement'),'Signature':ref('signature')})
    d['policy_bytes']=obj({'registration':ref('hex'),'numeric':ref('hex')})
    bundle=obj({'ContractID':const(CONTRACT),'Policies':ref('policy_bytes'),'SourceManifest':ref('manifest'),
      'SourceArtifacts':arr(ref('source_entry')),'PreservedEvidence':arr(ref('evidence')),
      'DerivationPlan':ref('plan'),'Events':arr(ref('envelope')),
      'Anchor':ref('anchor'),'InclusionEvidence':arr(ref('proof')),'MigrationAttestation':ref('attestation')})
    return dict(bundle,**{'$schema':'https://json-schema.org/draft/2020-12/schema',
      '$id':CONTRACT+':schema','$comment':'UNADOPTED. SYNTHETIC SUBSET ONLY. Independent third-party reproduction not established.',
      '$defs':d})

if __name__=='__main__':
    print(json.dumps(build(),indent=2,ensure_ascii=True))
