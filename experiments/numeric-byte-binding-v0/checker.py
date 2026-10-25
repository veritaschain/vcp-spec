"""Synthetic composition checks. Numeric validity never follows from a signature."""
import json
import re

import rfc8785
import common as m

CHECKS = {"event_parse", "event_shape", "event_statement_shape", "anchor_shape", "numeric", "policy_binding",
          "policy_interpretation", "event_crypto", "event_test_trust", "event_binding",
          "anchor_crypto", "anchor_test_trust", "batch_binding", "external_binding",
          "event_signature_encoding", "anchor_signature_encoding"}
RELATIONS = {"event_hash", "leaf_hash", "root_hash", "event_signature_message_hash",
             "event_signature", "anchor_signature_message_hash", "anchor_signature",
             "external_commitment", "policy_digest", "diagnostic_jcs_hash"}
ENVELOPE = {"event_json", "event_statement", "event_signature", "anchor_statement",
            "anchor_signature", "policy_hex", "external_commitment", "transport"}


def aggregate(states):
    if not states or any(s not in ("PASS", "FAIL", "UNASSESSED") for s in states):
        raise ValueError("invalid check states")
    return "FAIL" if "FAIL" in states else "UNASSESSED" if "UNASSESSED" in states else "PASS"


def request(data):
    return m.numeric.check_bytes(json.dumps(data, ensure_ascii=True).encode(), m.FIELDS)


def numeric_checks(event, anchor):
    try:
        payload = event["Payload"]
        m.byte.exact(payload, "ExperimentID PolicyDigest NumericEvidence")
        m.byte.require(payload["ExperimentID"] == m.EXPERIMENT, "numeric experiment ID")
        evidence = payload["NumericEvidence"]
        m.byte.exact(evidence, "TimestampISO TimeBasis TimestampUnit Duration Tolerance Confidence")
        for name in ("Duration", "Tolerance", "Confidence"):
            m.byte.exact(evidence[name], "Value Unit")
        unit = m.numeric.unit(evidence["TimestampUnit"], "unix_ns")
        calls = {
            "timestamp_pair": request({"operation": "iso_pair", "ns": event["Header"]["TimestampInt"],
                "iso": evidence["TimestampISO"], "time_basis": evidence["TimeBasis"]}),
            "anchor_count": request({"operation": "scalar", "field": "N037", "value": anchor["EventCount"], "unit": "batch_events"}),
            # Explicit research mapping only: old candidate RecordedAtNs -> TIME_NS.
            "anchor_time": request({"operation": "scalar", "field": "N036", "value": anchor["RecordedAtNs"], "unit": "unix_ns"}),
        }
        for name, field in (("Duration", "N028"), ("Tolerance", "N042"), ("Confidence", "N012")):
            calls[name] = request({"operation": "scalar", "field": field, "value": evidence[name]["Value"], "unit": evidence[name]["Unit"]})
        return aggregate([unit["status"]] + [v["operation_result"] for v in calls.values()]), {"timestamp_unit": unit, "calls": calls}
    except (m.byte.Rejected, KeyError, TypeError, ValueError) as error:
        return "FAIL", {"shape_error": str(error)}


