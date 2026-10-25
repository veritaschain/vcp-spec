"""Read-only composition of two pinned, UNADOPTED research implementations."""
import base64
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "1131901d0b83f87c1c60674697574a60cc88fee1"
EXPERIMENT = "urn:vcp-research:numeric-byte-binding:2026-10-25:v0"
BYTE_DIR = "proposals/integrity-2026-10-24/byte-contract-candidate-v0"
NUMERIC_DIR = "experiments/numeric-representation-candidate-v0"
SOURCE_FILES = {
    BYTE_DIR + "/contract.py", BYTE_DIR + "/README.md", BYTE_DIR + "/requirements.txt",
    NUMERIC_DIR + "/checker.py", NUMERIC_DIR + "/data/field-map.json", NUMERIC_DIR + "/README.md",
    "proposals/numeric-fields-2026-10-25/inventory.json",
    "proposals/numeric-fields-2026-10-25/README.md",
}
DEPENDENCIES = {"cryptography": "50.0.2", "rfc8785": "0.1.4"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def pairs(items):
        value = {}
        for key, child in items:
            if key in value:
                raise ValueError("duplicate JSON key")
            value[key] = child
        return value

    def constant(_):
        raise ValueError("non-JSON constant")

    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)


def sources():
    data = strict_json((HERE / "sources.json").read_bytes())
    if (set(data) != {"source_commit", "status", "files"} or data["source_commit"] != BASE or
            data["status"] != "UNADOPTED" or set(data["files"]) != SOURCE_FILES):
        raise ValueError("source manifest context/file inventory mismatch")
    for name, expected in data["files"].items():
        if sha((ROOT / name).read_bytes()) != expected:
            raise ValueError("pinned source hash mismatch: " + name)
    for name, expected in DEPENDENCIES.items():
        if importlib.metadata.version(name) != expected:
            raise ValueError("dependency version mismatch: " + name)
    return data


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Validate source fingerprints before importing the two existing modules.
SOURCE_MANIFEST = sources()
byte = load("pinned_byte_contract", BYTE_DIR + "/contract.py")
numeric = load("pinned_numeric_checker", NUMERIC_DIR + "/checker.py")
FIELDS = numeric.load_fields()

PRODUCER = "urn:vcp-research:producer:numeric-demo"
STREAM = "urn:vcp-research:stream:numeric-demo"
POLICY_ID = "urn:vcp-research:policy:numeric-binding-v0"
KEY_IDS = {role: "urn:vcp-research:key:numeric-" + role for role in ("event", "anchor")}

# PUBLIC, SYNTHETIC TEST MATERIAL ONLY. Never authorize a real record with these.
SEEDS = {role: hashlib.sha256(("PUBLIC TEST MATERIAL numeric-byte-binding-v0 " + role).encode()).digest()
         for role in ("event", "anchor")}


def private_key(role):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    return Ed25519PrivateKey.from_private_bytes(SEEDS[role])


PUBLIC_KEYS = {role: private_key(role).public_key().public_bytes_raw().hex() for role in SEEDS}
TRUST = {(role + "_signature", PRODUCER, STREAM, KEY_IDS[role]): PUBLIC_KEYS[role] for role in SEEDS}

POLICY = {
    "ExperimentID": EXPERIMENT, "PolicyID": POLICY_ID, "SourceCommit": BASE,
    "NumericProposal": "vcp-numeric-experiment-v0",
    "ByteContract": byte.CONTRACT,
    "Units": {"TimestampInt": "unix_ns", "RecordedAtNs": "unix_ns", "Duration": "s",
              "Tolerance": "ms", "Confidence": "ratio", "EventCount": "batch_events"},
    "TimeBasis": "unix_no_leap",
}
POLICY_BYTES = byte.jcs(POLICY)


def sign(statement, role):
    message = byte.signature_preimage(statement, role + "_signature")
    return base64.b64encode(private_key(role).sign(message)).decode("ascii")


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=True, indent=2, allow_nan=False) + "\n").encode()


def bundle_bytes(data, list_key):
    meta = {k: v for k, v in data.items() if k != list_key}
    start = json.dumps(meta, ensure_ascii=True, indent=2)[:-2]
    rows = ",\n".join("    " + json.dumps(r, ensure_ascii=True, separators=(",", ":"), allow_nan=False) for r in data[list_key])
    return (start + ',\n  "' + list_key + '": [\n' + rows + '\n  ]\n}\n').encode()
