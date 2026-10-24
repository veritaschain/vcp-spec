"""UNADOPTED synthetic byte-contract candidate; not a native VCP verifier.

This module has no network/production integration. Key/time authorization,
external receipts, complete schema mapping and submission sufficiency are NOT
implemented. A successful byte check does not imply any of those properties.
"""
import base64
import hashlib
import json
import re

import rfc8785
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

CONTRACT = "urn:vcp-research:integrity-byte-contract:2026-10-24:v0"
SCHEMES = {
    "ProtocolVersion": "unassigned-research-v0",
    "EventHashScheme": "jcs-object-sha256-v0",
    "NumericEncoding": "decimal-string-v0",
}
DOMAINS = {
    "event": b"VCP-RESEARCH-20261024-V0/EVENT\x00",
    "event_signature": b"VCP-RESEARCH-20261024-V0/EVENT-SIGNATURE\x00",
    "anchor_signature": b"VCP-RESEARCH-20261024-V0/ANCHOR-SIGNATURE\x00",
    "external": b"VCP-RESEARCH-20261024-V0/EXTERNAL-COMMITMENT\x00",
}
MAX_NS = 9223372036854775807
MAX_COUNT = 2147483647
ID_RE = re.compile(r"urn:vcp-research:[a-z0-9][a-z0-9:._-]{0,127}")
DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}")


class Rejected(ValueError):
    """Outside this closed synthetic candidate or malformed evidence."""


def require(condition, reason):
    if not condition:
        raise Rejected(reason)


def sha(data):
    return hashlib.sha256(data).digest()


def digest_text(data):
    return "sha256:" + sha(data).hex()


def digest_bytes(value):
    require(type(value) is str and DIGEST_RE.fullmatch(value), "digest spelling")
    return bytes.fromhex(value[7:])


def decimal(value, minimum, maximum):
    require(type(value) is str and len(value) <= 19 and
            re.fullmatch(r"0|[1-9][0-9]*", value), "decimal spelling/type")
    result = int(value)
    require(minimum <= result <= maximum, "decimal range")
    return result


def identifier(value):
    require(type(value) is str and ID_RE.fullmatch(value), "synthetic identifier")


def exact(obj, fields):
    require(type(obj) is dict and set(obj) == set(fields.split()), "object fields")


def restricted_json(value):
    """Deliberately number-free JSON subset, including arbitrary Payload bytes.

    Payload values are committed, NOT interpreted as authorization or finance.
    Unknown outer/header/security fields are rejected separately, not dropped.
    """
    if value is None or type(value) is bool:
        return
    if type(value) is str:
        require(not any(0xD800 <= ord(c) <= 0xDFFF for c in value), "lone surrogate")
    elif type(value) is list:
        for item in value:
            restricted_json(item)
    elif type(value) is dict:
        for key, item in value.items():
            require(type(key) is str, "non-string key")
            restricted_json(key)
            restricted_json(item)
    else:
        raise Rejected("JSON numbers/non-JSON values unsupported in candidate")


def jcs(obj):
    restricted_json(obj)
    return rfc8785.dumps(obj)


def load_json(text):
    # json.loads(bytes) otherwise auto-detects UTF-16/32 and accepts a BOM.
    # This candidate has one transport encoding, not an encoding fallback.
    require(type(text) in (str, bytes), "JSON source must be text or UTF-8 bytes")
    if type(text) is bytes:
        try:
            text = text.decode("utf-8")
        except UnicodeError as exc:
            raise Rejected("JSON source must be UTF-8") from exc
    require(not text.startswith("\ufeff"), "JSON source BOM")

    def pairs(items):
        obj = {}
        for key, value in items:
            require(key not in obj, "duplicate key")
            obj[key] = value
        return obj

    def constant(_):
        raise Rejected("non-JSON constant")

    try:
        obj = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, UnicodeError) as exc:
        raise Rejected(str(exc)) from exc
    restricted_json(obj)
    return obj


