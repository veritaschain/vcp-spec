#!/usr/bin/env python3
"""UNADOPTED numeric experiment. Not a native VCP or cryptographic verifier."""
import argparse
import hashlib
import json
import re
import sys
from datetime import date
from decimal import Decimal, DecimalException
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACT = "vcp-numeric-experiment-v0"
INVENTORY_SHA256 = "28645bbdeb1da72a2cb71a703ecc1dab2a54f4f23971b65498e921699568cc63"
FIELD_MAP_SHA256 = "8654db47dcaa97cd5095c424be5bb724a85fcceb34d9062978d227e1a5a3df63"
MAX63, MAX31 = 9223372036854775807, 2147483647
INTEGER_BOUNDS = {
    "TIME_NS": (0, MAX63), "DURATION_NS63": (0, MAX63), "SECONDS63": (0, MAX63),
    "MILLISECONDS31": (0, MAX31), "UINT63": (0, MAX63), "POS63": (1, MAX63),
    "UINT31": (0, MAX31), "POS31": (1, MAX31), "INDEX31": (0, MAX31 - 1),
}
DECIMALS = {"DEC_SIGNED", "DEC_NONNEG", "RATIO01"}
UNRESOLVED_CLASSES = {"TYPED_FEATURE", "TYPED_CONTROL", "CALENDAR", "EXTERNAL_INTEGER", "ENUM_CODE"}
INTEGER_RE = re.compile(r"(?:0|[1-9][0-9]*)", re.ASCII)
DECIMAL_RE = re.compile(r"(-?)([0-9]+)(?:\.([0-9]+))?", re.ASCII)
ISO_RE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})\.([0-9]{9})Z", re.ASCII)


class InvalidInput(ValueError):
    pass


def parse_json(raw, limit=262144):
    if len(raw) > limit:
        raise InvalidInput("input_size_limit")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeError as error:
        raise InvalidInput("invalid_utf8") from error

    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise InvalidInput("duplicate_key")
            result[key] = value
        return result

    def constant(_):
        raise InvalidInput("non_json_constant")

    try:
        # Decimal avoids binary64 rounding even for inputs later rejected as numbers.
        value = json.loads(text, object_pairs_hook=object_pairs, parse_float=Decimal,
                           parse_constant=constant)

        def unicode_scalars(item):
            if type(item) is str and any(0xD800 <= ord(c) <= 0xDFFF for c in item):
                raise InvalidInput("invalid_unicode_scalar")
            if type(item) is dict:
                for key, child in item.items():
                    unicode_scalars(key)
                    unicode_scalars(child)
            elif type(item) is list:
                for child in item:
                    unicode_scalars(child)

        unicode_scalars(value)
        return value
    except InvalidInput:
        raise
    except DecimalException as error:
        # JSON number tokens are not candidate quantity strings. Even extreme
        # exponents must yield a structured rejection, never an uncaught trap.
        raise InvalidInput("json_number_range") from error
    except (ValueError, RecursionError) as error:
        raise InvalidInput("json_syntax") from error


def load_fields():
    catalog_raw = (HERE / "data/field-map.json").read_bytes()
    if hashlib.sha256(catalog_raw).hexdigest() != FIELD_MAP_SHA256:
        raise ValueError("pinned experimental field map hash mismatch")
    catalog = parse_json(catalog_raw)
    source = ROOT / "proposals/numeric-fields-2026-10-25/inventory.json"
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != INVENTORY_SHA256 or catalog["inventory_sha256"] != INVENTORY_SHA256:
        raise ValueError("pinned PR #11 inventory hash mismatch")
    if catalog["contract"] != CONTRACT or catalog["status"] != "UNADOPTED":
        raise ValueError("field catalog contract/status mismatch")
    original = parse_json(raw)["fields"]
    expected = {(r["id"], r["path"], r["candidate_class"]) for r in original}
    actual = {(r["id"], r["path"], r["class"]) for r in catalog["fields"]}
    if expected != actual or len(catalog["fields"]) != len(expected):
        raise ValueError("field catalog coverage mismatch")
    return {r["id"]: r for r in catalog["fields"]}


def outcome(status, code):
    return {"status": status, "code": code}


def good():
    return outcome("PASS", "ok")


def unknown(code):
    return outcome("UNASSESSED", code)


def bad(code):
    return outcome("FAIL", code)


def result(operation, checks, values=None):
    statuses = {v["status"] for v in checks.values()}
    aggregate = "FAIL" if "FAIL" in statuses else "UNASSESSED" if "UNASSESSED" in statuses else "PASS"
    return {"contract": CONTRACT, "operation": operation, "checks": checks,
            "operation_result": aggregate, "values": values or {},
            "status": "UNADOPTED", "protocol_conformance": "not_assessed",
            "authentication": "not_assessed", "independent_reproduction": "not_established"}


def keys(value, required, optional=()):
    if type(value) is not dict:
        raise InvalidInput("object_required")
    if not set(required) <= value.keys():
        raise InvalidInput("missing_field")
    if value.keys() - set(required) - set(optional):
        raise InvalidInput("unknown_field")


