import copy
import json
import re
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from validate_v1_2 import errors

SPEC = ROOT / 'spec/v1.2'
FIXTURES = ROOT / 'tests/fixtures/v1.2'


class V12ContractTests(unittest.TestCase):
    def test_schemas_and_internal_refs(self):
        for name in ('vcp-event-v1.2.json', 'vcp-event-v1.2-rc-legacy.json'):
            schema = json.loads((SPEC / name).read_text())
            Draft202012Validator.check_schema(schema)
            def walk(value):
                if isinstance(value, dict):
                    if '$ref' in value:
                        self.assertTrue(value['$ref'].startswith('#/'))
                        target = schema
                        for part in value['$ref'][2:].split('/'):
                            target = target[part.replace('~1', '/').replace('~0', '~')]
                    for item in value.values(): walk(item)
                elif isinstance(value, list):
                    for item in value: walk(item)
            walk(schema)

    def test_fixture_manifest(self):
        cases = json.loads((FIXTURES / 'manifest.json').read_text())
        self.assertEqual({x['file'] for x in cases}, {str(p.relative_to(FIXTURES)) for p in FIXTURES.glob('*/*.json')})
        for case in cases:
            with self.subTest(file=case['file']):
                legacy = case['contract'] == 'legacy'
                path = SPEC / ('vcp-event-v1.2-rc-legacy.json' if legacy else 'vcp-event-v1.2.json')
                failures = errors(json.loads((FIXTURES / case['file']).read_text()), path, legacy)
                self.assertEqual(not failures, case['valid'], failures)
                if case.get('error_contains'):
                    self.assertTrue(any(case['error_contains'] in failure for failure in failures), failures)

    def test_old_schema_reproduces_p1_findings(self):
        old = Draft202012Validator(json.loads((SPEC / 'vcp-event-v1.2-rc-legacy.json').read_text()), format_checker=FormatChecker())
        for name in ('recovery-announce','checkpoint-planned','audit','anchor-migration','anchor-failover'):
            event = json.loads((FIXTURES / f'valid/{name}.json').read_text())
            self.assertTrue(any(list(e.absolute_path) == ['Header','EventType'] for e in old.iter_errors(event)), name)
        self.assertFalse(old.is_valid(json.loads((FIXTURES / 'valid/erasure.json').read_text())))

    def test_mirrors_and_registry(self):
        for name in ['VSO-SPEC-CHANGE-001.md'] + [f'VCP-Specification-v1_2_{lang}.md' for lang in ('en','ja','zh')]:
            self.assertEqual((ROOT / name).read_bytes(), (SPEC / name).read_bytes())
        annex = (SPEC / 'VSO-SPEC-CHANGE-001.md').read_text()
        schema = json.loads((SPEC / 'vcp-event-v1.2.json').read_text())
        registered = set(schema['$defs']['Header']['properties']['EventType']['enum'])
        system = set(re.findall(r'\bSYS_[A-Z_]+\b', annex))
        self.assertEqual(system, {x for x in registered if x.startswith('SYS_')})
        for lang in ('en','ja','zh'):
            text = (SPEC / f'VCP-Specification-v1_2_{lang}.md').read_text()
            for kind in system: self.assertIn(kind, text)
            self.assertIn('Payload.VCP-PRIVACY.ErasureDetails', text)
        documented = set(re.findall(r'\| \*\*([A-Z_0-9]+)\*\* \|', annex.split('#### 3.4.1')[1].split('#### 3.4.2')[0]))
        self.assertEqual(documented, set(schema['$defs']['ErasureDetails']['properties']['Reason']['properties']['Code']['enum']))

    def test_canonical_annex_examples(self):
        text = (SPEC / 'VSO-SPEC-CHANGE-001.md').read_text()
        examples = re.findall(r'<!-- canonical-event -->\s*```json\s*(.*?)```', text, re.S)
        self.assertEqual(len(examples), 3)
        for example in examples:
            event = json.loads(example)
            self.assertEqual(errors(event), [])

    def test_non_erasure_contract_preserved(self):
        ga = json.loads((SPEC / 'vcp-event-v1.2.json').read_text())
        old = json.loads((SPEC / 'vcp-event-v1.2-rc-legacy.json').read_text())
        for name in ('UUID','DecimalString','SCITTAlignment','Security','PolicyIdentification'):
            self.assertEqual(ga['$defs'][name], old['$defs'][name])
        old_types = old['$defs']['Header']['properties']['EventType']['enum']
        self.assertTrue(set(old_types).issubset(ga['$defs']['Header']['properties']['EventType']['enum']))
        for name in ('VCP-TRADE','VCP-RISK','VCP-GOV','VCP-XREF','VCP-RECOVERY'):
            self.assertEqual(ga['$defs']['Payload']['properties'][name], old['$defs']['Payload']['properties'][name])


if __name__ == '__main__':
    unittest.main(verbosity=2)
