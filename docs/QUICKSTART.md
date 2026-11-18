# VeritasChain Protocol (VCP) — offline quick start

**Updated 18 November 2026.** Use the first-party
[vcp-sdk offline core](https://github.com/veritaschain/vcp-sdk) to create and
inspect VCP v1.2 events locally. This path needs no hosted Explorer account or
API key. The SDK is a pre-release implementation with documented interpretations;
this is not a protocol-conformance or certification test.

## 1. Install the documented source snapshot

Python 3.10+ and Git are required. Installation downloads the source and its
dependencies; event generation and the checks below run locally after installation.

Use SDK commit [`0832f1d84af9b130db6a17d36c343a8abd7002a8`](https://github.com/veritaschain/vcp-sdk/commit/0832f1d84af9b130db6a17d36c343a8abd7002a8).
It includes the `vcp seal` checks that reject output paths pointing to the input,
private-key file or other output. The previous installation snapshot (`8eadded87`)
and the historical `v0.1.0` tag lack these checks. Package metadata still reports
`0.1.0`. Record the full source commit when reporting results and use the
[SDK installation guide](https://github.com/veritaschain/vcp-sdk/blob/4d26bac80c9ffe059c92336ffabec19b722d66f2/README.md#install)
for installation in other languages. The packages are distributed from GitHub only.

```bash
python -m venv .venv
# POSIX shell; on Windows use .venv\Scripts\activate
. .venv/bin/activate
python -m pip install --force-reinstall "git+https://github.com/veritaschain/vcp-sdk.git@0832f1d84af9b130db6a17d36c343a8abd7002a8#subdirectory=python"
```

Before comparing evidence with another implementation, read the snapshot's
[interpretations](https://github.com/veritaschain/vcp-sdk/blob/0832f1d84af9b130db6a17d36c343a8abd7002a8/INTERPRETATIONS.md)
and [quick-start instructions](https://github.com/veritaschain/vcp-sdk/blob/0832f1d84af9b130db6a17d36c343a8abd7002a8/README.md#quick-start-python).

## 2. Create and inspect a local batch

Save the following as `local_vcp_demo.py` and run `python local_vcp_demo.py`:

```python
import veritaschain_vcp as vcp

key = vcp.generate_key()
producer = vcp.Producer(
    key, actor_id="demo-01", chain_id="demo-chain",
    policy_id="org.example:offline-demo", use_prev_hash=True,
)
producer.create("INIT", {"VCP-GOV": {"AlgoID": "demo", "AlgoVersion": "0.1"}})
producer.create("ORD", {"VCP-TRADE": {
    "Symbol": "USDJPY", "Side": "BUY", "Price": "151.230", "Quantity": "100000",
}})
batch, record = producer.close_batch()
report = vcp.verify_batch(
    batch.events, record, key.verify_key, require_sign_algo="ED25519",
)
print(report.status)
for check in report.failed():
    print(check.name, check.status, check.reason)
```

The full result is expected to remain **INDETERMINATE**, because this demo
supplies no externally verified anchor. That is not a pass. The local signature
check uses the key generated in the same process; it does not establish an
external party's identity. The SDK checks selected integrity and structure rules,
not the complete JSON Schema or all VCP requirements. It neither submits a trade
nor sends events to a hosted API.

## 3. Further evaluation

- [TypeScript quick start](https://github.com/veritaschain/vcp-sdk/blob/0832f1d84af9b130db6a17d36c343a8abd7002a8/README.md#quick-start-typescript)
  uses the same source snapshot. Preserve exact integers with the SDK parser.
- [VCP v1.2 known issues](../spec/v1.2/README.md#known-issues-in-v12-informative)
  distinguish published requirements from unresolved technical contradictions.
- External anchoring and anchor verification require a separately selected and
  configured mechanism. The offline library does not contact anchor services.

## Historical hosted-API examples

The previous [hosted Explorer quick-start guide at the reviewed baseline](https://github.com/veritaschain/vcp-spec/blob/5b042c73adc294e503f07451a18345165341372c/docs/QUICKSTART.md)
and the repository's API examples are historical interface illustrations. They
assume service access and an API key; no self-service provisioning is established
by this document. They are not the prerequisites for the offline path above.
