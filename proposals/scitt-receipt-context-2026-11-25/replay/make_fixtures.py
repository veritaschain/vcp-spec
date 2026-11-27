"""Produce only the fixed, ordinary signed inputs for seven research cases."""
import argparse
import hashlib
import json
from pathlib import Path

import cbor2
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parent
SERVICE = "https://transparency.example"
ISSUER = "https://issuer.example"
SCOPE = "restricted-E-v1"
PRIMARY = "urn:example:fixture:primary"
SIBLING = "urn:example:fixture:sibling"


def sha(data):
    return hashlib.sha256(data).digest()


def test_key(label):
    # Publicly reproducible fixture seeds. These are not operational keys.
    return Ed25519PrivateKey.from_private_bytes(
        sha(b"VSO SCITT ordinary fixture 2026-11-27 PUBLIC TEST SEED " + label.encode("ascii"))
    )


def public(key):
    return key.public_key().public_bytes_raw().hex()


def json_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def cbor(value):
    return cbor2.dumps(value, canonical=True)


def sign1(key, protected, unprotected, payload, detached=False):
    headers = cbor(protected)
    signature = key.sign(cbor(["Signature1", headers, b"", payload]))
    return cbor(cbor2.CBORTag(18, [headers, unprotected, None if detached else payload, signature]))


def statement(issuer, subject):
    protected = {1: -8, 3: "application/json", 4: b"ISSUER", 15: {1: ISSUER, 2: subject}}
    payload = json_bytes({"artifact": subject, "observation": "ordinary synthetic record"})
    return sign1(issuer, protected, {}, payload)


def authority_record(authority, data):
    body = json_bytes(data)
    return {"body": body.hex(), "signature": authority.sign(body).hex()}


def view(rules, keys, receipts):
    return {"rules": rules, "keys": keys, "receipts": receipts}


def make():
    archive = test_key("entry-rule archive authority")
    key_authority = test_key("historical signing key authority")
    issuer = test_key("statement issuer")
    first = statement(issuer, PRIMARY)
    second = statement(issuer, SIBLING)
    sibling = sha(b"\x00" + second)
    root = sha(b"\x01" + sha(b"\x00" + first) + sibling)
    proof_header = {396: {-1: [cbor([2, 0, [sibling]])]}}
    receipts, records = {}, {}
    for kid, epoch, status in (("K1", "key-epoch-1", "retired"), ("K2", "key-epoch-2", "current")):
        key = test_key(kid)
        protected = {1: -8, 4: kid.encode("ascii"), 15: {1: SERVICE, 2: PRIMARY}, 395: 1}
        receipt = sign1(key, protected, proof_header, root, detached=True)
        receipts[kid] = receipt.hex()
        # The key authority attests to authorization for use on this exact receipt.
        # The entry-rule authority supplies no time or key authorization evidence.
        records[kid] = authority_record(key_authority, {
            "kind": "receipt-key", "service": SERVICE, "kid": kid,
            "public_key": public(key), "receipt_sha256": sha(receipt).hex(),
            "epoch": epoch, "status": status,
        })
    for rule, epoch in (("A1", "epoch-1"), ("A2", "epoch-2")):
        records[rule] = authority_record(archive, {
            "kind": "entry-rule", "service": SERVICE,
            "entry_sha256": sha(first).hex(), "preprocessing": SCOPE,
            "rule": rule, "epoch": epoch,
        })
    bundle = {"service": SERVICE, "statement": first.hex(), "sibling_statement": second.hex(),
              "receipts": receipts, "records": records}
    trust = {
        "service": SERVICE, "archive_public_key": public(archive),
        "key_authority_public_key": public(key_authority), "issuer_public_key": public(issuer),
        "views": {
            "CX-01": view(["A1"], ["K1"], ["K1"]),
            "CX-09": view(["A1"], ["K1", "K2"], ["K1"]),
            "CX-10": view(["A1"], ["K2"], ["K1"]),
            "CX-17": view(["A1"], ["K1"], ["K1"]),
            "CX-19": view(["A1"], ["K1", "K2"], ["K1", "K2"]),
            "CX-21": view(["A1"], ["K1"], ["K2"]),
            "CX-22": view(["A1", "A2"], ["K1"], ["K1"]),
        },
    }
    return {"bundle.json": bundle, "trust.json": trust}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="compare files without writing")
    args = ap.parse_args()
    for name, value in make().items():
        path = ROOT / name
        new = (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")
        if args.check:
            if path.read_bytes() != new:
                raise SystemExit(f"Fixture differs: {name}")
        else:
            path.write_bytes(new)


if __name__ == "__main__":
    main()
