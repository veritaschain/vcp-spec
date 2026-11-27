"""Exercise raw-input and invocation boundaries without editing fixed fixtures."""
import json
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from validate_v1_2 import (LEGACY_SCHEMA, SCHEMA, FormatChecker, errors, load_json)

FIXTURES = ROOT / 'tests/fixtures/v1.2'
VALID = FIXTURES / 'valid/checkpoint-emergency.json'


class ValidatorCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.raw = VALID.read_text(encoding='utf-8')

    def write(self, name, content):
        path = self.directory / name
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding='utf-8')
        return path

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'tools/validate_v1_2.py'),
                               *map(str, args)], cwd=ROOT, capture_output=True,
                              text=True, timeout=15)

    def assert_rejected(self, result, code=1):
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn('LOCAL CHECKS PASS', result.stdout)
        self.assertNotIn('Traceback', result.stdout + result.stderr)

    def test_current_valid_control_preserves_large_integer(self):
        self.assertEqual(load_json(VALID)['Header']['TimestampInt'], 1791504000000000000)
        result = self.run_cli(VALID)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('cryptographic/external checks not performed', result.stdout)

    def test_duplicate_keys_are_rejected_before_values_are_discarded(self):
        candidates = [
            self.raw.replace('"Header":', '"Header": null, "Header":', 1),
            self.raw.replace('"SequenceNum": 1', '"SequenceNum": 2, "SequenceNum": 1'),
            self.raw.replace('"SequenceNum": 1', '"SequenceNum": 1, "SequenceNum": 1'),
            self.raw.replace('"SequenceNum": 1', '"SequenceNum": 2, "SequenceN\\u0075m": 1'),
        ]
        for index, raw in enumerate(candidates):
            with self.subTest(index=index):
                result = self.run_cli(self.write('duplicate.json', raw))
                self.assert_rejected(result)
                self.assertIn('duplicate JSON object key', result.stdout)

    def test_non_json_constants_are_rejected_even_in_extension_modules(self):
        for token in ('NaN', 'Infinity', '-Infinity'):
            with self.subTest(token=token):
                raw = self.raw.replace('"Payload": {',
                    '"Payload": {"VCP-CUSTOM":{"metric":' + token + '},', 1)
                result = self.run_cli(self.write('constant.json', raw))
                self.assert_rejected(result)
                self.assertIn('non-JSON numeric constant', result.stdout)

    def test_decimal_tokens_cannot_round_into_valid_integer_fields(self):
        for token in ('1.0000000000000001', '1e-400', '-1e-400'):
            with self.subTest(token=token):
                raw = self.raw.replace('"SequenceNum": 1', '"SequenceNum": ' + token)
                result = self.run_cli(self.write('fraction.json', raw))
                self.assert_rejected(result)
                self.assertIn('Header/SequenceNum', result.stdout)
        for token in ('1.0', '1e0'):
            with self.subTest(integral_token=token):
                raw = self.raw.replace('"SequenceNum": 1', '"SequenceNum": ' + token)
                result = self.run_cli(self.write('integral.json', raw))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        parsed = load_json(self.write('number.json', '{"value": 1e999}'))
        self.assertEqual(parsed['value'], Decimal('1e999'))
        self.assertTrue(parsed['value'].is_finite())

    def test_legacy_cannot_skip_current_checks_through_schema_path_spelling(self):
        invalid = FIXTURES / 'invalid/emergency-duplicate-role.json'
        schemas = (SCHEMA, SCHEMA.relative_to(ROOT),
                   self.write('current-schema.json', SCHEMA.read_bytes()))
        for schema in schemas:
            with self.subTest(schema=schema):
                result = self.run_cli('--legacy', '--schema', schema, invalid)
                self.assert_rejected(result, 2)
                self.assertIn('unchanged historical legacy schema', result.stderr)
        with self.assertRaisesRegex(ValueError, 'unchanged historical legacy schema'):
            errors(load_json(invalid), SCHEMA, legacy=True)
        self.assert_rejected(self.run_cli(invalid))

    def test_original_and_copied_legacy_schema_still_work(self):
        legacy = FIXTURES / 'valid/legacy-retention_expired.json'
        for schema in (LEGACY_SCHEMA, self.write('legacy-copy.json', LEGACY_SCHEMA.read_bytes())):
            with self.subTest(schema=schema):
                result = self.run_cli('--legacy', '--schema', schema, legacy)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('LOCAL CHECKS PASS', result.stdout)

    def test_invalid_input_reports_each_file_without_aborting_later_checks(self):
        for raw in (b'\xff', b'{', b'[' * 1500,
                    b'{"value":1e999999999999999999999999999}'):
            with self.subTest(raw=raw[:40]):
                bad = self.write('invalid.json', raw)
                result = self.run_cli(bad, VALID)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(f'{bad}: INVALID INPUT:', result.stdout)
                self.assertIn(f'{VALID}: LOCAL CHECKS PASS', result.stdout)
                self.assertNotIn('Traceback', result.stderr)

    def test_operational_errors_use_exit_two_and_keep_later_results(self):
        missing = self.directory / 'missing.json'
        bad = self.write('invalid.json', '{')
        result = self.run_cli(missing, bad, VALID)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(f'{missing}: ERROR:', result.stdout)
        self.assertIn(f'{bad}: INVALID INPUT:', result.stdout)
        self.assertIn(f'{VALID}: LOCAL CHECKS PASS', result.stdout)
        for schema in (missing, self.write('bad-schema.json', '{'),
                       self.write('invalid-schema.json', '{"type": "not-a-type"}')):
            with self.subTest(schema=schema):
                self.assert_rejected(self.run_cli('--schema', schema, VALID), 2)

    def test_schema_reference_failure_is_a_configuration_error_for_the_batch(self):
        base_event = {"Header": {"EventType": "ORD"}}
        order = self.write("order.json", json.dumps(base_event))
        detailed = self.write("order-with-details.json",
                              json.dumps({**base_event, "details": {}}))
        reference = {"$ref": "#/$defs/Details"}
        schema = {
            "$defs": {"Details": {"type": "object"}},
            "properties": {"details": reference},
        }
        path = self.write("schema.json", json.dumps(schema))
        result = self.run_cli("--schema", path, order, detailed)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.count("LOCAL CHECKS PASS"), 2)

        # The first event can finish before the second follows the missing ref.
        del schema["$defs"]["Details"]
        for candidate in (reference, schema):
            with self.subTest(candidate=candidate):
                path = self.write("schema.json", json.dumps(candidate))
                result = self.run_cli("--schema", path, order, detailed)
                self.assert_rejected(result, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("cannot use schema", result.stderr)
                self.assertIn("Details", result.stderr)

    def test_missing_format_dependencies_cannot_silently_skip_date_checks(self):
        available = {key: value for key, value in FormatChecker.checkers.items()
                     if key != 'date-time'}
        with patch.dict(FormatChecker.checkers, available, clear=True):
            with self.assertRaisesRegex(ValueError, 'missing schema format checkers: date-time'):
                errors(load_json(FIXTURES / 'invalid/announce-bad-date.json'))

    def test_custom_schema_integer_keywords_keep_exact_json_schema_semantics(self):
        event = json.loads(self.raw)
        event['review_items'] = [1]
        valid = self.write('custom-event.json', json.dumps(event))
        event['review_items'] = []
        empty = self.write('custom-empty.json', json.dumps(event))
        for token in ('1.0', '1e0'):
            with self.subTest(integral_schema_token=token):
                schema = self.write('custom-schema.json',
                    '{"type":"object","properties":{"review_items":'
                    '{"type":"array","minItems":' + token + '}}}')
                result = self.run_cli('--schema', schema, valid)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                # The admitted integral bound still rejects an empty array.
                self.assert_rejected(self.run_cli('--schema', schema, empty))
        for token in ('1.0000000000000001', '1e-400', '-1.0'):
            with self.subTest(invalid_schema_token=token):
                schema = self.write('invalid-bound.json',
                    '{"type":"object","properties":{"review_items":'
                    '{"type":"array","minItems":' + token + '}}}')
                result = self.run_cli('--schema', schema, valid)
                self.assert_rejected(result, 2)
                self.assertIn('cannot use schema', result.stderr)

    def assert_custom_inputs_rejected(self, cases):
        schema = self.write('permissive-schema.json', '{}')
        sources = [self.write(f'local-input-{i}.json', json.dumps(event))
                   for i, event in enumerate(cases)]
        result = self.run_cli('--schema', schema, *sources, VALID)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for source in sources:
            self.assertIn(f'{source}: INVALID:', result.stdout)
            self.assertNotIn(f'{source}: LOCAL CHECKS PASS', result.stdout)
        self.assertIn(f'{VALID}: LOCAL CHECKS PASS', result.stdout)
        self.assertNotIn('Traceback', result.stdout + result.stderr)

    def test_custom_schema_missing_event_envelope_does_not_abort_batch(self):
        self.assert_custom_inputs_rejected([
            {}, None, [], 'not an event',
            {'Header': None}, {'Header': []}, {'Header': {}},
            {'Header': {'EventType': []}}, {'Header': {'EventType': 1}},
        ])
        # A custom vocabulary remains possible; the default schema is not
        # silently reapplied when no selected rule inspects this event type.
        schema = self.write('custom-envelope-schema.json', '{"type":"object"}')
        event = self.write('custom-envelope.json', json.dumps({
            'Header': {'EventType': 'CUSTOM_REVIEW'}, 'review_note': 'local only',
        }))
        result = self.run_cli('--schema', schema, event)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('cryptographic/external checks not performed', result.stdout)

    def test_custom_schema_malformed_selected_rule_inputs_do_not_abort_batch(self):
        cases = []
        mutations = {
            'erasure': [
                ('Payload', None),
                ('Payload/VCP-PRIVACY/ErasureDetails/Scope', []),
                ('Payload/VCP-PRIVACY/ErasureDetails/Scope/AffectedEventCount', True),
                ('Payload/VCP-PRIVACY/ErasureDetails/Scope/EventIDs', {}),
                ('Payload/VCP-PRIVACY/ErasureDetails/Authorization', {}),
                ('Payload/VCP-PRIVACY/ErasureDetails/CryptoShredding/DestructionTimestamp', 'later'),
                ('Header/TimestampInt', 1.5),
            ],
            'checkpoint-emergency': [
                ('Payload/VCP-RECOVERY', {}),
                ('Payload/VCP-RECOVERY/RecoveryAction', []),
                ('Payload/VCP-RECOVERY/RecoveryAction/EmergencyOverride', None),
                ('Payload/VCP-RECOVERY/RecoveryAction/EmergencyOverride/IsEmergency', 'yes'),
                ('Payload/VCP-RECOVERY/RecoveryAction/EmergencyOverride/ApprovalChain', {}),
                ('Payload/VCP-RECOVERY/RecoveryAction/EmergencyOverride/ApprovalChain', [None]),
                ('Payload/VCP-RECOVERY/RecoveryAction/EmergencyOverride/ApprovalChain', [{}]),
                ('Payload/VCP-RECOVERY/RecoveryAction/EmergencyOverride/ApprovalChain',
                 [{'ApproverRoleID': {}, 'ApprovalTimestamp': 'later'}]),
                ('Header/TimestampInt', None),
            ],
            'anchor-migration': [
                ('Payload/VCP-ANCHOR/MigrationDetails', {}),
                ('Payload/VCP-ANCHOR/MigrationDetails/DualAnchorPeriod/StartTimestamp', 'earlier'),
                ('Payload/VCP-ANCHOR/MigrationDetails/DualAnchorPeriod/EndTimestamp', None),
            ],
        }
        for fixture, edits in mutations.items():
            for path, replacement in edits:
                event = json.loads((FIXTURES / f'valid/{fixture}.json').read_text())
                target = event
                keys = path.split('/')
                for key in keys[:-1]:
                    target = target[key]
                target[keys[-1]] = replacement
                cases.append(event)
        self.assert_custom_inputs_rejected(cases)

    def test_custom_schema_keeps_existing_local_rule_rejections(self):
        sources = [FIXTURES / f'invalid/{name}.json' for name in (
            'emergency-duplicate-role', 'erasure-destruction-before-authorization',
            'migration-reversed-overlap')]
        schema = self.write('permissive-schema.json', '{"type":"object"}')
        result = self.run_cli('--schema', schema, *sources, VALID)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for source in sources:
            self.assertIn(f'{source}: INVALID:', result.stdout)
        self.assertIn(f'{VALID}: LOCAL CHECKS PASS', result.stdout)
        self.assertNotIn('Traceback', result.stdout + result.stderr)

    def test_format_instance_data_is_not_a_schema_format_requirement(self):
        event = json.loads(self.raw)
        event['format'] = 'instance-format-label'
        source = self.write('annotated-event.json', json.dumps(event))
        schema = self.write('annotated-schema.json', json.dumps({
            'type': 'object',
            'examples': [{'format': 'example-format-label'}],
            'default': {'format': 'default-format-label'},
            'enum': [event],
            'x-annotation': {'format': 'annotation-format-label'},
        }))
        result = self.run_cli('--schema', schema, source)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for location in ('properties', '$defs'):
            with self.subTest(schema_location=location):
                actual_format = self.write('actual-format.json', json.dumps({
                    'type': 'object', location: {'review_value': {
                        'type': 'string', 'format': 'unsupported-format-checker'}},
                }))
                result = self.run_cli('--schema', actual_format, source)
                self.assert_rejected(result, 2)
                self.assertIn('missing schema format checkers: unsupported-format-checker',
                              result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
