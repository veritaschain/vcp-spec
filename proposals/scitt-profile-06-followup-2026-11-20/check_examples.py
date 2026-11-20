#!/usr/bin/env python3
"""Check documentation clocks only, not hashes, signatures, receipts or conformance."""

import calendar
import json
import re
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def iso_ns(value):
    match = re.fullmatch(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?Z", value)
    if match is None:
        raise ValueError("expected UTC ISO timestamp with at most nine fractional digits")
    seconds = calendar.timegm(datetime.strptime(match[1], "%Y-%m-%dT%H:%M:%S").timetuple())
    return seconds * 1_000_000_000 + int((match[2] or "").ljust(9, "0"))


def check_clock(event):
    errors = []
    header = event["Header"]
    ns = header["TimestampInt"]
    if type(ns) is not int:
        return ["TIMESTAMP_NOT_INTEGER"]
    if iso_ns(header["TimestampISO"]) != ns:
        errors.append("ISO_INTEGER_MISMATCH")
    identity = uuid.UUID(header["EventID"])
    if identity.version != 7 or identity.variant != uuid.RFC_4122:
        errors.append("UUID_NOT_V7")
    elif identity.int >> 80 != ns // 1_000_000:
        errors.append("UUID_INTEGER_MISMATCH")
    if header.get("EventType") == "ERASURE":
        details = event["Payload"]["VCP-PRIVACY"]["ErasureDetails"]
        auth = details["Authorization"]["AuthorizationTimestamp"]
        destruction = details["CryptoShredding"]["DestructionTimestamp"]
        if type(auth) is not int or type(destruction) is not int:
            errors.append("ERASURE_TIMESTAMP_NOT_INTEGER")
        elif not auth <= destruction <= ns:
            errors.append("ERASURE_TIME_ORDER")
    return errors


def main():
    errors = []
    for path in sorted((ROOT / "examples").glob("*.json")):
        for error in check_clock(json.loads(path.read_text())):
            errors.append(path.name + ": " + error)
    if errors:
        raise SystemExit("\n".join(errors))
    print("Three illustrative examples have consistent ISO/integer/UUID clocks; this is not cryptographic verification.")


if __name__ == "__main__":
    main()
