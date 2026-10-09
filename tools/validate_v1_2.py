"""Local syntax and selected intra-event checks; NOT a cryptographic verifier."""
import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'spec/v1.2/vcp-event-v1.2.json'


def errors(event, schema_path=SCHEMA, legacy=False):
    schema = json.loads(Path(schema_path).read_text())
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    result = [f'{"/".join(map(str, e.absolute_path))}: {e.message}' for e in validator.iter_errors(event)]
    if result or legacy:
        return result
    kind = event['Header']['EventType']
    if kind == 'ERASURE':
        d = event['Payload']['VCP-PRIVACY']['ErasureDetails']
        scope = d['Scope']
        ids = scope.get('EventIDs')
        if ids and (len(ids) != scope['AffectedEventCount'] or ids[0] != scope['FirstAffectedEventID'] or ids[-1] != scope['LastAffectedEventID']):
            result.append('Scope.EventIDs must match AffectedEventCount and first/last IDs')
        if scope['AffectedEventCount'] == 1 and scope['FirstAffectedEventID'] != scope['LastAffectedEventID']:
            result.append('Scope single-event first/last IDs must match AffectedEventCount')
        if not d['Authorization']['AuthorizationTimestamp'] <= d['CryptoShredding']['DestructionTimestamp'] <= event['Header']['TimestampInt']:
            result.append('Erasure authorization <= destruction <= event timestamp is required')
        if d['CryptoShredding']['DestructionMethod'] in ('HSM_ZEROIZE', 'CLOUD_KMS_DESTROY') and not d['CryptoShredding'].get('DestructionCertificate'):
            result.append('DestructionCertificate required for HSM/KMS evidence')
    elif kind == 'SYS_CHECKPOINT':
        override = event['Payload']['VCP-RECOVERY']['RecoveryAction'].get('EmergencyOverride', {})
        if override.get('IsEmergency'):
            approvals = override['ApprovalChain']
            roles = [a['ApproverRoleID'] for a in approvals]
            if len(set(roles)) != len(roles):
                result.append('Emergency approvals require distinct role identifiers (human identity must be checked externally)')
            if any(a['ApprovalTimestamp'] > event['Header']['TimestampInt'] for a in approvals):
                result.append('Emergency approval cannot occur after checkpoint')
    elif kind == 'SYS_ANCHOR_MIGRATION':
        overlap = event['Payload']['VCP-ANCHOR']['MigrationDetails']['DualAnchorPeriod']
        if overlap['StartTimestamp'] > overlap['EndTimestamp']:
            result.append('Migration overlap start must not follow end')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--schema', type=Path, default=SCHEMA)
    parser.add_argument('--legacy', action='store_true', help='Historical compact syntax only; requires the legacy schema')
    args = parser.parse_args()
    if args.legacy and args.schema == SCHEMA:
        parser.error('--legacy requires --schema spec/v1.2/vcp-event-v1.2-rc-legacy.json')
    failed = False
    for file in args.files:
        failures = errors(json.loads(file.read_text()), args.schema, args.legacy)
        failed |= bool(failures)
        print(f'{file}: ' + ('INVALID: ' + '; '.join(failures) if failures else 'LOCAL CHECKS PASS (cryptographic/external checks not performed)'))
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
