"""Deterministic PUBLIC synthetic evidence and separately declared expectations.

This producer imports the pinned byte contract to construct/sign new fixtures;
it never imports or calls the composition checker. It rewrites no old fixture.
"""
import argparse
import base64
import copy
import json

import common as m

CHECK_NAMES = (
    "event_parse", "event_shape", "event_statement_shape", "anchor_shape", "numeric", "policy_binding",
    "policy_interpretation", "event_crypto", "event_test_trust", "event_binding", "anchor_crypto",
    "anchor_test_trust", "batch_binding", "external_binding", "event_signature_encoding", "anchor_signature_encoding",
)
RELATION_NAMES = (
    "event_hash", "leaf_hash", "root_hash", "event_signature_message_hash", "event_signature",
    "anchor_signature_message_hash", "anchor_signature", "external_commitment", "policy_digest", "diagnostic_jcs_hash",
)
EVENT_CHANGE = {k: "CHANGED" for k in RELATION_NAMES if k != "policy_digest"}
HASH_CHANGE = {k: "CHANGED" for k in ("event_hash", "leaf_hash", "root_hash", "diagnostic_jcs_hash")}
INVALID_EVENT = {"event_shape": "FAIL", "event_binding": "FAIL", "batch_binding": "FAIL"}
UNAVAILABLE_EVENT = {k: "UNAVAILABLE" for k in ("event_hash", "leaf_hash", "root_hash")}


def event_statement(event):
    return {"ContractID": m.byte.CONTRACT, **m.byte.SCHEMES,
            "SignatureScheme": "ed25519-event-v0", "SignatureAlgorithm": "Ed25519",
            "EventHash": m.byte.event_hash(event),
            **{k: event["Header"][k] for k in ("EventID", "ProducerID", "StreamID")}, "KeyID": m.KEY_IDS["event"]}


def anchor_statement(event, policy):
    event_id = event["Header"]["EventID"]
    return {"ContractID": m.byte.CONTRACT, **m.byte.SCHEMES, "TreeScheme": "rfc6962-sha256-digest-leaf-v0",
            "HashAlgorithm": "SHA-256", "SignatureScheme": "ed25519-anchor-v0", "SignatureAlgorithm": "Ed25519",
            "AnchorRecordID": "urn:vcp-research:anchor:numeric-one", "ProducerID": m.PRODUCER,
            "StreamID": m.STREAM, "BatchID": "urn:vcp-research:batch:numeric-one", "KeyID": m.KEY_IDS["anchor"],
            "MerkleRoot": "sha256:" + m.byte.tree([m.byte.digest_bytes(m.byte.event_hash(event))]).hex(),
            "EventCount": "1", "FirstEventID": event_id, "LastEventID": event_id, "PolicyID": m.POLICY_ID,
            "PolicyDigest": m.byte.digest_text(policy), "RecordedAtNs": "1735128000123457789",
            "IntendedAnchorTarget": {"Type": "synthetic-unconnected", "Identifier": "urn:vcp-research:target:numeric-none"}}


def external(bundle):
    return m.byte.digest_text(m.byte.external_preimage(bundle["anchor_statement"], bundle["anchor_signature"]))


def signed_bundle(event, policy=m.POLICY_BYTES):
    es, anchor = event_statement(event), anchor_statement(event, policy)
    result = {"event_json": json.dumps(event, ensure_ascii=True), "event_statement": es,
              "event_signature": m.sign(es, "event"), "anchor_statement": anchor,
              "anchor_signature": m.sign(anchor, "anchor"), "policy_hex": policy.hex(), "transport": {}}
    result["external_commitment"] = external(result)
    return result


def event_data():
    return {"ContractID": m.byte.CONTRACT, "EventHashAlgorithm": "SHA-256",
            "Header": {"EventID": "urn:vcp-research:event:numeric-one", "ProducerID": m.PRODUCER,
                       "StreamID": m.STREAM, "PolicyID": m.POLICY_ID, "TimestampInt": "1735128000123456789"},
            "Payload": {"ExperimentID": m.EXPERIMENT, "PolicyDigest": m.byte.digest_text(m.POLICY_BYTES),
                        "NumericEvidence": {"TimestampISO": "2024-12-25T12:00:00.123456789Z", "TimeBasis": "unix_no_leap",
                            "TimestampUnit": "unix_ns", "Duration": {"Value": "1", "Unit": "s"},
                            "Tolerance": {"Value": "1", "Unit": "ms"}, "Confidence": {"Value": "1", "Unit": "ratio"}}},
            "PolicyIdentification": {"PolicyID": m.POLICY_ID}, "ChainMode": "none", "PreviousEventHash": None}


