"""Check frozen synthetic vectors; never writes/replaces a vector or legacy file."""
import argparse
import base64
import copy
import hashlib
import importlib.metadata
import json
import platform
import re
from pathlib import Path
import subprocess
import sys

from cryptography.hazmat.backends.openssl.backend import backend
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import contract as c
import generate as g

HERE = Path(__file__).resolve().parent


def check(directory):
    counts = {}

    def equal(actual, expected, group):
        if actual != expected:
            raise RuntimeError(f"{group}: expected {expected!r}, got {actual!r}")
        counts[group] = counts.get(group, 0) + 1

    def rejects(fn, group):
        try:
            fn()
        except c.Rejected:
            counts[group] = counts.get(group, 0) + 1
        else:
            raise RuntimeError(group + ": unexpected acceptance")

    for name, data in g.encoded_files().items():
        equal((directory / name).read_bytes() == data, True, "exact_regeneration")
    v = c.load_json((directory / "vectors.json").read_bytes())
    m = [c.load_json(line) for line in (directory / "merkle-vectors.jsonl").read_bytes().splitlines()]
    keys = v["public_test_keys"]
    equal(v["domain_prefixes_hex"], {k: b.hex() for k, b in c.DOMAINS.items()}, "domain_literals")
    equal(len(set(c.DOMAINS.values())), len(c.DOMAINS), "domain_separation")
    events = [e["input"] for e in v["events"]]
    for e in v["events"] + v["extra_events"]:
        equal(c.jcs(e["input"]).decode(), e["jcs_utf8"], "event_jcs")
        equal(c.event_preimage(e["input"]).hex(), e["preimage_hex"], "event_preimage")
        equal(c.event_hash(e["input"]), e["event_hash"], "event_hash")
    for i, e in enumerate(events[1:], 1):
        equal(e["PreviousEventHash"], c.event_hash(events[i - 1]), "local_predecessor_linkage")
    # A changed predecessor is detected by comparison, without claiming restart authorization.
    equal(events[2]["PreviousEventHash"] == c.event_hash(events[0]), False, "wrong_predecessor")
    for case in v["event_hash_mutations"]:
        mutated = g.replace(events[0], case["path"], case["replacement"])
        # Coverage test hashes raw mutated preimages even if the shape is unsupported.
        equal(c.digest_text(c.DOMAINS["event"] + c.jcs(mutated)) == v["events"][0]["event_hash"],
              case["expected_hash_equal"], "event_protected_field_mutation")
    for field in list(events[0]):
        e = copy.deepcopy(events[0]); del e[field]
        rejects(lambda: c.event_validate(e), "event_missing_field")
    for path in ([], ["Header"], ["PolicyIdentification"]):
        e = copy.deepcopy(events[0]); obj = e
        for part in path:
            obj = obj[part]
        obj["UnknownInterpretation"] = "x"
        rejects(lambda: c.event_validate(e), "event_unknown_field")
    e = copy.deepcopy(events[0]); e["Security"] = {"signature_valid": True}
    rejects(lambda: c.event_validate(e), "validity_flag_not_evidence")
    e = copy.deepcopy(events[0]); e["ChainMode"] = "linked"
    rejects(lambda: c.event_validate(e), "chain_shape")
    e = copy.deepcopy(events[1]); e["ChainMode"] = "start"
    rejects(lambda: c.event_validate(e), "chain_shape")
    e = copy.deepcopy(events[0]); e["Header"]["TimestampISO"] = "2026-10-09T00:00:00Z"
    rejects(lambda: c.event_validate(e), "unmapped_timestamp_iso")

    a = v["anchor"]; statement = a["statement"]
    roles = {"event_signature": "event", "anchor_signature": "anchor"}
    # Configure the test authority separately; do not promote statement fields
    # or its embedded test public key into trust entries.
    fixed_trust = {
        (kind, g.PRODUCER, g.STREAM, "urn:vcp-research:key:" + role):
        Ed25519PrivateKey.from_private_bytes(g.KEYS[role]).public_key().public_bytes_raw().hex()
        for kind, role in roles.items()
    }
    for kind, rows in (("event_signature", v["event_signatures"]), ("anchor_signature", [a])):
        for row in rows:
            s, sig = row["statement"], row["signature"]
            equal(c.jcs(s).decode(), row["jcs_utf8"], "signed_jcs")
            equal(c.signature_preimage(s, kind).hex(), row["preimage_hex"], "signed_preimage")
            equal(c.signature_check(s, sig, kind, fixed_trust), "pass", "signature_with_test_trust")
            equal(c.signature_check(s, sig, kind, {}), "unknown", "missing_trust_not_pass")
            wrong_trust = {k: keys["unauthorized"]["public_key_hex"] for k in fixed_trust}
            equal(c.signature_check(s, sig, kind, wrong_trust), "fail", "wrong_key")
            raw = bytearray(base64.b64decode(sig)); raw[0] ^= 1
            equal(c.signature_check(s, base64.b64encode(raw).decode(), kind, fixed_trust), "fail", "changed_signature")
            opposite = "anchor_signature" if kind == "event_signature" else "event_signature"
            equal(c.raw_verify(keys[roles[kind]]["public_key_hex"], sig,
                               c.DOMAINS[opposite] + c.jcs(s)), False, "wrong_signature_domain")
            for bad in (sig.rstrip("="), sig + "\n", sig + "=", base64.b64encode(b"x" * 63).decode()):
                rejects(lambda: c.signature_bytes(bad), "signature_encoding")
            if kind == "event_signature":
                c.event_binding(events[int(row["event_index"])], s)
                counts["event_signature_binding"] = counts.get("event_signature_binding", 0) + 1
    for kind, row in (("event_signature", v["event_signatures"][0]), ("anchor_signature", a)):
        role = roles[kind]
        for field in ("ProducerID", "StreamID", "KeyID"):
            s = g.replace(row["statement"], [field], "urn:vcp-research:untrusted:other")
            sig = g.sign(s, kind, role)
            equal(c.raw_verify(keys[role]["public_key_hex"], sig, c.signature_preimage(s, kind)),
                  True, "resigned_identity_raw_signature")
            equal(c.signature_check(s, sig, kind, fixed_trust), "unknown", "untrusted_identity_not_pass")
        identity = (kind, row["statement"]["ProducerID"], row["statement"]["StreamID"], row["statement"]["KeyID"])
        wrong_role = "anchor_signature" if kind == "event_signature" else "event_signature"
        role_mismatch = {(wrong_role, *identity[1:]): fixed_trust[identity]}
        equal(c.signature_check(row["statement"], row["signature"], kind, role_mismatch),
              "unknown", "untrusted_role_not_pass")
    for field in statement:
        s = copy.deepcopy(statement); del s[field]
        rejects(lambda: c.anchor_validate(s), "anchor_missing_field")
    s = copy.deepcopy(statement); s["UnprotectedExtension"] = "ignored?"
    rejects(lambda: c.anchor_validate(s), "anchor_unknown_field")
    for case in v["signature_mutations"]:
        kind = case["kind"]
        row = a if kind == "anchor_signature" else v["event_signatures"][0]
        s = g.replace(row["statement"], case["path"], case["replacement"])
        try:
            c.signature_preimage(s, kind); fmt = "pass"
        except c.Rejected:
            fmt = "reject"
        equal(fmt, case["expected_format"], "signed_field_mutation_format")
        actual = c.raw_verify(keys[roles[kind]]["public_key_hex"], row["signature"], c.DOMAINS[kind] + c.jcs(s))
        equal("pass" if actual else "fail", case["expected_original_signature"], "signed_field_mutation_crypto")
    policy = bytes.fromhex(v["policy_bytes_hex"])
    equal(c.digest_text(policy), v["policy_digest"], "policy_digest")
    c.batch_binding(events[:3], statement, policy)
    counts["positive_full_list_binding"] = 1
    rejects(lambda: c.batch_binding(events[:3], statement, policy + b"\n"), "changed_policy_bytes")
    for case in v["signed_inconsistencies"]:
        actual = c.raw_verify(keys["anchor"]["public_key_hex"], case["signature"],
                              c.signature_preimage(case["statement"], "anchor_signature"))
        equal("pass" if actual else "fail", case["expected_raw_signature"], "resigned_inconsistency_signature")
        rejects(lambda: c.batch_binding(events[:3], case["statement"], policy), "resigned_inconsistency_binding")
    for changed_events, group in ((list(reversed(events[:3])), "reordered_events"),
                                   (events[:2], "omitted_event"),
                                   (events[:3] + [events[2]], "extra_event")):
        rejects(lambda: c.batch_binding(changed_events, statement, policy), group)
    duplicate = copy.deepcopy(events[:3]); duplicate[1]["Header"]["EventID"] = duplicate[0]["Header"]["EventID"]
    # Root, count and endpoints agree: the duplicate-ID semantic rule must still fail.
    duplicate_anchor = g.anchor(duplicate)
    rejects(lambda: c.batch_binding(duplicate, duplicate_anchor, policy), "duplicate_id_with_matching_root")
    mixed = copy.deepcopy(events[:3]); mixed[1]["Header"]["PolicyID"] = "urn:vcp-research:policy:other"
    rejects(lambda: c.batch_binding(mixed, g.anchor(mixed), policy), "mixed_policy_with_matching_root")
    e_statement = copy.deepcopy(v["event_signatures"][0]["statement"])
    e_statement["EventHash"] = v["events"][1]["event_hash"]
    sig = g.sign(e_statement, "event_signature", "event")
    equal(c.signature_check(e_statement, sig, "event_signature", fixed_trust), "pass", "resigned_wrong_event_hash")
    rejects(lambda: c.event_binding(events[0], e_statement), "resigned_wrong_event_binding")

    digests = [c.digest_bytes(e["event_hash"]) for e in v["events"]]
    equal(c.tree([]).hex(), v["empty_root_hex"], "empty_tree")
    equal([int(row["count"]) for row in m], g.SIZES, "tree_size_inventory")
    for row in m:
        n = int(row["count"]); root = bytes.fromhex(row["root_hex"])
        equal(c.tree(digests[:n]), root, "merkle_root")
        equal([int(p["index"]) for p in row["proofs"]], list(range(n)), "proof_index_inventory")
        for proof in row["proofs"]:
            i = int(proof["index"]); nodes = [bytes.fromhex(h) for h in proof["nodes_hex"]]
            equal(c.membership(digests[i], str(i), str(n), nodes, root), True, "merkle_membership")
            equal(c.membership(digests[i], str(i), str(n), nodes + [b"\x00" * 32], root), False, "surplus_proof")
            equal(c.membership(digests[i], str(i), str(n), nodes, b"\x00" * 32), False, "wrong_root")
            if nodes:
                equal(c.membership(digests[i], str(i), str(n), nodes[:-1], root), False, "missing_proof")
                bad = [bytes([nodes[0][0] ^ 1]) + nodes[0][1:]] + nodes[1:]
                equal(c.membership(digests[i], str(i), str(n), bad, root), False, "changed_proof_node")
    rejects(lambda: c.membership(digests[0], "0", "3", [b"x"], c.tree(digests[:3])), "bad_proof_length")
    rejects(lambda: c.membership(digests[0], "3", "3", [], c.tree(digests[:3])), "index_range")
    rejects(lambda: c.membership(b"x", "0", "1", [], c.tree(digests[:1])), "bad_leaf_length")
    rejects(lambda: c.membership(digests[0], "0", "0", [], c.tree([])), "empty_signed_batch")
    for i in (4, 5):
        equal(c.membership(digests[i], str(i), "6", c.path(digests[:8], i), c.tree(digests[:8])), False, "eight_as_six_size_attack")
    equal(c.tree(digests[:3]) == c.tree(digests[:3] + [digests[2]]), False, "odd_duplication_distinguished")
    for case in v["numeric_vectors"]:
        value = json.loads(case["input_json"])
        field = case["field"]
        lo, hi = (1, c.MAX_COUNT) if field == "EventCount" else (0, 2) if field.startswith("LeafIndex") else (0, c.MAX_NS)
        try:
            c.decimal(value, lo, hi); actual = "accept"
        except c.Rejected:
            actual = "reject"
        equal(actual, case["expected"], "numeric_lexical_and_range")
    for raw in v["invalid_json"]:
        rejects(lambda: c.load_json(raw), "malformed_or_unsupported_json")
    for raw in (b"\xef\xbb\xbf{}", "{}".encode("utf-16"), "{}".encode("utf-16-le"),
                "{}".encode("utf-32"), b'{"x":"\xff"}', {"already_parsed": True}):
        rejects(lambda: c.load_json(raw), "transport_encoding_rejection")
    equal(c.load_json('{"x":"証拠 😀"}'.encode("utf-8")), {"x": "証拠 😀"}, "utf8_bytes_supported")
    equal(c.jcs({"x": "é"}) == c.jcs({"x": "e\u0301"}), False, "unicode_not_normalized")
    equal(c.external_preimage(statement, a["signature"]).hex(), a["external_preimage_hex"], "external_preimage")
    equal(c.digest_text(c.external_preimage(statement, a["signature"])), a["external_commitment"], "external_commitment")
    altered_target = g.replace(statement, ["IntendedAnchorTarget", "Identifier"], "urn:vcp-research:target:other")
    altered_sig = g.sign(altered_target, "anchor_signature", "anchor")
    equal(c.digest_text(c.external_preimage(altered_target, altered_sig)) == a["external_commitment"], False, "target_changes_external_commitment")
    for statuses, expected in ((["pass", "unknown"], "unknown"), (["fail", "unknown"], "fail"), (["pass", "pass"], "pass")):
        equal(c.aggregate_required(statuses), expected, "aggregate_failure_over_unknown")
    return counts


