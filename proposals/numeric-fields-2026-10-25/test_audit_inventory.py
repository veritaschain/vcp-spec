"""Regression tests for this proposal's inventory audit only.

Every mutation is confined to a temporary copy. No existing VCP validator,
current schema, signed data, release or K3 fixture is modified.
"""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import audit_inventory as audit


class InventoryAuditTests(unittest.TestCase):
    def setUp(self):
        self.original_here, self.original_root = audit.HERE, audit.ROOT
        self.temporary = tempfile.TemporaryDirectory(prefix="vcp-numeric-audit-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.here = self.root / "proposals/numeric-fields-2026-10-25"
        self.here.mkdir(parents=True)
        self.manifest = audit.read_json(self.original_here / "sources.json")
        self.inventory = audit.read_json(self.original_here / "inventory.json")
        for name in ("sources.json", "inventory.json", "inventory.md"):
            shutil.copyfile(self.original_here / name, self.here / name)
        files = [v["path"] for v in self.manifest["sources"].values()] + [
            "VCP-Specification-v1_2_en.md", "VSO-SPEC-CHANGE-001.md"]
        for name in files:
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.original_root / name, destination)
        audit.HERE, audit.ROOT = self.here, self.root
        self.addCleanup(self.restore_paths)

    def restore_paths(self):
        audit.HERE, audit.ROOT = self.original_here, self.original_root

    def write_inventory(self, value):
        (self.here / "inventory.json").write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        # A matching rendered file must not hide a bad source snapshot.
        (self.here / "inventory.md").write_text(
            audit.render(value["fields"], self.manifest["sources"]), encoding="utf-8")

    def test_original_inventory_passes_without_writing(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = audit.audit()
        self.assertEqual(result["status"], "inventory_consistency_pass")
        self.assertEqual((result["schema_definition_sites"], result["schema_instance_paths"],
                          result["review_entries"]), (34, 35, 74))
        self.assertEqual(result["independent_reproduction"], "not_established")
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(after, before)

    def test_snapshot_numeric_types_are_not_coerced(self):
        for field_id, replacement in (("N002", False), ("N013", True), ("N002", 0.0)):
            with self.subTest(field=field_id, replacement=repr(replacement)):
                value = copy.deepcopy(self.inventory)
                row = next(r for r in value["fields"] if r["id"] == field_id)
                row["schema"]["constraints"]["minimum"] = replacement
                self.write_inventory(value)
                with self.assertRaisesRegex(ValueError, "schema snapshot mismatch"):
                    audit.audit()

    def test_duplicate_inventory_keys_are_rejected(self):
        original = (self.here / "inventory.json").read_text(encoding="utf-8")
        for changed in (original.replace("{", '{"status":"ADOPTED",', 1),
                        original.replace('"minimum": 0', '"minimum": false, "minimum": 0', 1)):
            with self.subTest(changed=changed[:40]):
                (self.here / "inventory.json").write_text(changed, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                    audit.audit()

    def test_duplicate_manifest_keys_are_rejected(self):
        path = self.here / "sources.json"
        path.write_text(path.read_text(encoding="utf-8").replace("{", '{"commit":"wrong",', 1),
                        encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON key: commit"):
            audit.audit()

    def test_non_json_numeric_constants_are_rejected(self):
        original = (self.here / "inventory.json").read_text(encoding="utf-8")
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                changed = original.replace("{", '{"invalid_extra":' + token + ",", 1)
                (self.here / "inventory.json").write_text(changed, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "non-JSON numeric constant"):
                    audit.audit()

    def test_missing_schema_path_is_rejected(self):
        self.inventory["fields"] = [r for r in self.inventory["fields"] if r["id"] != "N002"]
        self.write_inventory(self.inventory)
        with self.assertRaisesRegex(ValueError, "missing/extra schema instance path"):
            audit.audit()

    def test_changed_constraint_is_rejected(self):
        row = next(r for r in self.inventory["fields"] if r["id"] == "N002")
        row["schema"]["constraints"]["minimum"] = 1
        self.write_inventory(self.inventory)
        with self.assertRaisesRegex(ValueError, "schema snapshot mismatch"):
            audit.audit()

    def test_requiredness_cannot_be_numeric(self):
        self.inventory["fields"][0]["schema"]["required_in_containing_object"] = 1
        self.write_inventory(self.inventory)
        with self.assertRaisesRegex(ValueError, "requiredness mismatch"):
            audit.audit()

    def test_source_hash_drift_is_rejected(self):
        path = self.root / self.manifest["sources"]["schema"]["path"]
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "source drift: schema"):
            audit.audit()

    def test_generated_markdown_drift_is_rejected(self):
        path = self.here / "inventory.md"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "generated inventory.md drift"):
            audit.audit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