def integer(value, kind):
    if type(value) is not str:
        return bad("string_required"), None
    if len(value) > 19:
        return bad("integer_length"), None
    if not INTEGER_RE.fullmatch(value):
        return bad("integer_lexeme"), None
    number = int(value)
    lower, upper = INTEGER_BOUNDS[kind]
    if not lower <= number <= upper:
        return bad("integer_range"), None
    return good(), number


def decimal(value, kind):
    if type(value) is not str:
        return bad("string_required"), None
    if len(value) > 40:
        return bad("decimal_length"), None
    match = DECIMAL_RE.fullmatch(value)
    if not match:
        return bad("decimal_lexeme"), None
    sign, whole, fractional = match.groups()
    fractional = fractional or ""
    if len(whole) > 20 or len(fractional) > 18:
        return bad("decimal_digits"), None
    coefficient = int(whole + fractional) * (-1 if sign else 1)
    scale = len(fractional)
    if kind != "DEC_SIGNED" and coefficient < 0:
        return bad("decimal_range"), None
    if kind == "RATIO01" and coefficient > 10 ** scale:
        return bad("decimal_range"), None
    return good(), (coefficient, scale)


def iso(value):
    if type(value) is not str:
        return bad("string_required"), None
    match = ISO_RE.fullmatch(value)
    if not match:
        return bad("iso_lexeme"), None
    year, month, day, hour, minute, second, fraction = map(int, match.groups())
    try:
        days = (date(year, month, day) - date(1970, 1, 1)).days
    except ValueError:
        return bad("iso_calendar"), None
    if hour > 23 or minute > 59 or second > 60:
        return bad("iso_clock"), None
    if second == 60:
        # This is not a statement that an actual leap second occurred on this date.
        return unknown("leap_second_mapping_unresolved"), None
    ns = ((days * 24 + hour) * 3600 + minute * 60 + second) * 1000000000 + fraction
    if not 0 <= ns <= MAX63:
        return bad("iso_range"), None
    return good(), ns


def unit(value, expected):
    if type(value) is not str:
        return bad("unit_string_required")
    if expected is None:
        return unknown("unit_policy_unresolved")
    return good() if value == expected else bad("unit_mismatch")


def passed(checks, *names):
    return all(checks[name]["status"] == "PASS" for name in names)


def scalar(request, fields):
    keys(request, ("operation", "field", "value", "unit"))
    if type(request["field"]) is not str or request["field"] not in fields:
        raise InvalidInput("unknown_field_id")
    entry = fields[request["field"]]
    kind, value = entry["class"], request["value"]
    checks = {"syntax": good(), "unit": unit(request["unit"], entry["unit"])}
    values = {}
    if kind in UNRESOLVED_CLASSES or "legacy_mapping_unresolved" in entry["unresolved"]:
        checks["representation"] = unknown("mapping_unresolved")
    else:
        if kind in INTEGER_BOUNDS:
            checks["representation"], number = integer(value, kind)
            if number is not None:
                values["exact_integer"] = str(number)
        elif kind in DECIMALS:
            checks["representation"], parts = decimal(value, kind)
            if parts is not None:
                values.update(coefficient=str(parts[0]), scale=str(parts[1]))
        elif kind == "UTC_NS":
            checks["representation"], number = iso(value)
            if number is not None:
                values["exact_ns"] = str(number)
        else:
            raise InvalidInput("unsupported_class")
        if checks["representation"]["status"] == "PASS":
            values.update(lexeme=value, utf8_hex=value.encode("utf-8").hex())
    for unresolved in entry["unresolved"]:
        checks[unresolved] = unknown(unresolved)
    return result("scalar", checks, values)


def iso_pair(request):
    keys(request, ("operation", "ns", "iso", "time_basis"))
    checks = {"syntax": good()}
    checks["integer"], ns = integer(request["ns"], "TIME_NS")
    checks["iso"], converted = iso(request["iso"])
    if type(request["time_basis"]) is not str:
        checks["time_basis"] = bad("time_basis_string_required")
    else:
        checks["time_basis"] = good() if request["time_basis"] == "unix_no_leap" else unknown("time_basis_unresolved")
    checks["equality"] = unknown("operands_unavailable")
    values = {}
    if passed(checks, "integer", "iso", "time_basis"):
        checks["equality"] = good() if ns == converted else bad("iso_integer_mismatch")
        values["iso_as_ns"] = str(converted)
    return result("iso_pair", checks, values)