def build():
    rows = []
    baseline_event = event_data()
    base = signed_bundle(baseline_event)

    def add(name, bundle, overrides=None, relation_changes=None, note="", reference="baseline"):
        checks = dict.fromkeys(CHECK_NAMES, "PASS")
        checks.update(overrides or {})
        relations = dict.fromkeys(RELATION_NAMES, "SAME")
        relations.update(relation_changes or {})
        aggregate = "FAIL" if "FAIL" in checks.values() else "UNASSESSED" if "UNASSESSED" in checks.values() else "PASS"
        rows.append({"id": name, "reference": reference, "note": note, "bundle": bundle,
                     "expected": {"checks": checks, "covered_checks_result": aggregate, "relations": relations}})

    def event_variant(name, mutate, mode="fresh", overrides=None, relation_changes=None, note="", reference="baseline", original=None):
        bundle = copy.deepcopy(original or base)
        event = json.loads(bundle["event_json"])
        mutate(event)
        if mode == "fresh":
            bundle = signed_bundle(event, bytes.fromhex(bundle["policy_hex"]))
        else:
            bundle["event_json"] = json.dumps(event, ensure_ascii=True)
            if mode == "statement_only":
                bundle["event_statement"] = event_statement(event)
        add(name, bundle, overrides, relation_changes, note, reference)
        return bundle

    def set_path(path, value):
        def mutate(event):
            target = event
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = value
        return mutate

    evidence = ["Payload", "NumericEvidence"]
    add("baseline", base, note="All covered synthetic checks pass; no native conformance or external time is established.")
    bundle = copy.deepcopy(base)
    bundle["event_json"] = json.dumps(baseline_event, sort_keys=True, indent=2)
    add("json-key-order-and-whitespace", bundle, note="JSON transport layout changes; canonical bytes and signatures do not.")
    bundle = copy.deepcopy(base)
    bundle["event_json"] = bundle["event_json"].replace('"Value": "1"', '"Value": "\\u0031"')
    add("json-escape-equivalence", bundle, note="An escape spelling for the same decoded numeric string is not a new signed lexeme.")
    bundle = copy.deepcopy(base)
    bundle["transport"] = {"DurationUnit": "ms", "TimestampUnit": "unix_ms", "Claim": "unsigned, not authoritative"}
    add("unsigned-unit-hints-excluded", bundle, note="Transport hints are never used to supply or override numeric semantics.")

    def next_ns(event):
        event["Header"]["TimestampInt"] = "1735128000123456790"
        event["Payload"]["NumericEvidence"]["TimestampISO"] = "2024-12-25T12:00:00.123456790Z"

    event_variant("one-ns-fresh-evidence", next_ns, relation_changes=EVENT_CHANGE,
                  note="A new consistent instant creates new event/leaf/root/messages/signatures/commitment.")
    event_variant("one-ns-stale-statements", next_ns, mode="keep",
                  overrides={"event_binding": "FAIL", "batch_binding": "FAIL"}, relation_changes=HASH_CHANGE,
                  note="Old signatures still verify over old statements, but those statements do not bind the changed event.")
    event_variant("one-ns-rehashed-not-resigned", next_ns, mode="statement_only",
                  overrides={"event_crypto": "FAIL", "event_test_trust": "FAIL", "batch_binding": "FAIL"},
                  relation_changes={**HASH_CHANGE, "event_signature_message_hash": "CHANGED"},
                  note="Recomputing EventHash in the statement invalidates the reused event signature.")
    event_variant("integer-only-one-ns-stale", set_path(["Header", "TimestampInt"], "1735128000123456790"), mode="keep",
                  overrides={"numeric": "FAIL", "event_binding": "FAIL", "batch_binding": "FAIL"}, relation_changes=HASH_CHANGE,
                  note="Numeric/ISO mismatch coexists with stale binding; raw old signatures remain valid.")
    event_variant("resigned-wrong-iso-year", set_path(evidence + ["TimestampISO"], "2025-12-25T12:00:00.123456789Z"),
                  overrides={"numeric": "FAIL"}, relation_changes=EVENT_CHANGE,
                  note="Fresh valid signatures and bindings cannot make a mismatched ISO year valid.")
    for name, value in (("iso-offset-spelling", "2024-12-25T12:00:00.123456789+00:00"),
                        ("iso-extra-fraction", "2024-12-25T12:00:00.1234567890Z")):
        event_variant(name, set_path(evidence + ["TimestampISO"], value), overrides={"numeric": "FAIL"},
                      relation_changes=EVENT_CHANGE, note="May denote the same time under a broader format; it is outside the selected numeric candidate.")
    event_variant("smear-unmapped", set_path(evidence + ["TimeBasis"], "smear"), overrides={"numeric": "UNASSESSED"},
                  relation_changes=EVENT_CHANGE, note="Signed claims of a smear basis do not supply its missing mapping.")

    def leap(event):
        event["Header"]["TimestampInt"] = "1483228800000000000"
        event["Payload"]["NumericEvidence"]["TimestampISO"] = "2016-12-31T23:59:60.000000000Z"
    event_variant("leap-unmapped", leap, overrides={"numeric": "UNASSESSED"}, relation_changes=EVENT_CHANGE)

    def epoch_one(event):
        event["Header"]["TimestampInt"] = "1"
        event["Payload"]["NumericEvidence"]["TimestampISO"] = "1970-01-01T00:00:00.000000001Z"
    one = event_variant("epoch-string-one", epoch_one, relation_changes=EVENT_CHANGE)
    event_variant("epoch-json-number-one", set_path(["Header", "TimestampInt"], 1), mode="keep", original=one,
                  reference="epoch-string-one", overrides={**INVALID_EVENT, "numeric": "FAIL"},
                  relation_changes={**UNAVAILABLE_EVENT, "diagnostic_jcs_hash": "CHANGED"},
                  note="Generic JCS distinguishes number 1 from string 1, but no candidate EventHash is defined for the number input.")

    def maximum(event):
        event["Header"]["TimestampInt"] = "9223372036854775807"
        event["Payload"]["NumericEvidence"]["TimestampISO"] = "2262-04-11T23:47:16.854775807Z"
    event_variant("maximum-time-fresh", maximum, relation_changes=EVENT_CHANGE)
    event_variant("time-range-overflow", set_path(["Header", "TimestampInt"], "9223372036854775808"), mode="keep",
                  overrides={**INVALID_EVENT, "numeric": "FAIL"}, relation_changes={**UNAVAILABLE_EVENT, "diagnostic_jcs_hash": "CHANGED"})
    event_variant("header-iso-not-an-extension", set_path(["Header", "TimestampISO"], "2024-12-25T12:00:00.123456789Z"), mode="keep",
                  overrides=INVALID_EVENT, relation_changes={**UNAVAILABLE_EVENT, "diagnostic_jcs_hash": "CHANGED"},
                  note="The unchanged byte candidate rejects additional Header members; this adapter does not amend that contract.")

    for name, value, mode, numeric_result in (
        ("confidence-decimal-zero-suffix", "1.0", "fresh", "PASS"),
        ("confidence-leading-zero", "01.00", "fresh", "PASS"),
        ("confidence-above-one", "1.000000000000000001", "fresh", "FAIL"),
        ("confidence-boolean", True, "fresh", "FAIL"),
        ("confidence-null", None, "fresh", "FAIL"),
        ("confidence-json-number", 1, "keep", "FAIL"),
    ):
        changes = EVENT_CHANGE if mode == "fresh" else {**UNAVAILABLE_EVENT, "diagnostic_jcs_hash": "CHANGED"}
        checks = {} if numeric_result == "PASS" else {"numeric": numeric_result}
        if mode == "keep":
            checks.update(INVALID_EVENT)
        event_variant(name, set_path(evidence + ["Confidence", "Value"], value), mode=mode, overrides=checks, relation_changes=changes,
                      note="Byte-level commitments preserve type and decoded string spelling; a valid signature does not imply ratio validity.")
    zero = event_variant("confidence-zero", set_path(evidence + ["Confidence", "Value"], "0"), relation_changes=EVENT_CHANGE)
    event_variant("confidence-negative-zero", set_path(evidence + ["Confidence", "Value"], "-0.000"), original=zero,
                  reference="confidence-zero", relation_changes=EVENT_CHANGE,
                  note="Numerically equal signed zero stays a distinct committed string.")

    def duration_ms(event):
        event["Payload"]["NumericEvidence"]["Duration"] = {"Value": "1000", "Unit": "ms"}
    event_variant("duration-equivalent-ms-unmapped", duration_ms, overrides={"numeric": "FAIL"}, relation_changes=EVENT_CHANGE,
                  note="1 s and 1000 ms describe equal elapsed time, but N028 remains seconds; no automatic signed-data conversion.")
    event_variant("duration-unit-only-stale", set_path(evidence + ["Duration", "Unit"], "ms"), mode="keep",
                  overrides={"numeric": "FAIL", "event_binding": "FAIL", "batch_binding": "FAIL"}, relation_changes=HASH_CHANGE)
    event_variant("timestamp-unit-mismatch-signed", set_path(evidence + ["TimestampUnit"], "unix_ms"),
                  overrides={"numeric": "FAIL"}, relation_changes=EVENT_CHANGE)
    event_variant("tolerance-unit-mismatch-signed", set_path(evidence + ["Tolerance", "Unit"], "s"),
                  overrides={"numeric": "FAIL"}, relation_changes=EVENT_CHANGE)
    event_variant("confidence-percent-unmapped", set_path(evidence + ["Confidence", "Unit"], "percent"),
                  overrides={"numeric": "FAIL"}, relation_changes=EVENT_CHANGE)
    missing = copy.deepcopy(baseline_event)
    del missing["Payload"]["NumericEvidence"]["Duration"]["Unit"]
    bundle = signed_bundle(missing)
    bundle["transport"] = {"DurationUnit": "s"}
    add("unsigned-unit-cannot-fill-omission", bundle, {"numeric": "FAIL"}, EVENT_CHANGE,
        "An unsigned correct unit hint does not repair missing signed numeric evidence.")

    bundle = copy.deepcopy(base)
    bundle["policy_hex"] = (m.POLICY_BYTES + b"\n").hex()
    add("policy-byte-change-unbound", bundle, {"policy_binding": "FAIL", "batch_binding": "FAIL"}, {"policy_digest": "CHANGED"},
        "Equivalent policy JSON text still has different exact bytes; old policy digests are not silently recanonicalized.")
    raw = m.POLICY_BYTES + b"\n"
    event = copy.deepcopy(baseline_event)
    event["Payload"]["PolicyDigest"] = m.byte.digest_text(raw)
    add("policy-byte-change-new-evidence", signed_bundle(event, raw), relation_changes={**EVENT_CHANGE, "policy_digest": "CHANGED"},
        note="New synthetic signatures bind the new exact policy bytes; the old fixture is retained separately.")
    policy = copy.deepcopy(m.POLICY)
    policy["Units"]["Duration"] = "ms"
    raw = m.byte.jcs(policy)
    event = copy.deepcopy(baseline_event)
    event["Payload"]["PolicyDigest"] = m.byte.digest_text(raw)
    duration_ms(event)
    add("unselected-policy-resigned", signed_bundle(event, raw), {"numeric": "FAIL", "policy_interpretation": "UNASSESSED"},
        {**EVENT_CHANGE, "policy_digest": "CHANGED"}, "A self-consistent signed policy does not authorize a new unit/mapping contract.")

    for name, resign in (("anchor-count-stale-signature", False), ("anchor-count-resigned-wrong-list", True)):
        bundle = copy.deepcopy(base)
        bundle["anchor_statement"]["EventCount"] = "2"
        checks = {"batch_binding": "FAIL"}
        rel = {"anchor_signature_message_hash": "CHANGED", "external_commitment": "CHANGED"}
        if resign:
            bundle["anchor_signature"] = m.sign(bundle["anchor_statement"], "anchor")
            bundle["external_commitment"] = external(bundle)
            rel["anchor_signature"] = "CHANGED"
        else:
            checks.update(anchor_crypto="FAIL", anchor_test_trust="FAIL", external_binding="FAIL")
        add(name, bundle, checks, rel, "Anchor count is signed; a newly signed incorrect count still fails the supplied-list binding.")
    bundle = copy.deepcopy(base)
    bundle["anchor_statement"]["RecordedAtNs"] = "1735128000123457790"
    add("anchor-time-stale-signature", bundle, {"anchor_crypto": "FAIL", "anchor_test_trust": "FAIL", "external_binding": "FAIL"},
        {"anchor_signature_message_hash": "CHANGED", "external_commitment": "CHANGED"}, "RecordedAtNs is signed, but never establishes trusted external time.")
    bundle = copy.deepcopy(base)
    bundle["anchor_statement"]["EventCount"] = 1
    add("anchor-count-json-number", bundle, {"anchor_shape": "FAIL", "numeric": "FAIL", "anchor_crypto": "UNASSESSED",
        "anchor_test_trust": "UNASSESSED", "batch_binding": "FAIL", "external_binding": "UNASSESSED"},
        {"anchor_signature_message_hash": "UNAVAILABLE", "external_commitment": "UNAVAILABLE"})
    bundle = copy.deepcopy(base)
    signature = bytearray(base64.b64decode(bundle["anchor_signature"]))
    signature[0] ^= 1
    bundle["anchor_signature"] = base64.b64encode(signature).decode()
    add("anchor-signature-corrupted", bundle, {"anchor_crypto": "FAIL", "anchor_test_trust": "FAIL", "external_binding": "FAIL"},
        {"anchor_signature": "CHANGED", "external_commitment": "CHANGED"})

    bundle = copy.deepcopy(base)
    bundle["event_statement"]["KeyID"] = "urn:vcp-research:key:unapproved"
    bundle["event_signature"] = m.sign(bundle["event_statement"], "event")
    add("signed-unknown-key-id", bundle, {"event_test_trust": "UNASSESSED"},
        {"event_signature_message_hash": "CHANGED", "event_signature": "CHANGED"},
        "Raw Ed25519 validity does not authorize an unconfigured KeyID. Event signatures are outside the event/anchor digest inputs.")
    bundle = copy.deepcopy(base)
    message = m.byte.signature_preimage(bundle["event_statement"], "event_signature")
    bundle["event_signature"] = base64.b64encode(m.private_key("anchor").sign(message)).decode()
    add("event-wrong-role-key", bundle, {"event_crypto": "FAIL", "event_test_trust": "FAIL"}, {"event_signature": "CHANGED"})
    bundle = copy.deepcopy(base)
    wrong = m.byte.DOMAINS["anchor_signature"] + m.byte.jcs(bundle["event_statement"])
    bundle["event_signature"] = base64.b64encode(m.private_key("event").sign(wrong)).decode()
    add("event-wrong-domain-prefix", bundle, {"event_crypto": "FAIL", "event_test_trust": "FAIL"}, {"event_signature": "CHANGED"},
        "The event and anchor domain prefixes are not interchangeable.")
    bundle = copy.deepcopy(base)
    bundle["event_signature"] = "not base64"
    add("event-malformed-signature", bundle, {"event_signature_encoding": "FAIL", "event_crypto": "UNASSESSED", "event_test_trust": "UNASSESSED"},
        {"event_signature": "UNAVAILABLE"})
    bundle = copy.deepcopy(base)
    bundle["event_json"] = bundle["event_json"].replace('"TimestampInt": "1735128000123456789"', '"TimestampInt":"0","TimestampInt":"1735128000123456789"')
    add("duplicate-event-key", bundle, {**INVALID_EVENT, "event_parse": "FAIL", "numeric": "FAIL", "policy_binding": "FAIL"},
        {**UNAVAILABLE_EVENT, "diagnostic_jcs_hash": "UNAVAILABLE"}, "Duplicate JSON keys are rejected before any projection/hash.")

    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("duplicate case id")
    return {"experiment": m.EXPERIMENT, "status": "UNADOPTED", "source_commit": m.BASE,
            "independent_reproduction": "not_established", "test_keys": {role: {"public_test_seed_hex": m.SEEDS[role].hex(), "public_key_hex": m.PUBLIC_KEYS[role]} for role in m.SEEDS},
            "cases": rows}


def encoded():
    return m.bundle_bytes(build(), "cases")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write ONLY this experiment's new data/cases.json")
    args = parser.parse_args()
    path = m.HERE / "data/cases.json"
    raw = encoded()
    if args.write:
        path.write_bytes(raw)
    elif not path.exists() or path.read_bytes() != raw:
        parser.exit(1, "Stored synthetic evidence differs from the declared producer/expectations.\n")
    print(f"{len(build()['cases'])} synthetic cases; {'written' if args.write else 'bytes matched'}")
