#!/usr/bin/env python3
"""Declare synthetic inputs and expectations; never import or run the checker.

Validity/error decisions and ISO epoch answers below are explicit review data.
Helpers only serialize expectations and compute exact elementary integer values.
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTRACT = "vcp-numeric-experiment-v0"
P = {"status": "PASS", "code": "ok"}


def F(code):
    return {"status": "FAIL", "code": code}


def U(code):
    return {"status": "UNASSESSED", "code": code}


def expected(op, checks, values=None):
    states = [c["status"] for c in checks.values()]
    return {"contract": CONTRACT, "operation": op, "checks": checks,
            "operation_result": "FAIL" if "FAIL" in states else "UNASSESSED" if "UNASSESSED" in states else "PASS",
            "values": values or {}, "status": "UNADOPTED",
            "protocol_conformance": "not_assessed", "authentication": "not_assessed",
            "independent_reproduction": "not_established"}


def build():
    fields = {f["id"]: f for f in json.loads((HERE / "data/field-map.json").read_text())["fields"]}
    cases = []

    def add(name, category, request, answer, note=""):
        cases.append({"id": name, "category": category, "input": request,
                      "expected": answer, "note": note})

    def scalar(name, field, value, representation=P, unit_check=None, category="scalar", numeric=None, sent_unit=None):
        f = fields[field]
        request_unit = f["unit"] if f["unit"] is not None else "policy-not-bound"
        if sent_unit is not None:
            request_unit = sent_unit
        checks = {"syntax": P, "unit": unit_check or (P if f["unit"] is not None else U("unit_policy_unresolved")),
                  "representation": representation}
        checks.update({key: U(key) for key in f["unresolved"]})
        values = {}
        if representation == P:
            if f["class"] in ("DEC_SIGNED", "DEC_NONNEG", "RATIO01"):
                whole, _, frac = value.partition(".")
                values = {"coefficient": str(int(whole + frac)), "scale": str(len(frac))}
            elif f["class"] == "UTC_NS":
                assert numeric is not None
                values["exact_ns"] = numeric
            else:
                values["exact_integer"] = value
            values.update(lexeme=value, utf8_hex=value.encode("utf-8").hex())
        add(name, category, {"operation": "scalar", "field": field, "value": value, "unit": request_unit},
            expected("scalar", checks, values))

    # One declared mapping exercise for all 74 inventory entries, including the
    # explicitly unsupported contexts. This is NOT 74 native-schema validations.
    unresolved = {"TYPED_FEATURE", "TYPED_CONTROL", "CALENDAR", "EXTERNAL_INTEGER", "ENUM_CODE"}
    for fid, f in fields.items():
        kind = f["class"]
        if kind in unresolved or fid == "N073":
            value = {"TYPED_FEATURE": "category-A", "TYPED_CONTROL": "enabled",
                     "CALENDAR": "P1Y", "EXTERNAL_INTEGER": 8, "ENUM_CODE": 10}.get(kind, 1735128000)
            scalar("field-" + fid, fid, value, U("mapping_unresolved"), category="field_coverage")
        elif kind == "UTC_NS":
            scalar("field-" + fid, fid, "1970-01-01T00:00:00.000000000Z", category="field_coverage", numeric="0")
        elif kind in ("DEC_SIGNED", "DEC_NONNEG", "RATIO01"):
            scalar("field-" + fid, fid, "0.5", category="field_coverage")
        else:
            scalar("field-" + fid, fid, "1", category="field_coverage")

    # Independent table transcribed from PR #11, not from checker constants.
    integers = [
        ("TIME_NS", "N004", 0, 9223372036854775807),
        ("DURATION_NS63", "N048", 0, 9223372036854775807),
        ("SECONDS63", "N028", 0, 9223372036854775807),
        ("MILLISECONDS31", "N042", 0, 2147483647),
        ("UINT63", "N003", 0, 9223372036854775807),
        ("POS63", "N013", 1, 9223372036854775807),
        ("UINT31", "N038", 0, 2147483647),
        ("POS31", "N037", 1, 2147483647),
        ("INDEX31", "N017", 0, 2147483646),
    ]
    invalid_integer = [
        ("negative", "-1", "integer_lexeme"), ("negative-zero", "-0", "integer_lexeme"),
        ("plus", "+1", "integer_lexeme"), ("leading-zero", "01", "integer_lexeme"),
        ("decimal", "1.0", "integer_lexeme"), ("exponent", "1e3", "integer_lexeme"),
        ("empty", "", "integer_lexeme"), ("space", " 1", "integer_lexeme"),
        ("newline", "1\n", "integer_lexeme"), ("arabic-digit", "١", "integer_lexeme"),
        ("fullwidth", "１", "integer_lexeme"), ("unicode-minus", "−1", "integer_lexeme"),
        ("number", 1, "string_required"), ("float", 1.0, "string_required"),
        ("true", True, "string_required"), ("false", False, "string_required"),
        ("null", None, "string_required"), ("array", [], "string_required"),
        ("object", {}, "string_required"), ("20digits", "18446744073709551615", "integer_length"),
    ]
    for kind, fid, lower, upper in integers:
        for label, value in (("min", lower), ("max", upper), ("above-max", upper + 1)):
            scalar(kind + "-" + label, fid, str(value), P if value <= upper else F("integer_range"), category="integer_boundary")
        scalar(kind + "-below-min", fid, str(lower - 1), F("integer_range" if lower else "integer_lexeme"), category="integer_boundary")
        for label, value, error in invalid_integer:
            scalar(kind + "-" + label, fid, value, F(error), category="integer_invalid")
        scalar(kind + "-wrong-unit", fid, "1", unit_check=F("unit_mismatch"), sent_unit="wrong", category="unit")
    for value in (9007199254740991, 9007199254740992, 9007199254740993):
        scalar("exact-string-" + str(value), "N004", str(value), category="exactness")
        scalar("json-number-" + str(value), "N004", value, F("string_required"), category="exactness")

    valid_decimals = ["0", "-0", "-0.000", "1", "1.0", "01.00", "000.5000", "0.000000000000000001"]
    invalid_decimals = [
        ("empty", "", "decimal_lexeme"), ("plus", "+1", "decimal_lexeme"),
        ("exponent", "1e0", "decimal_lexeme"), ("nan", "NaN", "decimal_lexeme"),
        ("infinity", "Infinity", "decimal_lexeme"), ("space", "1 ", "decimal_lexeme"),
        ("no-whole", ".5", "decimal_lexeme"), ("no-frac", "1.", "decimal_lexeme"),
        ("comma", "1,0", "decimal_lexeme"), ("unicode", "１.０", "decimal_lexeme"),
        ("whole21", "100000000000000000000", "decimal_digits"),
        ("frac19", "0.0000000000000000001", "decimal_digits"),
        ("long", "0" * 41, "decimal_length"), ("bool", True, "string_required"),
        ("number", 0.5, "string_required"), ("null", None, "string_required"),
    ]
    for kind, fid in (("DEC_SIGNED", "N005"), ("DEC_NONNEG", "N006"), ("RATIO01", "N012")):
        for i, value in enumerate(valid_decimals):
            scalar(kind + "-lexeme-" + str(i), fid, value, category="decimal_lexical_bytes")
        for label, value, error in invalid_decimals:
            scalar(kind + "-" + label, fid, value, F(error), category="decimal_invalid")
        scalar(kind + "-tiny-negative", fid, "-0.000000000000000001", P if kind == "DEC_SIGNED" else F("decimal_range"), category="decimal_boundary")
        scalar(kind + "-above-one", fid, "1.000000000000000001", F("decimal_range") if kind == "RATIO01" else P, category="decimal_boundary")
        scalar(kind + "-max-envelope", fid, "99999999999999999999.999999999999999999", F("decimal_range") if kind == "RATIO01" else P, category="decimal_boundary")
    scalar("signed-min-envelope", "N005", "-99999999999999999999.999999999999999999", category="decimal_boundary")
    scalar("utilization-over-one", "N063", "1.25", category="policy_unknown")
    scalar("latency-fractional-us", "N058", "0.001", category="unit")
    scalar("latency-mislabeled-ns", "N058", "0.001", unit_check=F("unit_mismatch"), sent_unit="ns", category="unit")
    scalar("throttle-fractional", "N066", "0.5", category="unit")
    scalar("confidence-not-percent", "N012", "0.5", unit_check=F("unit_mismatch"), sent_unit="percent", category="unit")
    scalar("unknown-unit-no-guess", "N005", "1", sent_unit="USD", category="policy_unknown")
    scalar("unit-json-number", "N004", "1", unit_check=F("unit_string_required"), sent_unit=1, category="unit")
    scalar("legacy-wrong-unit-still-fails", "N073", "1", U("mapping_unresolved"),
           unit_check=F("unit_mismatch"), sent_unit="seconds", category="aggregation")

    def pair(name, ns, iso, iso_result=P, int_result=P, equality=P, value=None, basis="unix_no_leap", basis_result=P):
        add(name, "iso_pair", {"operation": "iso_pair", "ns": ns, "iso": iso, "time_basis": basis},
            expected("iso_pair", {"syntax": P, "integer": int_result, "iso": iso_result,
                                   "time_basis": basis_result, "equality": equality},
                     {"iso_as_ns": value if value is not None else ns} if equality != U("operands_unavailable") else {}))
    iso_anchors = [
        ("epoch", "0", "1970-01-01T00:00:00.000000000Z"),
        ("one-ns", "1", "1970-01-01T00:00:00.000000001Z"),
        ("leap2000", "951782400000000000", "2000-02-29T00:00:00.000000000Z"),
        ("nonleap2100", "4107542400000000000", "2100-03-01T00:00:00.000000000Z"),
        ("body-example-2024", "1735128000123456789", "2024-12-25T12:00:00.123456789Z"),
        ("max", "9223372036854775807", "2262-04-11T23:47:16.854775807Z"),
    ]
    for label, ns, text in iso_anchors:
        pair("iso-" + label, ns, text)
    pair("iso-one-ns-mismatch", "0", iso_anchors[1][2], equality=F("iso_integer_mismatch"), value="1")
    pair("iso-body-year-mismatch", "1735128000123456789", "2025-12-25T12:00:00.123456789Z",
         equality=F("iso_integer_mismatch"), value="1766664000123456789")
    invalid_iso = [
        ("before-epoch", "1969-12-31T23:59:59.999999999Z", "iso_range"),
        ("above-max", "2262-04-11T23:47:16.854775808Z", "iso_range"),
        ("2100-feb29", "2100-02-29T00:00:00.000000000Z", "iso_calendar"),
        ("year-zero", "0000-01-01T00:00:00.000000000Z", "iso_calendar"),
        ("month13", "2024-13-01T00:00:00.000000000Z", "iso_calendar"),
        ("day-zero", "2024-01-00T00:00:00.000000000Z", "iso_calendar"),
        ("april31", "2024-04-31T00:00:00.000000000Z", "iso_calendar"),
        ("hour24", "2024-01-01T24:00:00.000000000Z", "iso_clock"),
        ("minute60", "2024-01-01T00:60:00.000000000Z", "iso_clock"),
        ("second61", "2024-01-01T00:00:61.000000000Z", "iso_clock"),
        ("offset", "1970-01-01T00:00:00.000000000+00:00", "iso_lexeme"),
        ("lowercase", "1970-01-01t00:00:00.000000000z", "iso_lexeme"),
        ("millis", "1970-01-01T00:00:00.000Z", "iso_lexeme"),
        ("no-fraction", "1970-01-01T00:00:00Z", "iso_lexeme"),
        ("10digits", "1970-01-01T00:00:00.0000000000Z", "iso_lexeme"),
        ("newline", "1970-01-01T00:00:00.000000000Z\n", "iso_lexeme"),
        ("not-string", None, "string_required"),
    ]
    for label, text, error in invalid_iso:
        pair("iso-" + label, "0", text, iso_result=F(error), equality=U("operands_unavailable"))
    pair("iso-leap-unmapped", "1483228800000000000", "2016-12-31T23:59:60.000000000Z",
         iso_result=U("leap_second_mapping_unresolved"), equality=U("operands_unavailable"))
    pair("iso-failure-over-unknown", False, "2016-12-31T23:59:60.000000000Z",
         iso_result=U("leap_second_mapping_unresolved"), int_result=F("string_required"), equality=U("operands_unavailable"))
    for basis in ("smear", "negative_leap_adjusted", "unknown"):
        pair("iso-basis-" + basis, "0", iso_anchors[0][2], basis=basis,
             basis_result=U("time_basis_unresolved"), equality=U("operands_unavailable"))
    pair("iso-basis-not-string", "0", iso_anchors[0][2], basis=False,
         basis_result=F("time_basis_string_required"), equality=U("operands_unavailable"))
    pair("iso-integer-overflow", "9223372036854775808", iso_anchors[5][2],
         int_result=F("integer_range"), equality=U("operands_unavailable"))
    scalar("scheduled-does-not-invent-pair", "N020", iso_anchors[0][2], category="iso_pair", numeric="0")

    for fid, index_unit, count_unit in (("N017", "leaf_index", "batch_events"), ("N043", "party_index", "parties")):
        for label, i, n, bound in (("first", "0", "1", P), ("last", "2147483646", "2147483647", P),
                                    ("equal", "1", "1", F("index_not_below_count")), ("greater", "2", "1", F("index_not_below_count"))):
            add(fid + "-index-" + label, "index_count", {"operation": "index_bound", "field": fid,
                "index": i, "index_unit": index_unit, "count": n, "count_unit": count_unit},
                expected("index_bound", {"syntax": P, "index_unit": P, "index": P, "count": P, "count_unit": P, "bound": bound}))
        add(fid + "-index-count-missing", "index_count", {"operation": "index_bound", "field": fid, "index": "0", "index_unit": index_unit},
            expected("index_bound", {"syntax": P, "index_unit": P, "index": P, "count": U("count_missing"),
                "count_unit": U("count_missing"), "bound": U("operands_unavailable")}))
        for label, n, error in (("zero", "0", "integer_range"), ("overflow", "2147483648", "integer_range"), ("bool", True, "string_required")):
            add(fid + "-count-" + label, "index_count", {"operation": "index_bound", "field": fid, "index": "0", "index_unit": index_unit, "count": n, "count_unit": count_unit},
                expected("index_bound", {"syntax": P, "index_unit": P, "index": P, "count": F(error), "count_unit": P, "bound": U("operands_unavailable")}))

    def tol(label, left, right, amount, verdict, limit, diff):
        add("tolerance-" + label, "tolerance", {"operation": "within_tolerance", "left_ns": left, "right_ns": right,
            "timestamp_unit": "unix_ns", "tolerance": amount, "tolerance_unit": "ms"},
            expected("within_tolerance", {"syntax": P, "timestamp_unit": P, "tolerance_unit": P, "left": P,
                "right": P, "tolerance": P, "comparison": verdict}, {"difference_ns": diff, "tolerance_ns": limit}))
    tol("equal-zero", "1", "1", "0", P, "0", "0")
    tol("one-ns-outside-zero", "1", "0", "0", F("outside_tolerance"), "0", "1")
    tol("edge", "1000000", "0", "1", P, "1000000", "1000000")
    tol("one-ns-outside", "1000001", "0", "1", F("outside_tolerance"), "1000000", "1000001")
    tol("symmetric", "0", "1000000", "1", P, "1000000", "1000000")
    tol("max-unit-conversion", "2147483647000000", "0", "2147483647", P, "2147483647000000", "2147483647000000")
    tol("max-time-difference", "9223372036854775807", "0", "2147483647", F("outside_tolerance"), "2147483647000000", "9223372036854775807")
    tol("above-binary64", "9007199254740993", "9007199254740992", "0", F("outside_tolerance"), "0", "1")

    for fid, units, delta in (("N028", "s", 1000000000), ("N031", "s", 1000000000), ("N042", "ms", 1000000), ("N048", "ns", 1)):
        for label, start, duration, destination, values in (
            ("one", "0", "1", P, {"duration_ns": str(delta), "end_ns": str(delta)}),
            ("zero-at-max", "9223372036854775807", "0", P, {"duration_ns": "0", "end_ns": "9223372036854775807"}),
            ("exact-max", str(9223372036854775807 - delta), "1", P, {"duration_ns": str(delta), "end_ns": "9223372036854775807"}),
            ("overflow", str(9223372036854775808 - delta), "1", F("destination_range"), {"duration_ns": str(delta)}),
        ):
            add(fid + "-add-" + label, "duration", {"operation": "duration_add", "field": fid, "start_ns": start,
                "start_unit": "unix_ns", "duration": duration, "duration_unit": units},
                expected("duration_add", {"syntax": P, "start_unit": P, "duration_unit": P, "start": P,
                    "duration": P, "destination": destination}, values))
    add("seconds-exact-intermediate-overflow", "duration", {"operation": "duration_add", "field": "N028", "start_ns": "0",
        "start_unit": "unix_ns", "duration": "9223372036854775807", "duration_unit": "s"},
        expected("duration_add", {"syntax": P, "start_unit": P, "duration_unit": P, "start": P, "duration": P,
            "destination": F("destination_range")}, {"duration_ns": "9223372036854775807000000000"}))

    for label, a, b, verdict, actor, chain in (
        ("first", "0", "1", P, "a", "c"), ("gap", "1", "100", P, "a", "c"),
        ("last", "9223372036854775806", "9223372036854775807", P, "a", "c"),
        ("equal", "1", "1", F("not_strictly_increasing"), "a", "c"),
        ("decrease", "2", "1", F("not_strictly_increasing"), "a", "c"),
        ("no-wrap", "9223372036854775807", "0", F("not_strictly_increasing"), "a", "c"),
        ("actor-change", "1", "0", U("operands_unavailable"), "b", "c"),
        ("chain-change", "1", "0", U("operands_unavailable"), "a", "d"),
    ):
        add("sequence-" + label, "sequence", {"operation": "sequence", "previous": {"actor": "a", "chain": "c", "value": a},
            "current": {"actor": actor, "chain": chain, "value": b}},
            expected("sequence", {"syntax": P, "previous": P, "current": P,
                "chain": P if (actor, chain) == ("a", "c") else U("different_chain"), "increase": verdict}))

    # Cross-operation unit and envelope mutations carry explicitly declared
    # effects. Their expected outcomes are not generated by the implementation.
    base_cases = {c["id"]: c for c in cases}
    mutations = [
        ("N017-index-first", "count_unit", "parties", "count_unit", "bound"),
        ("N043-index-first", "index_unit", "leaf_index", "index_unit", "bound"),
        ("tolerance-edge", "tolerance_unit", "s", "tolerance_unit", "comparison"),
        ("tolerance-edge", "timestamp_unit", "unix_ms", "timestamp_unit", "comparison"),
        ("N028-add-one", "duration_unit", "ns", "duration_unit", "destination"),
        ("N048-add-one", "duration_unit", "s", "duration_unit", "destination"),
        ("N042-add-one", "start_unit", "unix_ms", "start_unit", "destination"),
    ]
    for source_id, key, value, failing_check, blocked_check in mutations:
        original = base_cases[source_id]
        request = dict(original["input"], **{key: value})
        checks = dict(original["expected"]["checks"], **{failing_check: F("unit_mismatch"), blocked_check: U("operands_unavailable")})
        add(source_id + "-bad-" + key, "unit", request, expected(request["operation"], checks))
    for source_id in ("TIME_NS-min", "iso-epoch", "N017-index-first", "tolerance-edge", "N028-add-one", "sequence-first"):
        request = dict(base_cases[source_id]["input"])
        for key in sorted(request):
            truncated = {k: v for k, v in request.items() if k != key}
            op = request["operation"] if key != "operation" else None
            code = "operation_required" if key == "operation" else "incomplete_count" if key in ("count", "count_unit") else "missing_field"
            add(source_id + "-missing-" + key, "envelope", truncated, expected(op, {"syntax": F(code)}))
        add(source_id + "-untrusted-flag", "envelope", dict(request, signature_valid=True), expected(request["operation"], {"syntax": F("unknown_field")}))

    for name, request, operation, code in (
        ("root-array", [], None, "object_required"), ("root-null", None, None, "object_required"),
        ("unknown-operation", {"operation": "native-vcp"}, "native-vcp", "unknown_operation"),
        ("operation-object", {"operation": {}}, None, "operation_required"),
        ("unknown-field", {"operation": "scalar", "field": "N999", "value": "1", "unit": "ns"}, "scalar", "unknown_field_id"),
    ):
        add(name, "envelope", request, expected(operation, {"syntax": F(code)}))
    raw_cases = [
        ("duplicate-value", '{"operation":"scalar","field":"N004","value":"1","value":true,"unit":"unix_ns"}', "duplicate_key"),
        ("nested-duplicate", '{"operation":"sequence","previous":{"actor":"a","actor":"b"}}', "duplicate_key"),
        ("nonfinite-nan", '{"value":NaN}', "non_json_constant"),
        ("nonfinite-infinity", '{"value":Infinity}', "non_json_constant"),
        ("trailing-data", '{} {}', "json_syntax"),
        ("bom", '\ufeff{}', "json_syntax"),
        ("lone-surrogate", '{"operation":"\\ud800"}', "invalid_unicode_scalar"),
        ("surrogate-key", '{"\\ud800":1}', "invalid_unicode_scalar"),
    ]
    for name, raw, code in raw_cases:
        cases.append({"id": name, "category": "json_wire", "raw_utf8": raw,
                      "expected": expected(None, {"syntax": F(code)}), "note": "Strict research JSON input."})
    cases.append({"id": "invalid-utf8", "category": "json_wire", "raw_hex": "fffe7b7d",
                  "expected": expected(None, {"syntax": F("invalid_utf8")}), "note": "Not UTF-8."})
    # Keep deliberately invalid JSON floating-number tokens as raw wire input.
    # The fixture loader must not round or reserialize them on the way in.
    def has_float(value):
        if type(value) is float:
            return True
        if type(value) is dict:
            return any(has_float(v) for v in value.values())
        if type(value) is list:
            return any(has_float(v) for v in value)
        return False
    for case in cases:
        if "input" in case and has_float(case["input"]):
            case["raw_utf8"] = json.dumps(case.pop("input"), ensure_ascii=True, allow_nan=False)
    assert len({c["id"] for c in cases}) == len(cases)
    return {"contract": CONTRACT, "status": "UNADOPTED", "independent_reproduction": "not_established", "cases": cases}


def bundle(data, list_key):
    """Valid JSON with one complete case/result per line for reviewable diffs."""
    metadata = {k: v for k, v in data.items() if k != list_key}
    prefix = json.dumps(metadata, ensure_ascii=True, indent=2)[:-2]
    rows = ",\n".join("    " + json.dumps(row, ensure_ascii=True, separators=(",", ":")) for row in data[list_key])
    return (prefix + ',\n  "' + list_key + '": [\n' + rows + '\n  ]\n}\n').encode("utf-8")


def encoded():
    return bundle(build(), "cases")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write only the new experiment's vectors.json")
    args = parser.parse_args()
    target = HERE / "data/vectors.json"
    raw = encoded()
    if args.write:
        target.write_bytes(raw)
    elif not target.exists() or target.read_bytes() != raw:
        parser.exit(1, "Stored vectors differ from the declared expectations.\n")
    print(f"Declared vectors: {len(build()['cases'])}; {'written' if args.write else 'match stored bytes'}")


if __name__ == "__main__":
    main()