def index_bound(request, fields):
    keys(request, ("operation", "field", "index", "index_unit"), ("count", "count_unit"))
    if type(request["field"]) is not str or request["field"] not in ("N017", "N043"):
        raise InvalidInput("index_field_required")
    if ("count" in request) != ("count_unit" in request):
        raise InvalidInput("incomplete_count")
    checks = {"syntax": good(), "index_unit": unit(request["index_unit"], fields[request["field"]]["unit"])}
    checks["index"], index = integer(request["index"], "INDEX31")
    checks["count"] = unknown("count_missing")
    checks["count_unit"] = unknown("count_missing")
    checks["bound"] = unknown("operands_unavailable")
    if "count" in request:
        checks["count"], count = integer(request["count"], "POS31")
        checks["count_unit"] = unit(request["count_unit"], "batch_events" if request["field"] == "N017" else "parties")
        if passed(checks, "index", "index_unit", "count", "count_unit"):
            checks["bound"] = good() if index < count else bad("index_not_below_count")
    return result("index_bound", checks)


def tolerance(request):
    keys(request, ("operation", "left_ns", "right_ns", "timestamp_unit", "tolerance", "tolerance_unit"))
    checks = {"syntax": good(), "timestamp_unit": unit(request["timestamp_unit"], "unix_ns"),
              "tolerance_unit": unit(request["tolerance_unit"], "ms")}
    checks["left"], left = integer(request["left_ns"], "TIME_NS")
    checks["right"], right = integer(request["right_ns"], "TIME_NS")
    checks["tolerance"], amount = integer(request["tolerance"], "MILLISECONDS31")
    checks["comparison"] = unknown("operands_unavailable")
    values = {}
    if passed(checks, "left", "right", "tolerance", "timestamp_unit", "tolerance_unit"):
        difference, limit = abs(left - right), amount * 1000000
        checks["comparison"] = good() if difference <= limit else bad("outside_tolerance")
        values.update(difference_ns=str(difference), tolerance_ns=str(limit))
    return result("within_tolerance", checks, values)


def duration_add(request, fields):
    keys(request, ("operation", "field", "start_ns", "start_unit", "duration", "duration_unit"))
    if type(request["field"]) is not str or request["field"] not in ("N028", "N031", "N042", "N048"):
        raise InvalidInput("duration_field_required")
    entry = fields[request["field"]]
    checks = {"syntax": good(), "start_unit": unit(request["start_unit"], "unix_ns"),
              "duration_unit": unit(request["duration_unit"], entry["unit"])}
    checks["start"], start = integer(request["start_ns"], "TIME_NS")
    checks["duration"], amount = integer(request["duration"], entry["class"])
    checks["destination"] = unknown("operands_unavailable")
    values = {}
    if passed(checks, "start", "duration", "start_unit", "duration_unit"):
        delta = amount * {"ns": 1, "ms": 1000000, "s": 1000000000}[entry["unit"]]
        total = start + delta  # Python exact integers; no wrapping intermediate.
        checks["destination"] = good() if total <= MAX63 else bad("destination_range")
        values["duration_ns"] = str(delta)
        if checks["destination"]["status"] == "PASS":
            values["end_ns"] = str(total)
    return result("duration_add", checks, values)


def sequence(request):
    keys(request, ("operation", "previous", "current"))
    for item in (request["previous"], request["current"]):
        keys(item, ("actor", "chain", "value"))
        if any(type(item[k]) is not str or not item[k] for k in ("actor", "chain")):
            raise InvalidInput("chain_identity_required")
    before, after = request["previous"], request["current"]
    checks = {"syntax": good()}
    checks["previous"], a = integer(before["value"], "UINT63")
    checks["current"], b = integer(after["value"], "UINT63")
    checks["chain"] = good() if (before["actor"], before["chain"]) == (after["actor"], after["chain"]) else unknown("different_chain")
    checks["increase"] = unknown("operands_unavailable")
    if passed(checks, "previous", "current", "chain"):
        checks["increase"] = good() if b > a else bad("not_strictly_increasing")
    return result("sequence", checks)


def check(request, fields):
    operation = None
    try:
        if type(request) is not dict:
            raise InvalidInput("object_required")
        operation = request.get("operation")
        if type(operation) is not str:
            raise InvalidInput("operation_required")
        if operation == "scalar":
            return scalar(request, fields)
        if operation == "iso_pair":
            return iso_pair(request)
        if operation == "index_bound":
            return index_bound(request, fields)
        if operation == "within_tolerance":
            return tolerance(request)
        if operation == "duration_add":
            return duration_add(request, fields)
        if operation == "sequence":
            return sequence(request)
        raise InvalidInput("unknown_operation")
    except InvalidInput as error:
        return result(operation if type(operation) is str else None, {"syntax": bad(str(error))})


def check_bytes(raw, fields):
    try:
        request = parse_json(raw)
    except InvalidInput as error:
        return result(None, {"syntax": bad(str(error))})
    return check(request, fields)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Research request JSON; not a VCP event")
    args = parser.parse_args()
    try:
        with args.input.open("rb") as source:
            raw = source.read(262145)  # Bound memory before parsing; one byte detects oversize.
        output = check_bytes(raw, load_fields())
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f"experiment setup error: {error}\n")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return {"PASS": 0, "FAIL": 1, "UNASSESSED": 2}[output["operation_result"]]


if __name__ == "__main__":
    sys.exit(main())