def event_validate(event):
    exact(event, "ContractID EventHashAlgorithm Header Payload PolicyIdentification ChainMode PreviousEventHash")
    require(event["ContractID"] == CONTRACT and event["EventHashAlgorithm"] == "SHA-256", "event scheme")
    h = event["Header"]
    exact(h, "EventID ProducerID StreamID PolicyID TimestampInt")
    for key in ("EventID", "ProducerID", "StreamID", "PolicyID"):
        identifier(h[key])
    decimal(h["TimestampInt"], 0, MAX_NS)
    require(type(event["Payload"]) is dict, "payload object")
    policy = event["PolicyIdentification"]
    if policy is not None:
        exact(policy, "PolicyID")
        require(policy["PolicyID"] == h["PolicyID"], "event policy binding")
    mode = event["ChainMode"]
    require(mode in ("none", "start", "linked"), "chain mode")
    if mode == "linked":
        digest_bytes(event["PreviousEventHash"])
    else:
        require(event["PreviousEventHash"] is None, "unexpected predecessor")
    jcs(event)


def event_preimage(event):
    event_validate(event)
    return DOMAINS["event"] + jcs(event)


def event_hash(event):
    return digest_text(event_preimage(event))


def scheme_validate(obj):
    require(obj["ContractID"] == CONTRACT, "contract")
    for key, value in SCHEMES.items():
        require(obj[key] == value, "scheme " + key)
    require(obj["SignatureAlgorithm"] == "Ed25519", "signature algorithm")
    for key in ("ProducerID", "StreamID", "KeyID"):
        identifier(obj[key])


def event_statement_validate(obj):
    exact(obj, "ContractID ProtocolVersion EventHashScheme NumericEncoding SignatureScheme SignatureAlgorithm EventHash EventID ProducerID StreamID KeyID")
    scheme_validate(obj)
    require(obj["SignatureScheme"] == "ed25519-event-v0", "signature scheme")
    identifier(obj["EventID"])
    digest_bytes(obj["EventHash"])
    jcs(obj)


def anchor_validate(obj):
    exact(obj, "ContractID ProtocolVersion EventHashScheme NumericEncoding TreeScheme HashAlgorithm SignatureScheme SignatureAlgorithm AnchorRecordID ProducerID StreamID BatchID KeyID MerkleRoot EventCount FirstEventID LastEventID PolicyID PolicyDigest RecordedAtNs IntendedAnchorTarget")
    scheme_validate(obj)
    require(obj["TreeScheme"] == "rfc6962-sha256-digest-leaf-v0" and
            obj["HashAlgorithm"] == "SHA-256" and
            obj["SignatureScheme"] == "ed25519-anchor-v0", "anchor scheme")
    for key in ("AnchorRecordID", "BatchID", "FirstEventID", "LastEventID", "PolicyID"):
        identifier(obj[key])
    digest_bytes(obj["MerkleRoot"])
    digest_bytes(obj["PolicyDigest"])
    decimal(obj["EventCount"], 1, MAX_COUNT)
    decimal(obj["RecordedAtNs"], 0, MAX_NS)
    target = obj["IntendedAnchorTarget"]
    exact(target, "Type Identifier")
    require(target["Type"] == "synthetic-unconnected", "no external adapter")
    identifier(target["Identifier"])
    jcs(obj)


def signature_preimage(statement, kind):
    if kind == "event_signature":
        event_statement_validate(statement)
    elif kind == "anchor_signature":
        anchor_validate(statement)
    else:
        raise Rejected("unknown signature kind")
    return DOMAINS[kind] + jcs(statement)


def signature_bytes(value):
    require(type(value) is str, "signature type")
    try:
        result = base64.b64decode(value, validate=True)
    except (ValueError, UnicodeError) as exc:
        raise Rejected("signature base64") from exc
    require(len(result) == 64 and base64.b64encode(result).decode("ascii") == value,
            "signature canonical spelling/length")
    return result


