"""Local syntax and selected intra-event checks; NOT a cryptographic verifier."""
import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from jsonschema.validators import extend

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'spec/v1.2/vcp-event-v1.2.json'
LEGACY_SCHEMA = ROOT / 'spec/v1.2/vcp-event-v1.2-rc-legacy.json'


def _is_integer(checker, value):
    # JSON Schema accepts 1.0 as an integer, but not a fraction rounded to 1.0.
    # Exact parsing here does not define the protocol's unresolved signed bytes.
    return (Draft202012Validator.TYPE_CHECKER.is_type(value, 'integer') or
            isinstance(value, Decimal) and value.is_finite() and
            value == value.to_integral_value())


LocalValidator = extend(Draft202012Validator, type_checker=
                        Draft202012Validator.TYPE_CHECKER.redefine('integer', _is_integer))


def load_json(path):
    """Preserve numeric values and reject ambiguous/non-JSON file input."""
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'duplicate JSON object key: {key!r}')
            result[key] = value
        return result

    def reject_constant(token):
        raise ValueError(f'non-JSON numeric constant: {token}')

    def exact_number(token):
        try:
            return Decimal(token)
        except InvalidOperation as exc:
            raise ValueError('JSON number exceeds the local parser range') from exc

    return json.loads(Path(path).read_text(encoding='utf-8'),
                      object_pairs_hook=unique_pairs,
                      parse_constant=reject_constant, parse_float=exact_number)


def _check_schema(schema):
    # Referenced meta-schemas use the stock validator even when the entry class
    # is extended. Correct only its false integer-type errors for exact Decimal
    # values; all other type, minimum and structural errors remain authoritative.
    validator = Draft202012Validator(Draft202012Validator.META_SCHEMA,
                                     format_checker=Draft202012Validator.FORMAT_CHECKER)
    for error in validator.iter_errors(schema):
        if (error.validator == 'type' and error.validator_value == 'integer' and
                isinstance(error.instance, Decimal) and _is_integer(None, error.instance)):
            continue
        raise SchemaError.create_from(error)


def _schema_formats(schema):
    # Traverse schema locations, not example/default/enum instance data or
    # unknown annotation keywords whose objects can also have a "format" key.
    maps = ('$defs', 'definitions', 'properties', 'patternProperties', 'dependentSchemas')
    arrays = ('allOf', 'anyOf', 'oneOf', 'prefixItems')
    singles = ('additionalProperties', 'unevaluatedProperties', 'propertyNames',
               'items', 'contains', 'unevaluatedItems', 'not', 'if', 'then', 'else')
    formats, pending = set(), [schema]
    while pending:
        value = pending.pop()
        if not isinstance(value, dict):
            continue
        if isinstance(value.get('format'), str):
            formats.add(value['format'])
        for keyword in maps:
            if isinstance(value.get(keyword), dict):
                pending.extend(value[keyword].values())
        for keyword in arrays:
            if isinstance(value.get(keyword), list):
                pending.extend(value[keyword])
        pending.extend(value[keyword] for keyword in singles if keyword in value)
    return formats


def _validator(schema_path, legacy):
    schema = load_json(schema_path)
    if legacy and schema != load_json(LEGACY_SCHEMA):
        raise ValueError('--legacy requires the unchanged historical legacy schema '
                         '(spec/v1.2/vcp-event-v1.2-rc-legacy.json)')
    _check_schema(schema)
    checker = FormatChecker()
    missing = _schema_formats(schema) - checker.checkers.keys()
    if missing:
        raise ValueError('missing schema format checkers: ' + ', '.join(sorted(missing)) +
                         '; install requirements-test.txt')
    return LocalValidator(schema, format_checker=checker)


def errors(event, schema_path=SCHEMA, legacy=False):
    return _event_errors(event, _validator(schema_path, legacy), legacy)


def _event_errors(event, validator, legacy):
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
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--schema', type=Path, default=SCHEMA)
    parser.add_argument('--legacy', action='store_true', help='Historical compact syntax only; requires the unchanged legacy schema')
    args = parser.parse_args()
    try:
        validator = _validator(args.schema, args.legacy)
    except (OSError, ValueError, RecursionError, SchemaError) as exc:
        parser.exit(2, f'ERROR: cannot use schema: {exc}\n')
    exit_code = 0
    for file in args.files:
        try:
            event = load_json(file)
        except OSError as exc:
            print(f'{file}: ERROR: {exc}')
            exit_code = 2
            continue
        except (ValueError, RecursionError) as exc:
            print(f'{file}: INVALID INPUT: {exc}')
            exit_code = max(exit_code, 1)
            continue
        failures = _event_errors(event, validator, args.legacy)
        exit_code = max(exit_code, int(bool(failures)))
        print(f'{file}: ' + ('INVALID: ' + '; '.join(failures) if failures else 'LOCAL CHECKS PASS (cryptographic/external checks not performed)'))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
