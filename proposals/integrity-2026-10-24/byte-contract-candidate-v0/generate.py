"""Deterministic synthetic vectors, UNADOPTED. Writes only a new output directory.

All private seeds here are PUBLIC TEST MATERIAL and must never authorize real
records. No current VCP fixture or signed record is used or rewritten.
"""
import argparse
import base64
import copy
import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import contract as c

KEYS = {
    role: c.sha(("PUBLIC SYNTHETIC VCP BYTE CONTRACT V0 " + role).encode())
    for role in ("event", "anchor", "unauthorized")
}
PRODUCER = "urn:vcp-research:producer:alice"
STREAM = "urn:vcp-research:stream:demo"
POLICY_ID = "urn:vcp-research:policy:demo"
POLICY = b"SYNTHETIC ONLY\nPolicy: submit the declared ordered list.\n"
SIZES = list(range(1, 65)) + [65, 127, 128, 129]


def sign(statement, kind, role):
    key = Ed25519PrivateKey.from_private_bytes(KEYS[role])
    return base64.b64encode(key.sign(c.signature_preimage(statement, kind))).decode("ascii")


def event(index, previous=None):
    return {
        "ContractID": c.CONTRACT, "EventHashAlgorithm": "SHA-256",
        "Header": {"EventID": f"urn:vcp-research:event:{index:04d}",
                   "ProducerID": PRODUCER, "StreamID": STREAM,
                   "PolicyID": POLICY_ID, "TimestampInt": str(1791504000000000001 + index)},
        "Payload": {"Action": "observe-synthetic", "Ordinal": str(index),
                    "Text": "証拠 é e\u0301 😀", "Flags": [True, False, None],
                    "OrderingProbe": {"\ue000": "bmp", "😀": "astral"}},
        "PolicyIdentification": {"PolicyID": POLICY_ID} if index % 2 == 0 else None,
        "ChainMode": "start" if previous is None else "linked",
        "PreviousEventHash": previous,
    }


def event_statement(e):
    return {"ContractID": c.CONTRACT, **c.SCHEMES,
            "SignatureScheme": "ed25519-event-v0", "SignatureAlgorithm": "Ed25519",
            "EventHash": c.event_hash(e),
            **{key: e["Header"][key] for key in ("EventID", "ProducerID", "StreamID")},
            "KeyID": "urn:vcp-research:key:event"}


def anchor(events):
    return {"ContractID": c.CONTRACT, **c.SCHEMES,
            "TreeScheme": "rfc6962-sha256-digest-leaf-v0", "HashAlgorithm": "SHA-256",
            "SignatureScheme": "ed25519-anchor-v0", "SignatureAlgorithm": "Ed25519",
            "AnchorRecordID": "urn:vcp-research:anchor:0001", "ProducerID": PRODUCER,
            "StreamID": STREAM, "BatchID": "urn:vcp-research:batch:0001",
            "KeyID": "urn:vcp-research:key:anchor",
            "MerkleRoot": "sha256:" + c.tree([c.digest_bytes(c.event_hash(e)) for e in events]).hex(),
            "EventCount": str(len(events)), "FirstEventID": events[0]["Header"]["EventID"],
            "LastEventID": events[-1]["Header"]["EventID"],
            "PolicyID": POLICY_ID, "PolicyDigest": c.digest_text(POLICY),
            "RecordedAtNs": "1791504000000000999",
            "IntendedAnchorTarget": {"Type": "synthetic-unconnected",
                                     "Identifier": "urn:vcp-research:target:unconnected"}}


def changed(value):
    if value is None:
        return "not-null"
    if type(value) is bool:
        return not value
    if type(value) is str:
        if value.startswith("sha256:"):
            return "sha256:" + ("0" if value[7] != "0" else "1") + value[8:]
        if value.isascii() and value.isdigit():
            return str(int(value) + 1)
        return value + "-changed"
    raise ValueError("not a scalar")


def leaf_paths(value, prefix=()):
    if type(value) is dict:
        for key, item in value.items():
            yield from leaf_paths(item, prefix + (key,))
    elif type(value) is list:
        for index, item in enumerate(value):
            yield from leaf_paths(item, prefix + (str(index),))
    else:
        yield prefix, value


def replace(obj, path, value):
    obj = copy.deepcopy(obj)
    current = obj
    for part in path[:-1]:
        current = current[int(part)] if type(current) is list else current[part]
    key = int(path[-1]) if type(current) is list else path[-1]
    current[key] = value
    return obj


def numeric_vectors():
    values = ["0", "1", "2147483646", "2147483647", "2147483648",
              "9007199254740991", "9007199254740992", "9007199254740993",
              "1791504000000000000", "1791504000000000001",
              "9223372036854775806", "9223372036854775807", "9223372036854775808",
              "", "00", "01", "+1", "-1", "-0", " 1", "1 ", "1\n", "1\r", "1\t",
              "1\u2028", "1\u2029", "1.0", "1e0", "１", "١"]
    # Each field's independently stated expected set, not computed by decimal().
    allowed = {
        "Header.TimestampInt": set(values[:12]),
        "RecordedAtNs": set(values[:12]),
        "EventCount": set(values[1:4]),
        "LeafIndex(count=3)": {"0", "1"},
    }
    result = []
    for field, accepted in allowed.items():
        for value in values + ["2", "3"]:
            expectation = value in accepted or (value in ("2", "3") and field != "LeafIndex(count=3)") or (value == "2" and field == "LeafIndex(count=3)")
            result.append({"field": field, "input_json": json.dumps(value, ensure_ascii=False),
                           "expected": "accept" if expectation else "reject"})
        for raw in ("true", "false", "null", "0", "1", "1.0", "1e0", "1791504000000000001", "[]", "{}"):
            result.append({"field": field, "input_json": raw, "expected": "reject"})
    return result


