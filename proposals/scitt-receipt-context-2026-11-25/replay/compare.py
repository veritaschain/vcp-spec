"""Compare both replays, the expected outcomes, and the recorded transcripts."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_bytes())


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("python_report", type=Path)
    parser.add_argument("go_report", type=Path)
    args = parser.parse_args()
    report = read(args.python_report)
    require(report == read(args.go_report), "Python and Go reports differ")
    require(report["cases"] == read(HERE / "expected.json")["cases"], "Case oracle mismatch")

    historical = report["details"]["CX-09"]["K1"]
    reissued = report["details"]["CX-19"]
    require(historical["key_status"] == "retired", "Historical K1 status missing")
    require(reissued["K2"]["key_status"] == "current", "Reissued K2 status missing")
    require(reissued["K1"]["key_epoch"] != reissued["K2"]["key_epoch"], "Expected different key epochs")
    assert_scope = ("history_consistency", "source_completeness", "issuance_time",
                    "position_and_size", "local_vcp_batch_integrity")
    require(all(report[item] == "unassessed" for item in assert_scope), "Inclusion claim scope changed")
    require(report["details"]["CX-17"]["K1"]["claim"] == "inclusion under service-signed root",
            "Expected an inclusion-only claim")
    for name in ("python", "go"):
        require(report == read(HERE / "results" / (name + ".json")), f"{name} transcript changed")
    count = sum(len(assessments) for assessments in report["cases"].values())
    print(f"{len(report['cases'])} cases, {count} receipt assessments: both replays and recorded outputs agree")


if __name__ == "__main__":
    main()
