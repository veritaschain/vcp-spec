#!/usr/bin/env python3
"""Reproduce this isolated, UNADOPTED numeric experiment with Python stdlib."""
import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path, PurePosixPath

import checker
import generate_vectors

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACT = "vcp-numeric-experiment-v0"
BASE = "16018dd405cad45bd8b11a7dc2278f6d95111ea6"
OPERATIONS = {"scalar", "iso_pair", "index_bound", "within_tolerance", "duration_add", "sequence"}
SOURCE_FILES = {
    "proposals/numeric-fields-2026-10-25/README.md",
    "proposals/numeric-fields-2026-10-25/inventory.json",
    "proposals/numeric-fields-2026-10-25/inventory.md",
    "proposals/numeric-fields-2026-10-25/sources.json",
    "spec/v1.2/VCP-Specification-v1_2_en.md",
    "spec/v1.2/vcp-event-v1.2.json",
    "spec/v1.2/VSO-SPEC-CHANGE-001.md",
    "VCP-Specification-v1_0_en.md",
}
EXPERIMENT_FILES = {"checker.py", "generate_vectors.py", "run.py", "test_checker.py",
                    "data/field-map.json", "data/vectors.json"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def same(a, b):
    """Do not collapse JSON booleans, integers and floating numbers."""
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def read_json(path):
    return checker.parse_json(path.read_bytes(), limit=8388608)


def validate_cases(payload):
    if type(payload) is not dict or set(payload) != {"contract", "status", "independent_reproduction", "cases"}:
        raise ValueError("invalid vector envelope")
    if (payload["contract"], payload["status"], payload["independent_reproduction"]) != (CONTRACT, "UNADOPTED", "not_established"):
        raise ValueError("invalid vector status")
    cases = payload["cases"]
    if type(cases) is not list or not cases:
        raise ValueError("empty/malformed vector cases")
    seen = set()
    for case in cases:
        if type(case) is not dict:
            raise ValueError("malformed case")
        forms = set(case) & {"input", "raw_utf8", "raw_hex"}
        if len(forms) != 1 or set(case) != {"id", "category", "expected", "note"} | forms:
            raise ValueError("ambiguous/malformed case input")
        if any(type(case[k]) is not str for k in ("id", "category", "note")) or not case["id"] or case["id"] in seen:
            raise ValueError("duplicate/malformed case id")
        seen.add(case["id"])
        answer = case["expected"]
        required = {"contract", "operation", "checks", "operation_result", "values", "status", "protocol_conformance", "authentication", "independent_reproduction"}
        if type(answer) is not dict or set(answer) != required or not answer["checks"]:
            raise ValueError("incomplete expected result")
        if (answer["contract"], answer["status"], answer["protocol_conformance"], answer["authentication"], answer["independent_reproduction"]) != (CONTRACT, "UNADOPTED", "not_assessed", "not_assessed", "not_established"):
            raise ValueError("invalid expected status")
        for check in answer["checks"].values():
            if (type(check) is not dict or set(check) != {"status", "code"} or
                    check["status"] not in ("PASS", "FAIL", "UNASSESSED") or type(check["code"]) is not str):
                raise ValueError("invalid expected check")
        states = [c["status"] for c in answer["checks"].values()]
        aggregate = "FAIL" if "FAIL" in states else "UNASSESSED" if "UNASSESSED" in states else "PASS"
        if answer["operation_result"] != aggregate:
            raise ValueError("invalid expected aggregate")
        if type(answer["values"]) is not dict or any(type(v) is not str for v in answer["values"].values()):
            raise ValueError("derived values must be exact strings")
        raw_input(case)  # Also validate transport encoding.
    coverage = {c["input"].get("field") for c in cases if c["category"] == "field_coverage" and type(c.get("input")) is dict}
    if coverage != {f"N{i:03}" for i in range(1, 75)}:
        raise ValueError("incomplete 74-entry field-map coverage")
    if not OPERATIONS <= {c["expected"]["operation"] for c in cases}:
        raise ValueError("incomplete operation coverage")
    return cases


def raw_input(case):
    if "input" in case:
        return json.dumps(case["input"], ensure_ascii=True, allow_nan=False).encode("utf-8")
    if "raw_utf8" in case and type(case["raw_utf8"]) is str:
        return case["raw_utf8"].encode("utf-8")
    if "raw_hex" in case and type(case["raw_hex"]) is str:
        return bytes.fromhex(case["raw_hex"])
    raise ValueError("invalid raw transport")


def validate_manifest(manifest):
    required = {"contract", "status", "source_commit", "vector_count", "regression_count", "sources", "experiment"}
    if type(manifest) is not dict or set(manifest) != required:
        raise ValueError("invalid manifest envelope")
    if (manifest["contract"], manifest["status"], manifest["source_commit"]) != (CONTRACT, "UNADOPTED", BASE):
        raise ValueError("manifest context mismatch")
    for key in ("vector_count", "regression_count"):
        if type(manifest[key]) is not int or manifest[key] <= 0:
            raise ValueError("invalid manifest count: " + key)
    for group, expected_files in (("sources", SOURCE_FILES), ("experiment", EXPERIMENT_FILES)):
        entries = manifest[group]
        if type(entries) is not dict or set(entries) != expected_files:
            raise ValueError("incomplete/unexpected " + group + " file inventory")
        if any(type(sha) is not str or not re.fullmatch(r"[0-9a-f]{64}", sha) for sha in entries.values()):
            raise ValueError("invalid SHA-256 in " + group)


def verify_setup():
    manifest = read_json(HERE / "manifest.json")
    validate_manifest(manifest)
    for root, group in ((ROOT, "sources"), (HERE, "experiment")):
        for name, sha in manifest[group].items():
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name:
                raise ValueError("unsafe manifest path")
            if digest((root / name).read_bytes()) != sha:
                raise ValueError("SHA-256 mismatch: " + name)
    fields = checker.load_fields()
    stored = (HERE / "data/vectors.json").read_bytes()
    if stored != generate_vectors.encoded():
        raise ValueError("stored vectors differ from separately declared expectations")
    cases = validate_cases(read_json(HERE / "data/vectors.json"))
    if type(manifest["vector_count"]) is not int or len(cases) != manifest["vector_count"]:
        raise ValueError("vector count mismatch")
    return manifest, fields, cases


def evaluate(cases, fields, implementation=checker.check_bytes):
    results = []
    for case in cases:
        actual = implementation(raw_input(case), fields)
        results.append({"id": case["id"], "category": case["category"], "expected": case["expected"],
                        "actual": actual, "matched": same(actual, case["expected"])})
    return results


def regression_ok(summary, returncode, required_count):
    return (type(summary) is dict and type(required_count) is int and required_count > 0 and
            same(summary, {"tests": required_count, "failures": 0, "errors": 0, "skipped": 0,
                           "expected_failures": 0, "unexpected_successes": 0, "successful": True}) and returncode == 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New local JSON report; refuses to overwrite an existing path")
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.exit(2, "Report path already exists; choose a new filename.\n")
    try:
        manifest, fields, cases = verify_setup()
        results = evaluate(cases, fields)
        test = subprocess.run([sys.executable, str(HERE / "test_checker.py")], capture_output=True, check=False)
        summary = checker.parse_json(test.stdout)
        regressions_passed = regression_ok(summary, test.returncode, manifest["regression_count"])
        matched = sum(r["matched"] for r in results)
        report = {"contract": CONTRACT, "status": "UNADOPTED", "source_commit": BASE,
                  "independent_reproduction": "not_established", "authentication": "not_assessed",
                  "protocol_conformance": "not_assessed", "execution": "internal_synthetic_run",
                  "python": platform.python_version(), "platform": platform.system(),
                  "dependencies": "Python standard library only",
                  "manifest_sha256": digest((HERE / "manifest.json").read_bytes()),
                  "artifacts": manifest, "vector_count": len(results), "matched": matched,
                  "mismatched": len(results) - matched,
                  "expected_operation_results": dict(sorted(Counter(r["expected"]["operation_result"] for r in results).items())),
                  "categories": dict(sorted(Counter(r["category"] for r in results).items())),
                  "regressions": summary, "regression_exit_code": test.returncode,
                  "regression_stderr": test.stderr.decode("utf-8", errors="replace"),
                  "all_expectations_matched": matched == len(results) and regressions_passed,
                  "results": results}
        encoded = generate_vectors.bundle(report, "results")
        if args.output:
            with args.output.open("xb") as output:
                output.write(encoded)
        print(json.dumps({k: report[k] for k in ("vector_count", "matched", "mismatched", "expected_operation_results", "regressions", "all_expectations_matched")}, indent=2))
        return 0 if report["all_expectations_matched"] else 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"Experiment setup/execution error: {error}\n")


if __name__ == "__main__":
    sys.exit(main())
