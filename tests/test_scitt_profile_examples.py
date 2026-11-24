"""Regression checks for unadopted I-D examples, independent of VCP conformance."""

import importlib.util
import hashlib
import json
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from jsonschema import Draft202012Validator, FormatChecker

REPO = Path(__file__).resolve().parents[1]
PROPOSAL = REPO / "proposals" / "scitt-profile-06-followup-2026-11-20"
SPEC = importlib.util.spec_from_file_location("scitt_example_clock", PROPOSAL / "check_examples.py")
CLOCK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLOCK)


class ScittCandidateExamples(unittest.TestCase):
    def event(self, name="order"):
        return json.loads((PROPOSAL / "examples" / (name + ".json")).read_text())

    def test_all_three_examples_have_consistent_clocks(self):
        for name in ("header", "order", "erasure"):
            with self.subTest(name=name):
                self.assertEqual(CLOCK.check_clock(self.event(name)), [])

    def test_exact_known_timestamp(self):
        self.assertEqual(CLOCK.iso_ns("2026-03-15T09:30:00.123456789Z"), 1773567000123456789)
        self.assertEqual(CLOCK.iso_ns("1970-01-01T00:00:00.000000001Z"), 1)

    def test_published_order_example_is_detected(self):
        event = self.event()
        event["Header"]["TimestampInt"] = 1742034600123456789
        event["Header"]["EventID"] = "01961e5f-5c0d-7000-8000-123456789abc"
        self.assertEqual(CLOCK.check_clock(event), ["ISO_INTEGER_MISMATCH", "UUID_INTEGER_MISMATCH"])

    def test_published_erasure_uuid_mismatch_is_detected(self):
        event = self.event("erasure")
        event["Header"]["EventID"] = "019eaf10-0000-7000-8000-000000000001"
        self.assertEqual(CLOCK.check_clock(event), ["UUID_INTEGER_MISMATCH"])

    def test_float_or_boolean_timestamp_is_rejected(self):
        for value in (float(1773567000123456789), True):
            event = self.event()
            event["Header"]["TimestampInt"] = value
            self.assertEqual(CLOCK.check_clock(event), ["TIMESTAMP_NOT_INTEGER"])

    def test_wrong_uuid_version_is_rejected(self):
        event = self.event()
        event["Header"]["EventID"] = "00000000-0000-4000-8000-000000000001"
        self.assertEqual(CLOCK.check_clock(event), ["UUID_NOT_V7"])

    def test_destruction_after_erasure_is_rejected(self):
        event = self.event("erasure")
        event["Payload"]["VCP-PRIVACY"]["ErasureDetails"]["CryptoShredding"]["DestructionTimestamp"] = event["Header"]["TimestampInt"] + 1
        self.assertEqual(CLOCK.check_clock(event), ["ERASURE_TIME_ORDER"])

    def test_complete_examples_match_unchanged_schema_shape(self):
        schema = json.loads((REPO / "spec" / "v1.2" / "vcp-event-v1.2.json").read_text())
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for name in ("order", "erasure"):
            with self.subTest(name=name):
                self.assertEqual(list(validator.iter_errors(self.event(name))), [])

    def test_rotated_event_type_is_not_silently_added(self):
        schema = json.loads((REPO / "spec" / "v1.2" / "vcp-event-v1.2.json").read_text())
        event = self.event()
        event["Header"]["EventType"] = "ROTATE"
        errors = list(Draft202012Validator(schema).iter_errors(event))
        self.assertTrue(any(e.validator == "enum" and list(e.path) == ["Header", "EventType"] for e in errors))

    def test_xml_carries_the_reviewed_json_examples(self):
        tree = ET.parse(PROPOSAL / "draft-kamimura-scitt-vcp-07.xml")
        for name, anchor in (("header", "schema-header"), ("order", "appendix-example"), ("erasure", "erasure-event")):
            node = tree.find(".//section[@anchor='" + anchor + "']/sourcecode[@type='json']")
            self.assertEqual(json.loads(node.text), self.event(name))

    def test_submission_xml_has_no_candidate_notice_and_the_generator_date(self):
        spec = importlib.util.spec_from_file_location("scitt_generate", PROPOSAL / "generate_candidate.py")
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
        text = (PROPOSAL / "draft-kamimura-scitt-vcp-07.xml").read_text()
        for phrase in ("Unsubmitted", "unsubmitted", "provisional. The published", "This candidate", "this candidate"):
            self.assertNotIn(phrase, text)
        root = ET.fromstring(text)
        self.assertEqual(root.get("docName"), "draft-kamimura-scitt-vcp-07")
        date = root.find("front/date")
        self.assertEqual((int(date.get("year")), date.get("month"), int(date.get("day"))), generator.DOC_DATE)
        rendered = (PROPOSAL / "draft-kamimura-scitt-vcp-07.txt").read_text()
        self.assertIn("%d %s %d" % (generator.DOC_DATE[2], generator.DOC_DATE[1], generator.DOC_DATE[0]), rendered)
        self.assertNotIn("unsubmitted", rendered)

    def test_render_record_matches_both_candidate_artifacts(self):
        record = json.loads((PROPOSAL / "rendered-manifest.json").read_text())
        for key in ("source", "output"):
            item = record[key]
            self.assertEqual(hashlib.sha256((PROPOSAL / item["path"]).read_bytes()).hexdigest(), item["sha256"])


if __name__ == "__main__":
    unittest.main()