def build():
    events, previous = [], None
    for index in range(max(SIZES)):
        item = event(index, previous)
        previous = c.event_hash(item)
        events.append({"input": item, "event_hash": previous,
                       "jcs_utf8": c.jcs(item).decode("utf-8"),
                       "preimage_hex": c.event_preimage(item).hex()})
    no_chain = copy.deepcopy(events[0]["input"])
    no_chain.update(ChainMode="none", PolicyIdentification=None)
    special = [no_chain]
    for ns in ("0", "9007199254740991", "9007199254740992", "9007199254740993", str(c.MAX_NS)):
        special.append(replace(no_chain, ["Header", "TimestampInt"], ns))
    extra = [{"input": e, "event_hash": c.event_hash(e), "jcs_utf8": c.jcs(e).decode(),
              "preimage_hex": c.event_preimage(e).hex()} for e in special]
    statements = []
    for i in range(3):
        s = event_statement(events[i]["input"])
        statements.append({"event_index": str(i), "statement": s,
                           "jcs_utf8": c.jcs(s).decode(),
                           "preimage_hex": c.signature_preimage(s, "event_signature").hex(),
                           "signature": sign(s, "event_signature", "event")})
    a = anchor([e["input"] for e in events[:3]])
    a_sig = sign(a, "anchor_signature", "anchor")
    a_vector = {"statement": a, "jcs_utf8": c.jcs(a).decode(),
                "preimage_hex": c.signature_preimage(a, "anchor_signature").hex(),
                "signature": a_sig,
                "external_preimage_hex": c.external_preimage(a, a_sig).hex(),
                "external_commitment": c.digest_text(c.external_preimage(a, a_sig)),
                "external_receipt_status": "unknown"}
    mutations = []
    for kind, original in (("anchor_signature", a), ("event_signature", statements[0]["statement"])):
        for field_path, value in leaf_paths(original):
            mutated = replace(original, field_path, changed(value))
            validator = c.anchor_validate if kind == "anchor_signature" else c.event_statement_validate
            try:
                validator(mutated)
                fmt = "pass"
            except c.Rejected:
                fmt = "reject"
            mutations.append({"kind": kind, "path": list(field_path), "replacement": changed(value),
                              "expected_format": fmt, "expected_original_signature": "fail"})
    # Correctly signed but semantically inconsistent assertions: signature pass is
    # deliberately NOT sufficient. Each is a new synthetic record, not a repair.
    inconsistent = []
    for field, replacement in {
        "EventCount": "2", "FirstEventID": "urn:vcp-research:event:9999",
        "LastEventID": "urn:vcp-research:event:9999", "PolicyID": "urn:vcp-research:policy:other",
        "PolicyDigest": "sha256:" + "0" * 64, "MerkleRoot": "sha256:" + "0" * 64,
        "ProducerID": "urn:vcp-research:producer:other", "StreamID": "urn:vcp-research:stream:other",
    }.items():
        s = replace(a, [field], replacement)
        inconsistent.append({"changed_field": field, "statement": s,
                             "signature": sign(s, "anchor_signature", "anchor"),
                             "expected_raw_signature": "pass", "expected_batch_binding": "reject"})
    hash_mutations = [{"path": list(p), "replacement": changed(v), "expected_hash_equal": False}
                      for p, v in leaf_paths(events[0]["input"])]
    hashes = [c.digest_bytes(e["event_hash"]) for e in events]
    merkle = [{"count": str(n), "root_hex": c.tree(hashes[:n]).hex(),
               "proofs": [{"index": str(i), "nodes_hex": [p.hex() for p in c.path(hashes[:n], i)]}
                          for i in range(n)]} for n in SIZES]
    output = {
        "status": "unadopted; independent third-party reproduction unestablished",
        "contract_id": c.CONTRACT,
        "domain_prefixes_hex": {name: value.hex() for name, value in c.DOMAINS.items()},
        "public_test_keys": {role: {"PUBLIC_TEST_SEED_HEX": seed.hex(),
                                   "public_key_hex": Ed25519PrivateKey.from_private_bytes(seed).public_key().public_bytes_raw().hex()}
                             for role, seed in KEYS.items()},
        "policy_bytes_hex": POLICY.hex(), "policy_digest": c.digest_text(POLICY),
        "events": events, "extra_events": extra, "event_signatures": statements,
        "anchor": a_vector, "signature_mutations": mutations,
        "event_hash_mutations": hash_mutations, "signed_inconsistencies": inconsistent,
        "numeric_vectors": numeric_vectors(),
        "invalid_json": ['{"a":null,"a":true}', '{"a":{"x":"1","x":"2"}}', '{"a":"x","\\u0061":"y"}',
                         '{"text":"\\ud800"}', '{"\\udfff":"x"}', '{"x":NaN}',
                         '{"x":Infinity}', '{"x":1}', '{"x":1.0}', '{"x":-0}',
                         '{"x":"ok",}', '\ufeff{"x":"ok"}'],
        "empty_root_hex": c.sha(b"").hex(),
    }
    return output, merkle


def encoded_files():
    bundle, merkle = build()
    # One Merkle tree per JSONL line; ordered proofs use digest inputs from events.
    return {"vectors.json": (json.dumps(bundle, ensure_ascii=False, indent=2) + "\n").encode(),
            "merkle-vectors.jsonl": ("\n".join(json.dumps(v, separators=(",", ":")) for v in merkle) + "\n").encode()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=False)
    for name, data in encoded_files().items():
        (args.output_directory / name).write_bytes(data)
    print("Generated PUBLIC SYNTHETIC TEST DATA only:", args.output_directory)
