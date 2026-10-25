"""Run the closed synthetic suite and regressions; retain actual byte traces."""
import argparse
import collections
import io
import platform
import re
import unittest
from pathlib import Path

import common as m
import checker
import fixtures

CASE_COUNT = 45
REGRESSION_COUNT = 20
FILES = {"common.py", "checker.py", "fixtures.py", "run.py", "test_regressions.py",
         "crosscheck.cjs", "README.md", "requirements.txt", "sources.json", "data/cases.json"}


def manifest_check(root=m.HERE):
    data = m.strict_json((root / "manifest.json").read_bytes())
    if (type(data) is not dict or set(data) != {"experiment", "status", "case_count", "regression_count", "files"}
            or data["experiment"] != m.EXPERIMENT or data["status"] != "UNADOPTED"
            or type(data["case_count"]) is not int or data["case_count"] != CASE_COUNT
            or type(data["regression_count"]) is not int or data["regression_count"] != REGRESSION_COUNT
            or type(data["files"]) is not dict or set(data["files"]) != FILES):
        raise ValueError("experiment manifest closed inventory/count mismatch")
    for name, digest in data["files"].items():
        if type(digest) is not str or not re.fullmatch("[0-9a-f]{64}", digest) or m.sha((root / name).read_bytes()) != digest:
            raise ValueError("experiment file hash mismatch: " + name)
    return data


def validate_cases(data):
    original = fixtures.build()
    # Includes the manually declared expectations and PUBLIC test keys. Evidence
    # cannot replace the caller-owned trust map or remove/duplicate a case.
    if not m.same(data, original) or len(data["cases"]) != CASE_COUNT:
        raise ValueError("case set differs from declared synthetic suite")
    ids = [c["id"] for c in data["cases"]]
    if len(set(ids)) != CASE_COUNT:
        raise ValueError("duplicate case")
    for case in data["cases"]:
        if (set(case) != {"id", "reference", "note", "bundle", "expected"}
                or case["reference"] not in ids
                or set(case["expected"]) != {"checks", "covered_checks_result", "relations"}
                or set(case["expected"]["checks"]) != checker.CHECKS
                or set(case["expected"]["relations"]) != checker.RELATIONS):
            raise ValueError("incomplete case expectations")


def run_cases(data):
    validate_cases(data)
    actual = {c["id"]: checker.evaluate(c["bundle"]) for c in data["cases"]}
    rows, mismatches = [], []
    for case in data["cases"]:
        result = actual[case["id"]]
        relation = checker.relations(result, actual[case["reference"]])
        observed = {"checks": result["checks"], "covered_checks_result": result["covered_checks_result"], "relations": relation}
        matched = m.same(observed, case["expected"])
        if not matched:
            mismatches.append(case["id"])
        rows.append({"id": case["id"], "reference": case["reference"], "expected": case["expected"],
                     "matched": matched, "actual": result, "relations": relation})
    return rows, mismatches


def regressions_ok(result):
    return (result.testsRun == REGRESSION_COUNT and result.wasSuccessful()
            and not result.skipped and not result.expectedFailures and not result.unexpectedSuccesses)


def run_regressions():
    import test_regressions
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_regressions)
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    return {"expected_count": REGRESSION_COUNT, "tests_run": result.testsRun,
            "success_without_skips_or_expected_failures": bool(regressions_ok(result)), "output": log.getvalue()}


def execute():
    manifest = manifest_check()
    raw = (m.HERE / "data/cases.json").read_bytes()
    if raw != fixtures.encoded():
        raise ValueError("stored fixture bytes differ from deterministic generation")
    data = m.strict_json(raw)
    rows, mismatches = run_cases(data)
    regression = run_regressions()
    counts = dict(collections.Counter(r["actual"]["covered_checks_result"] for r in rows))
    success = len(rows) == CASE_COUNT and not mismatches and regression["success_without_skips_or_expected_failures"]
    return {"experiment": m.EXPERIMENT, "status": "UNADOPTED", "source_commit": m.BASE,
            "independent_reproduction": "not_established", "native_vcp_conformance": "not_assessed",
            "runtime": {"python": platform.python_version(), "platform": platform.platform(), "dependencies": m.DEPENDENCIES},
            "source_files": m.SOURCE_MANIFEST["files"], "experiment_files": manifest["files"],
            "manifest_sha256": m.sha((m.HERE / "manifest.json").read_bytes()),
            "summary": {"case_count": len(rows), "covered_checks_counts": counts, "mismatches": mismatches,
                        "all_expected_results_matched_and_regressions_passed": success},
            "regressions": regression, "cases": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New local output file; existing files are never overwritten")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists; use a separate execution record")
    result = execute()
    # Exclusive creation also handles a race with another invocation.
    with args.output.open("xb") as stream:
        stream.write(m.bundle_bytes(result, "cases"))
    print(result["summary"])
    print(f"Regressions: {result['regressions']['tests_run']}; output: {args.output}")
    return 0 if result["summary"]["all_expected_results_matched_and_regressions_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