def evaluate(bundle):
    if type(bundle) is not dict or set(bundle) != ENVELOPE or type(bundle["transport"]) is not dict:
        raise ValueError("closed synthetic bundle required")
    checks, details, trace = {}, {}, {}
    event = None
    try:
        if type(bundle["event_json"]) is not str:
            raise ValueError("event_json must be UTF-8 text")
        event = m.numeric.parse_json(bundle["event_json"].encode())
        checks["event_parse"] = "PASS"
    except (ValueError, UnicodeError) as error:
        checks["event_parse"] = "FAIL"
        details["event_parse"] = str(error)

    def attempted(name, fn):
        try:
            value = fn()
            checks[name] = "PASS"
            return value
        except (m.byte.Rejected, ValueError, TypeError, KeyError) as error:
            checks[name] = "FAIL"
            details[name] = str(error)
            return None

    event_input = attempted("event_shape", lambda: m.byte.event_preimage(event))
    anchor = bundle["anchor_statement"]
    attempted("anchor_shape", lambda: m.byte.anchor_validate(anchor))
    checks["numeric"], details["numeric"] = numeric_checks(event, anchor)
    if event_input is not None:
        trace["event_preimage_hex"] = event_input.hex()
        trace["event_jcs_hex"] = m.byte.jcs(event).hex()
        trace["event_hash"] = m.byte.digest_text(event_input)
        digest = m.byte.digest_bytes(trace["event_hash"])
        trace["leaf_hash"] = "sha256:" + m.byte.sha(b"\x00" + digest).hex()
        trace["root_hash"] = "sha256:" + m.byte.tree([digest]).hex()
    # Explicitly non-candidate diagnostic. No EventHash is defined for rejected
    # candidate shapes/numbers merely because generic JCS can serialize them.
    if checks["event_parse"] == "PASS":
        try:
            diagnostic = rfc8785.dumps(event)
            trace["diagnostic_jcs_hex"] = diagnostic.hex()
            trace["diagnostic_jcs_hash"] = m.sha(diagnostic)
        except (ValueError, TypeError, rfc8785.CanonicalizationError) as error:
            details["diagnostic_jcs"] = type(error).__name__

    raw_policy = None
    try:
        value = bundle["policy_hex"]
        if type(value) is not str or len(value) > 16384 or not re.fullmatch(r"(?:[0-9a-f]{2})+", value):
            raise ValueError("policy hex")
        raw_policy = bytes.fromhex(value)
        trace["policy_digest"] = m.byte.digest_text(raw_policy)
        policy = m.numeric.parse_json(raw_policy)
        checks["policy_interpretation"] = "PASS" if m.same(policy, m.POLICY) else "UNASSESSED"
        if checks["policy_interpretation"] == "UNASSESSED":
            details["policy_interpretation"] = "not the selected synthetic unit/mapping policy"
    except (ValueError, TypeError) as error:
        checks["policy_interpretation"] = "FAIL"
        details["policy_interpretation"] = str(error)

    def policy_binding():
        m.byte.require(raw_policy is not None, "policy bytes unavailable")
        digest = m.byte.digest_text(raw_policy)
        m.byte.require(event["Payload"]["PolicyDigest"] == digest and anchor["PolicyDigest"] == digest, "policy byte digest binding")
        m.byte.require(event["Header"]["PolicyID"] == m.POLICY_ID and anchor["PolicyID"] == m.POLICY_ID, "research policy identity")

    attempted("policy_binding", policy_binding)
    for role in ("event", "anchor"):
        statement, signature = bundle[role + "_statement"], bundle[role + "_signature"]
        encoded_sig = attempted(role + "_signature_encoding", lambda: m.byte.signature_bytes(signature))
        if encoded_sig is not None:
            trace[role + "_signature"] = encoded_sig.hex()
        try:
            message = m.byte.signature_preimage(statement, role + "_signature")
            if role == "event":
                checks["event_statement_shape"] = "PASS"
            trace[role + "_signature_preimage_hex"] = message.hex()
            # Diagnostic digest only: Ed25519 signs the full preimage, not this hash.
            trace[role + "_signature_message_hash"] = m.sha(message)
            if encoded_sig is None:
                checks[role + "_crypto"] = checks[role + "_test_trust"] = "UNASSESSED"
            else:
                checks[role + "_crypto"] = "PASS" if m.byte.raw_verify(m.PUBLIC_KEYS[role], signature, message) else "FAIL"
                trust = m.byte.signature_check(statement, signature, role + "_signature", m.TRUST)
                checks[role + "_test_trust"] = {"pass": "PASS", "fail": "FAIL", "unknown": "UNASSESSED"}[trust]
        except (m.byte.Rejected, TypeError, ValueError, KeyError) as error:
            if role == "event":
                checks["event_statement_shape"] = "FAIL"
            checks[role + "_crypto"] = "UNASSESSED"
            checks[role + "_test_trust"] = "UNASSESSED"
            details[role + "_signature"] = "candidate signature input rejected: " + str(error)

    attempted("event_binding", lambda: m.byte.event_binding(event, bundle["event_statement"]))
    attempted("batch_binding", lambda: m.byte.batch_binding([event], anchor, raw_policy))
    try:
        preimage = m.byte.external_preimage(anchor, bundle["anchor_signature"])
        trace["external_preimage_hex"] = preimage.hex()
        trace["external_commitment"] = m.byte.digest_text(preimage)
        checks["external_binding"] = "PASS" if bundle["external_commitment"] == trace["external_commitment"] else "FAIL"
    except (m.byte.Rejected, TypeError, ValueError, KeyError) as error:
        checks["external_binding"] = "UNASSESSED"
        details["external_binding"] = str(error)
    if set(checks) != CHECKS:
        raise ValueError("incomplete composition checks")
    return {"checks": checks, "covered_checks_result": aggregate(list(checks.values())),
            "details": details, "trace": trace, "status": "UNADOPTED",
            "independent_reproduction": "not_established", "native_vcp_conformance": "not_assessed",
            "real_identity_and_authorization": "not_assessed", "external_receipt_and_time": "not_assessed",
            "transport_used_for_semantics": False}


def relations(actual, reference):
    return {name: "UNAVAILABLE" if name not in actual["trace"] or name not in reference["trace"] else
            "SAME" if actual["trace"][name] == reference["trace"][name] else "CHANGED" for name in sorted(RELATIONS)}