def validate_node_report(report, data_hashes, counts):
    """Check completion evidence, not just process exit or a self-reported pass.

    This cannot authenticate an executable/operator or detect a fully forged
    report; it rejects missing/failed/incomplete/mismatched check reports.
    """
    expected_counts = {
        "derived_public_key": 3, "domain": len(c.DOMAINS),
        **{k: counts[k] for k in ("event_jcs", "event_preimage", "event_hash", "signed_jcs", "signed_preimage", "merkle_root", "merkle_membership")},
        "signature_verify": counts["signed_preimage"], "signature_generation": counts["signed_preimage"],
        "signed_mutation": counts["signed_field_mutation_crypto"],
        "inconsistent_record_raw_signature_only": counts["resigned_inconsistency_signature"],
        "empty_root": 1, "numeric_exact_bigint": counts["numeric_lexical_and_range"],
        "external_preimage": 1, "external_commitment": 1, "policy_bytes": 1,
    }
    c.exact(report, "status node openssl scope counts contract_id data_sha256")
    c.require(report["status"] == "internal byte agreement; not independent reproduction", "Node status")
    c.require(report["contract_id"] == c.CONTRACT, "Node contract")
    c.require(report["data_sha256"] == data_hashes, "Node input hashes")
    actual = report["counts"]
    c.require(type(actual) is dict and all(type(n) is int for n in actual.values()) and
              actual == expected_counts, "Node coverage incomplete or invalid")
    c.require(type(report["node"]) is str and re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", report["node"]), "Node version")
    c.require(type(report["openssl"]) is str and bool(report["openssl"]), "Node OpenSSL version")
    c.require(report["scope"] == "known-answer JCS subset, hashes, trees/proofs, raw signatures and decimal fields; not full schema/trust/receipt validation", "Node scope")


def node_report_negative_controls(report, data_hashes, counts):
    cases = {
        "empty": {},
        "failed_status": g.replace(report, ["status"], "failed"),
        "wrong_contract": g.replace(report, ["contract_id"], "other"),
        "wrong_input_hash": g.replace(report, ["data_sha256", "vectors.json"], "0" * 64),
        "zero_coverage": g.replace(report, ["counts", "merkle_membership"], 0),
        "boolean_count": g.replace(report, ["counts", "empty_root"], True),
        "string_count": g.replace(report, ["counts", "empty_root"], "1"),
        "missing_group": copy.deepcopy(report),
        "missing_environment": g.replace(report, ["node"], ""),
    }
    del cases["missing_group"]["counts"]["event_hash"]
    for name, invalid in cases.items():
        try:
            validate_node_report(invalid, data_hashes, counts)
        except c.Rejected:
            continue
        raise RuntimeError("Node report control unexpectedly accepted: " + name)
    return {name: "rejected" for name in cases}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vectors", type=Path, default=HERE / "data")
    parser.add_argument("--node", help="Optional Node executable for separate byte/tree cross-check")
    args = parser.parse_args()
    result = {"status": "internal candidate-vector checks passed", "counts": check(args.vectors),
              "contract_id": c.CONTRACT, "adoption": "unadopted", "independent_reproduction": "unestablished",
              "scope": "closed synthetic candidate; NOT current VCP conformance",
              "not_assessed": ["key validity/revocation/trusted time", "external receipt verification",
                               "partial disclosure sufficiency", "chain restart/recovery authority",
                               "native VCP schema and COSE mapping", "real-world completeness"],
              "environment": {"python": sys.version, "platform": platform.platform(),
                              "openssl": backend.openssl_version_text(),
                              "dependencies": {p: importlib.metadata.version(p) for p in ("cryptography", "rfc8785")},
                              "installed_distributions": {d.metadata["Name"]: d.version for d in sorted(importlib.metadata.distributions(), key=lambda d: d.metadata["Name"].lower())}},
              "data_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (args.vectors / "vectors.json", args.vectors / "merkle-vectors.jsonl")}}
    if args.node:
        run = subprocess.run([args.node, str(HERE / "crosscheck.mjs"), str(args.vectors.resolve())],
                             check=True, capture_output=True, text=True)
        node_report = json.loads(run.stdout)
        validate_node_report(node_report, result["data_sha256"], result["counts"])
        result["node_report_negative_controls"] = node_report_negative_controls(node_report, result["data_sha256"], result["counts"])
        result["node_crosscheck"] = node_report
    else:
        result["node_crosscheck"] = "not run"
    print(json.dumps(result, indent=2))