def raw_verify(public_key_hex, signature, message):
    try:
        sig = signature_bytes(signature)
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex)).verify(sig, message)
        return True
    except (InvalidSignature, ValueError, UnicodeError):
        return False


def signature_check(statement, signature, kind, supplied_trust):
    """Trust is a separate caller-owned fixture, never read from the statement.

    Only synthetic role/producer/stream/key binding is checked. Real key validity,
    revocation and trusted time are deliberately not assessed by this function.
    """
    message = signature_preimage(statement, kind)
    signature_bytes(signature)
    identity = (kind, statement["ProducerID"], statement["StreamID"], statement["KeyID"])
    public_key = supplied_trust.get(identity)
    if public_key is None:
        return "unknown"
    return "pass" if raw_verify(public_key, signature, message) else "fail"


def event_binding(event, statement):
    event_statement_validate(statement)
    require(statement["EventHash"] == event_hash(event), "event digest mismatch")
    for key in ("EventID", "ProducerID", "StreamID"):
        require(statement[key] == event["Header"][key], "event identity mismatch")


def split(n):
    return 1 << ((n - 1).bit_length() - 1)


def tree(digests):
    require(all(type(d) is bytes and len(d) == 32 for d in digests), "leaf digest length")
    if not digests:
        return sha(b"")
    if len(digests) == 1:
        return sha(b"\x00" + digests[0])
    k = split(len(digests))
    return sha(b"\x01" + tree(digests[:k]) + tree(digests[k:]))


def path(digests, index):
    require(type(index) is int and 0 <= index < len(digests), "path index")
    if len(digests) == 1:
        return []
    k = split(len(digests))
    if index < k:
        return path(digests[:k], index) + [tree(digests[k:])]
    return path(digests[k:], index - k) + [tree(digests[:k])]


def membership(digest, index_text, count_text, proof, expected_root):
    """Size-aware iterative fold, separate from the recursive path constructor."""
    count = decimal(count_text, 1, MAX_COUNT)
    index = decimal(index_text, 0, count - 1)
    require(type(digest) is bytes and len(digest) == 32, "leaf digest length")
    require(type(expected_root) is bytes and len(expected_root) == 32, "root length")
    require(type(proof) is list and all(type(p) is bytes and len(p) == 32 for p in proof), "proof node length")
    fn, sn, root = index, count - 1, sha(b"\x00" + digest)
    for sibling in proof:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            root = sha(b"\x01" + sibling + root)
            while fn != 0 and not fn & 1:
                fn >>= 1
                sn >>= 1
        else:
            root = sha(b"\x01" + root + sibling)
        fn >>= 1
        sn >>= 1
    return sn == 0 and root == expected_root


def batch_binding(events, anchor, policy_bytes):
    """Full-list consistency ONLY; does not verify signatures or external capture."""
    anchor_validate(anchor)
    require(len(events) == decimal(anchor["EventCount"], 1, MAX_COUNT), "batch count")
    digests = [digest_bytes(event_hash(e)) for e in events]
    require(tree(digests) == digest_bytes(anchor["MerkleRoot"]), "batch root")
    ids = [e["Header"]["EventID"] for e in events]
    require(len(set(ids)) == len(ids), "duplicate event IDs")
    require(ids[0] == anchor["FirstEventID"] and ids[-1] == anchor["LastEventID"], "batch endpoints")
    for event in events:
        for key in ("ProducerID", "StreamID", "PolicyID"):
            require(event["Header"][key] == anchor[key], "batch context " + key)
    require(digest_text(policy_bytes) == anchor["PolicyDigest"], "policy bytes")


def external_preimage(anchor, signature):
    anchor_validate(anchor)
    signature_bytes(signature)
    return DOMAINS["external"] + jcs({"AnchorStatement": anchor, "Signature": signature})


def aggregate_required(statuses):
    require(bool(statuses) and all(s in ("pass", "fail", "unknown") for s in statuses), "statuses")
    return "fail" if "fail" in statuses else "unknown" if "unknown" in statuses else "pass"
