#!/usr/bin/env python3
"""Negative controls for the experimental checker and reproducibility harness."""
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import checker
import generate_vectors
import run


class NumericExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fields = checker.load_fields()
        cls.payload = generate_vectors.build()
        cls.cases = {c["id"]: c for c in cls.payload["cases"]}

    def check(self, name):
        case = self.cases[name]
        return checker.check_bytes(run.raw_input(case), self.fields)

    def test_json_types_do_not_collapse(self):
        self.assertFalse(run.same({"n": True}, {"n": 1}))
        self.assertFalse(run.same({"n": 1}, {"n": 1.0}))
        self.assertEqual(self.check("json-number-9007199254740993")["operation_result"], "FAIL")
        self.assertEqual(self.check("exact-string-9007199254740993")["values"]["exact_integer"], "9007199254740993")

    def test_extreme_number_exponents_return_structured_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            for name in ("number-exponent-too-large", "number-exponent-too-negative"):
                case = self.cases[name]
                path.write_bytes(run.raw_input(case))
                with self.subTest(name=name):
                    self.assertTrue(run.same(self.check(name), case["expected"]))
                    process = subprocess.run([sys.executable, str(checker.HERE / "checker.py"), str(path)], capture_output=True, check=False)
                    self.assertEqual(process.returncode, 1)
                    self.assertTrue(run.same(json.loads(process.stdout), case["expected"]))
                    self.assertEqual(process.stderr, b"")

    def test_manifest_inventory_and_types_are_closed(self):
        original = run.read_json(checker.HERE / "manifest.json")
        run.validate_manifest(original)
        for group in ("sources", "experiment"):
            for change in ("remove", "add", "empty", "invalid_hash", "hash_type"):
                manifest = copy.deepcopy(original)
                name = next(iter(manifest[group]))
                if change == "remove":
                    del manifest[group][name]
                elif change == "add":
                    manifest[group]["extra.json"] = "0" * 64
                elif change == "empty":
                    manifest[group] = {}
                else:
                    manifest[group][name] = "not-a-hash" if change == "invalid_hash" else 0
                with self.subTest(group=group, change=change), self.assertRaises(ValueError):
                    run.validate_manifest(manifest)
        for key, value in (("vector_count", True), ("regression_count", 0), ("regression_count", 18.0),
                           ("status", "ADOPTED"), ("unexpected", "value")):
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                run.validate_manifest(dict(original, **{key: value}))

    def test_omitted_changed_source_copy_is_rejected(self):
        # Mutate only an isolated temporary copy, never the repository sources.
        original = run.read_json(checker.HERE / "manifest.json")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            experiment = root / "experiments/numeric-representation-candidate-v0"
            experiment.mkdir(parents=True)
            for group, source, destination in (("sources", checker.ROOT, root), ("experiment", checker.HERE, experiment)):
                for name in original[group]:
                    target = destination / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source / name, target)
            omitted = "spec/v1.2/VCP-Specification-v1_2_en.md"
            changed = root / omitted
            changed.write_bytes(changed.read_bytes() + b"\nTemporary negative-control copy only.\n")
            del original["sources"][omitted]
            (experiment / "manifest.json").write_text(json.dumps(original))
            with patch.object(run, "ROOT", root), patch.object(run, "HERE", experiment), \
                 patch.object(checker, "ROOT", root), patch.object(checker, "HERE", experiment), \
                 patch.object(generate_vectors, "HERE", experiment), \
                 self.assertRaisesRegex(ValueError, "sources file inventory"):
                run.verify_setup()

    def test_duplicate_keys_and_nonfinite_rejected(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":{"b":0,"b":false}}', b'{"a":NaN}', b'{"a":Infinity}', b'{"a":-Infinity}'):
            with self.subTest(raw=raw), self.assertRaises(checker.InvalidInput):
                checker.parse_json(raw)

    def test_unicode_and_resource_bounds(self):
        for raw in (b'"\\ud800"', b'{"\\udfff":0}', b'\xff', b'[' * 2000 + b']' * 2000, b'0' * 262145):
            with self.subTest(raw=raw[:30]), self.assertRaises(checker.InvalidInput):
                checker.parse_json(raw)
        self.assertEqual(checker.parse_json(b'"\\ud83d\\ude00"'), "😀")

    def test_failure_keeps_unknown_checks(self):
        answer = self.check("iso-failure-over-unknown")
        self.assertEqual(answer["operation_result"], "FAIL")
        self.assertEqual(answer["checks"]["iso"]["status"], "UNASSESSED")
        self.assertEqual(answer["checks"]["equality"]["status"], "UNASSESSED")

    def test_decimal_lexical_evidence_preserved(self):
        values = [self.check("DEC_SIGNED-lexeme-" + str(i))["values"] for i in (3, 4, 5)]
        self.assertEqual([v["lexeme"] for v in values], ["1", "1.0", "01.00"])
        self.assertEqual(len({v["utf8_hex"] for v in values}), 3)
        self.assertEqual(self.check("DEC_NONNEG-lexeme-2")["values"]["lexeme"], "-0.000")

    def test_units_and_missing_counts_do_not_pass(self):
        self.assertEqual(self.check("tolerance-edge-bad-tolerance_unit")["operation_result"], "FAIL")
        self.assertEqual(self.check("N017-index-count-missing")["operation_result"], "UNASSESSED")
        self.assertEqual(self.check("N043-index-count-missing")["operation_result"], "UNASSESSED")
        self.assertEqual(self.check("unknown-unit-no-guess")["operation_result"], "UNASSESSED")

    def test_exact_time_math_and_no_overflow(self):
        self.assertEqual(self.check("iso-max")["values"]["iso_as_ns"], "9223372036854775807")
        self.assertEqual(self.check("seconds-exact-intermediate-overflow")["values"], {"duration_ns": "9223372036854775807000000000"})
        self.assertEqual(self.check("tolerance-above-binary64")["values"]["difference_ns"], "1")

    def test_unsupported_never_becomes_conformance(self):
        for name in ("field-N069", "field-N071", "field-N072", "field-N073", "iso-basis-smear", "field-N053"):
            with self.subTest(name=name):
                result = self.check(name)
                self.assertEqual(result["operation_result"], "UNASSESSED")
                self.assertEqual(result["protocol_conformance"], "not_assessed")
                self.assertEqual(result["authentication"], "not_assessed")
                self.assertEqual(result["independent_reproduction"], "not_established")

    def test_missing_or_duplicate_cases_rejected(self):
        empty = dict(self.payload, cases=[])
        duplicate = dict(self.payload, cases=self.payload["cases"] + [self.payload["cases"][0]])
        missing = dict(self.payload, cases=self.payload["cases"][1:])
        for value in (empty, duplicate, missing):
            with self.subTest(count=len(value["cases"])), self.assertRaises(ValueError):
                run.validate_cases(value)

    def test_incomplete_expected_and_ambiguous_input_rejected(self):
        for mutation in ("empty", "aggregate", "ambiguous"):
            value = copy.deepcopy(self.payload)
            if mutation == "empty":
                value["cases"][0]["expected"] = {}
            elif mutation == "aggregate":
                value["cases"][0]["expected"]["operation_result"] = "PASS"
            else:
                value["cases"][0]["raw_utf8"] = "{}"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                run.validate_cases(value)

    def test_result_mutations_are_detected(self):
        cases = [self.cases["TIME_NS-max"], self.cases["iso-leap-unmapped"], self.cases["tolerance-one-ns-outside"]]
        for mutation in ("empty", "always_pass", "erase_unknown", "lose_precision"):
            def wrong(raw, fields):
                value = checker.check_bytes(raw, fields)
                if mutation == "empty":
                    return {}
                if mutation == "always_pass":
                    value["operation_result"] = "PASS"
                elif mutation == "erase_unknown":
                    value["checks"] = {k: v for k, v in value["checks"].items() if v["status"] != "UNASSESSED"}
                else:
                    value["values"] = {}
                return value
            with self.subTest(mutation=mutation):
                self.assertTrue(any(not r["matched"] for r in run.evaluate(cases, self.fields, wrong)))

    def test_invalid_regression_success_is_rejected(self):
        good = {"tests": 15, "failures": 0, "errors": 0, "skipped": 0,
                "expected_failures": 0, "unexpected_successes": 0, "successful": True}
        self.assertTrue(run.regression_ok(good, 0, 15))
        for key, val in (("tests", 0), ("tests", 14), ("skipped", 1), ("expected_failures", 1),
                         ("unexpected_successes", 1), ("errors", 1), ("successful", 1)):
            with self.subTest(key=key, val=val):
                self.assertFalse(run.regression_ok(dict(good, **{key: val}), 0, 15))
        self.assertFalse(run.regression_ok(good, 1, 15))

    def test_catalog_units_cannot_be_silently_rebound(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            raw = (checker.HERE / "data/field-map.json").read_text().replace('"unit": "unix_ns"', '"unit": "unix_ms"', 1)
            (root / "data/field-map.json").write_text(raw)
            with patch.object(checker, "HERE", root), self.assertRaisesRegex(ValueError, "field map hash mismatch"):
                checker.load_fields()

    def test_stored_vectors_are_deterministic(self):
        self.assertEqual((checker.HERE / "data/vectors.json").read_bytes(), generate_vectors.encoded())
        self.assertEqual(len(run.validate_cases(self.payload)), len(self.payload["cases"]))
        manifest, _, _ = run.verify_setup()
        self.assertEqual(manifest["source_commit"], run.BASE)

    def test_cli_returns_distinct_status_codes_and_preserves_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            for name, code in (("TIME_NS-min", 0), ("TIME_NS-above-max", 1), ("field-N069", 2)):
                raw = run.raw_input(self.cases[name])
                path.write_bytes(raw)
                before = hashlib.sha256(raw).digest()
                process = subprocess.run([sys.executable, str(checker.HERE / "checker.py"), str(path)], capture_output=True, check=False)
                with self.subTest(name=name):
                    self.assertEqual(process.returncode, code, process.stderr)
                    self.assertTrue(run.same(json.loads(process.stdout), self.cases[name]["expected"]))
                    self.assertEqual(hashlib.sha256(path.read_bytes()).digest(), before)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(NumericExperimentTests)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    print(json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
                      "skipped": len(result.skipped), "expected_failures": len(result.expectedFailures),
                      "unexpected_successes": len(result.unexpectedSuccesses), "successful": result.wasSuccessful()}))
    sys.exit(0 if result.wasSuccessful() and not result.skipped and not result.expectedFailures else 1)
