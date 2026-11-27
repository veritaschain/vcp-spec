"""Replay the fixed, two-leaf SCITT context corpus using independently supplied trust."""
import argparse
import hashlib
import json
from pathlib import Path

import cbor2
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).digest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sign1(data):
    decoded = cbor2.loads(data)
    require(isinstance(decoded, cbor2.CBORTag) and decoded.tag == 18, "Expected tagged COSE_Sign1")
    require(len(decoded.value) == 4, "Expected four-element Sign1")
    protected, unprotected, payload, signature = decoded.value
    headers = cbor2.loads(protected)
    require(headers[1] == -8 and isinstance(headers[4], bytes), "Expected EdDSA and a key ID")
    require(isinstance(headers[15][1], str) and isinstance(headers[15][2], str), "Missing CWT claims")
    return headers, unprotected, payload, signature, protected


def verify_signature(public_hex, signature, message):
    key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_hex))
    key.verify(signature, message)


def sig_structure(protected, payload):
    return cbor2.dumps(["Signature1", protected, b"", payload])


def inspect_statement(raw, issuer_key):
    headers, unprotected, payload, signature, protected = sign1(raw)
    require(unprotected == {} and raw.startswith(b"\xd2\x84"), "Expected fixed restricted statement form")
    require(headers[15][1] == "https://issuer.example" and headers[4] == b"ISSUER", "Unexpected issuer")
    require(headers[3] == "application/json" and isinstance(payload, bytes), "Expected embedded JSON bytes")
    require(json.loads(payload)["artifact"] == headers[15][2], "Unexpected fixture subject")
    verify_signature(issuer_key, signature, sig_structure(protected, payload))
    # The supplied statement already has the empty unprotected map. E is the
    # original exact bytes, including protected/payload/signature encodings.
    return headers[15][2]


def authenticated_record(envelope, authority):
    body = bytes.fromhex(envelope["body"])
    verify_signature(authority, bytes.fromhex(envelope["signature"]), body)
    return json.loads(body)


def eligible_rules(bundle, trust, view, entry_digest):
    rules = []
    for name in view["rules"]:
        doc = authenticated_record(bundle["records"][name], trust["archive_public_key"])
        if (doc["kind"] == "entry-rule" and doc["service"] == trust["service"]
                and doc["entry_sha256"] == entry_digest and doc["preprocessing"] == "restricted-E-v1"):
            rules.append((doc["rule"], doc["epoch"]))
    return set(rules)


def eligible_key(bundle, trust, key_names, kid, receipt_digest):
    for name in key_names:
        doc = authenticated_record(bundle["records"][name], trust["key_authority_public_key"])
        if (doc["kind"] == "receipt-key" and doc["service"] == trust["service"]
                and doc["kid"] == kid and doc["receipt_sha256"] == receipt_digest
                and doc["epoch"] and doc["status"] in ("current", "retired")):
            return doc
    return None


def verify_receipt(raw, name, scope, bundle, trust, view, roots):
    headers, unprotected, payload, signature, protected = sign1(raw)
    require(payload is None and headers[395] == 1, "Expected detached RFC9162_SHA256 Receipt")
    require(headers[15] == {1: trust["service"], 2: scope} and headers[4] == name.encode("ascii"),
            "Unexpected service, subject or key ID")
    rules = eligible_rules(bundle, trust, view, roots["entry"].hex())
    if len(rules) > 1:
        return "context_ambiguous_rule", {}
    require(len(rules) == 1, "No applicable rule in this corpus")
    rule, epoch = next(iter(rules))
    require(rule == "A1", "This corpus uses A1 for every unambiguous path")
    key = eligible_key(bundle, trust, view["keys"], name, sha(raw).hex())
    if key is None:
        return "context_insufficient_key", {"rule": rule, "rule_epoch": epoch}

    proofs = unprotected[396][-1]
    require(len(proofs) == 1, "Expected one ordinary inclusion proof")
    size, index, path = cbor2.loads(proofs[0])
    require((size, index) == (2, 0) and path == [roots["sibling"]], "Expected fixed two-leaf fixture")
    reconstructed = sha(b"\x01" + roots["leaf"] + path[0])
    require(reconstructed == roots["root"], "Root differs from independently supplied two statements")
    verify_signature(key["public_key"], signature, sig_structure(protected, reconstructed))
    return "verified", {
        "claim": "inclusion under service-signed root", "key_epoch": key["epoch"],
        "key_status": key["status"], "rule": rule, "rule_epoch": epoch,
    }


def replay(bundle, trust):
    require(bundle["service"] == trust["service"], "Service does not match the trust input")
    primary = bytes.fromhex(bundle["statement"])
    sibling = bytes.fromhex(bundle["sibling_statement"])
    scope = inspect_statement(primary, trust["issuer_public_key"])
    inspect_statement(sibling, trust["issuer_public_key"])
    roots = {"entry": sha(primary), "leaf": sha(b"\x00" + primary), "sibling": sha(b"\x00" + sibling)}
    roots["root"] = sha(b"\x01" + roots["leaf"] + roots["sibling"])
    receipts = {name: bytes.fromhex(raw) for name, raw in bundle["receipts"].items()}
    require(receipts["K1"] != receipts["K2"], "Reissued Receipt must have different bytes")
    cases, details = {}, {}
    for case_id, view in trust["views"].items():
        cases[case_id], details[case_id] = {}, {}
        for name in view["receipts"]:
            status, detail = verify_receipt(receipts[name], name, scope, bundle, trust, view, roots)
            cases[case_id][name], details[case_id][name] = status, detail
    return {
        "cases": cases, "details": details, "entry_sha256": roots["entry"].hex(),
        "leaf_sha256": roots["leaf"].hex(), "root_sha256": roots["root"].hex(),
        "receipt_sha256": {kid: sha(raw).hex() for kid, raw in receipts.items()},
        "history_consistency": "unassessed", "source_completeness": "unassessed",
        "issuance_time": "unassessed", "position_and_size": "unassessed",
        "local_vcp_batch_integrity": "unassessed",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle", type=Path, default=HERE / "bundle.json")
    ap.add_argument("--trust", type=Path, default=HERE / "trust.json")
    ap.add_argument("--expected", type=Path, default=HERE / "expected.json")
    args = ap.parse_args()
    report = replay(json.loads(args.bundle.read_bytes()), json.loads(args.trust.read_bytes()))
    print(json.dumps(report, sort_keys=True, indent=2))
    if report["cases"] != json.loads(args.expected.read_bytes())["cases"]:
        raise SystemExit("Observed case reports differ from the separately recorded oracle")


if __name__ == "__main__":
    main()
