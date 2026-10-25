"""Boundary/false-success regressions for this composition only."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

import common as m
import checker
import fixtures
import run


class CompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = fixtures.build()
        cls.cases = {c["id"]: c for c in cls.data["cases"]}

    def actual(self, name):
        return checker.evaluate(self.cases[name]["bundle"])

    def test_valid_signature_does_not_validate_iso(self):
        r = self.actual("resigned-wrong-iso-year")
        self.assertEqual(r["checks"]["event_crypto"], "PASS")
        self.assertEqual(r["checks"]["event_binding"], "PASS")
        self.assertEqual(r["covered_checks_result"], "FAIL")

    def test_old_signature_does_not_bind_new_event(self):
        r = self.actual("one-ns-stale-statements")
        self.assertEqual(r["checks"]["event_crypto"], "PASS")
        self.assertEqual(r["checks"]["event_binding"], "FAIL")
        self.assertEqual(r["checks"]["batch_binding"], "FAIL")

    def test_rehash_without_resign_fails_crypto(self):
        self.assertEqual(self.actual("one-ns-rehashed-not-resigned")["checks"]["event_crypto"], "FAIL")

    def test_equal_numeric_lexemes_are_different_commitments(self):
        a, b = self.actual("baseline"), self.actual("confidence-leading-zero")
        self.assertEqual(b["covered_checks_result"], "PASS")
        self.assertNotEqual(a["trace"]["event_hash"], b["trace"]["event_hash"])
        self.assertNotEqual(self.actual("confidence-zero")["trace"]["event_hash"], self.actual("confidence-negative-zero")["trace"]["event_hash"])

    def test_type_changes_are_not_coerced(self):
        for name in ("confidence-boolean", "confidence-null", "confidence-json-number", "epoch-json-number-one"):
            self.assertEqual(self.actual(name)["checks"]["numeric"], "FAIL", name)
        self.assertNotIn("event_hash", self.actual("epoch-json-number-one")["trace"])
        self.assertFalse(m.same(True, 1))
        self.assertFalse(m.same(1, 1.0))

    def test_signed_wrong_units_and_unsigned_repairs_fail(self):
        for name in ("duration-equivalent-ms-unmapped", "timestamp-unit-mismatch-signed", "unsigned-unit-cannot-fill-omission"):
            self.assertEqual(self.actual(name)["covered_checks_result"], "FAIL", name)

    def test_exact_policy_bytes_are_bound(self):
        a = self.actual("policy-byte-change-unbound")
        self.assertEqual(a["checks"]["policy_interpretation"], "PASS")
        self.assertEqual(a["checks"]["policy_binding"], "FAIL")
        self.assertEqual(self.actual("policy-byte-change-new-evidence")["covered_checks_result"], "PASS")

    def test_unknown_key_id_not_authorized_by_valid_crypto(self):
        r = self.actual("signed-unknown-key-id")
        self.assertEqual(r["checks"]["event_crypto"], "PASS")
        self.assertEqual(r["covered_checks_result"], "UNASSESSED")

    def test_wrong_key_and_domain_really_fail_ed25519(self):
        for name in ("event-wrong-role-key", "event-wrong-domain-prefix", "anchor-signature-corrupted"):
            r = self.actual(name)
            self.assertEqual(r["checks"]["anchor_crypto" if name.startswith("anchor") else "event_crypto"], "FAIL")

    def test_malformed_signature_not_reported_as_checked(self):
        r = self.actual("event-malformed-signature")
        self.assertEqual(r["checks"]["event_signature_encoding"], "FAIL")
        self.assertEqual(r["checks"]["event_crypto"], "UNASSESSED")
        self.assertEqual(r["covered_checks_result"], "FAIL")

    def test_missing_expected_cases_or_checks_rejected(self):
        for mutate in (lambda d: d["cases"].pop(), lambda d: d["cases"][0]["expected"]["checks"].pop("numeric"),
                       lambda d: d["cases"].append(d["cases"][0])):
            data = copy.deepcopy(self.data)
            mutate(data)
            with self.assertRaises(ValueError):
                run.validate_cases(data)

    def test_evidence_cannot_substitute_trusted_key(self):
        data = copy.deepcopy(self.data)
        data["test_keys"]["event"]["public_key_hex"] = m.PUBLIC_KEYS["anchor"]
        with self.assertRaises(ValueError):
            run.validate_cases(data)

    def test_boolean_result_is_not_a_status(self):
        with self.assertRaises(ValueError):
            checker.aggregate([True])
        with self.assertRaises(ValueError):
            checker.aggregate([])

    def test_failure_dominates_unknown_without_erasing_it(self):
        r = self.actual("unselected-policy-resigned")
        self.assertEqual(r["covered_checks_result"], "FAIL")
        self.assertEqual(r["checks"]["policy_interpretation"], "UNASSESSED")

    def test_skips_and_expected_failures_never_count_as_success(self):
        result = unittest.TestResult()
        result.testsRun = run.REGRESSION_COUNT
        self.assertTrue(run.regressions_ok(result))
        result.skipped.append((None, "skipped"))
        self.assertFalse(run.regressions_ok(result))
        result.skipped.clear()
        result.expectedFailures.append((None, "expected failure"))
        self.assertFalse(run.regressions_ok(result))
        result.expectedFailures.clear()
        result.testsRun -= 1
        self.assertFalse(run.regressions_ok(result))

    def test_manifest_cannot_omit_file(self):
        data = m.strict_json((m.HERE / "manifest.json").read_bytes())
        data["files"].pop("checker.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "manifest.json").write_bytes(m.json_bytes(data))
            with self.assertRaisesRegex(ValueError, "inventory"):
                run.manifest_check(root)

    def test_manifest_detects_altered_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in run.FILES | {"manifest.json"}:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_bytes((m.HERE / name).read_bytes())
            (root / "checker.py").write_text("# replaced\n")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                run.manifest_check(root)

    def test_duplicate_keys_rejected_before_event_hash(self):
        r = self.actual("duplicate-event-key")
        self.assertEqual(r["checks"]["event_parse"], "FAIL")
        self.assertNotIn("event_hash", r["trace"])

    def test_count_is_signed_and_checked_against_list(self):
        self.assertEqual(self.actual("anchor-count-stale-signature")["checks"]["anchor_crypto"], "FAIL")
        r = self.actual("anchor-count-resigned-wrong-list")
        self.assertEqual(r["checks"]["anchor_crypto"], "PASS")
        self.assertEqual(r["checks"]["batch_binding"], "FAIL")

    def test_unknowns_and_real_world_limits_remain(self):
        for name in ("smear-unmapped", "leap-unmapped"):
            self.assertEqual(self.actual(name)["covered_checks_result"], "UNASSESSED")
        r = self.actual("baseline")
        for name in ("native_vcp_conformance", "real_identity_and_authorization", "external_receipt_and_time"):
            self.assertEqual(r[name], "not_assessed")
        self.assertEqual(r["independent_reproduction"], "not_established")


if __name__ == "__main__":
    unittest.main()
