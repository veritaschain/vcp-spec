# Replaying seven Receipt-context cases

The 27 November 2026 VSO experiment verifies two ordinary, synthetic Receipts for the same Signed Statement. One Receipt was issued under the retired fixture key K1 and the other under the current fixture key K2. Python and Go read the same fixed bytes, independently compute the inclusion result, and select authorized context from a local trust input. Both implementations and the fixture generator originate from this experiment. Independent external reproduction remains open in [issue 37](https://github.com/veritaschain/vcp-spec/issues/37).

## Observations

| Case | Evidence available to the verifier | Observed in both implementations |
|---|---|---|
| CX-01 | A1 rule record and K1 authorization | Verified inclusion under the service-signed root. |
| CX-09 | The above historical K1 evidence is retained alongside current K2 | Verified the original Receipt using the retired K1 key. |
| CX-10 | Only K2 authorization is available for the K1 Receipt | Insufficient key context. |
| CX-17 | Same Receipt and evidence as CX-01 | Verified inclusion. Source completeness and history consistency remain unassessed. |
| CX-19 | One applicable A1 rule record and both per-Receipt key authorizations | Verified both distinct Receipts under the same root. |
| CX-21 | Only K1 authorization is available for the reissued K2 Receipt | Insufficient key context. |
| CX-22 | The supported preprocessing and the same entry match two authenticated rule epochs | Ambiguous rule context. The verifier stops before choosing a rule or checking the Receipt signature. |

There are eight assessments across seven cases. Five verify inclusion, two lack the signing-key authorization and one lacks a unique applicable rule. Each verifier reports the same five additional properties as unassessed: source completeness, history consistency, issuance time, position and size, and local VCP batch integrity. The other 15 rows of the [case matrix](../cases.md) remain pending. The [Python transcript](results/python.json) and [Go transcript](results/go.json) contain the actual results.

## Fixed inputs and trust

- [bundle.json](bundle.json) contains the original hex-encoded COSE messages: two issuer-signed Statements (the primary and sibling leaves) and two detached service Receipts for the primary leaf. It also contains the signed bodies of two archive rule records and two key-authorization records.
- [trust.json](trust.json) is a separate relying-party fixture. It fixes the service, issuer key, and independently provisioned roles for the archive and the key authority. It selects which signed records are available for each case. This file and the documents it authenticates are synthetic. The fixture generator uses public deterministic test seeds for every key.
- The archive signs the mapping from service and SHA-256 of the prepared primary entry to a rule and epoch. A different authority signs a key, its status and its authorization for one specific Receipt digest. These records do not establish issuance time. The dated run, checked-in preprocessing code and [input manifest](inputs.sha256) supply the experiment's assessment context. Full rule-document digest negotiation, revocation handling and an operational trust-update channel are outside this replay.
- [expected.json](expected.json) records the seven case expectations from the candidate matrix separately from the generation of inputs. Both implementations read their applicable rule and keys from the authenticated records. Python checks the expected case labels after constructing its report. Go uses the COSE library to verify signatures and computes its report without reading the oracle.

For this restricted A1 input, the retained CBOR elements use definite byte strings and the unprotected Statement map is already empty. Python verifies the issuer signature and uses the original Statement bytes as the prepared entry E. Go verifies the issuer signature, copies the original encoded protected, payload and signature elements and writes an empty map at the unprotected position. The Proof is an ordinary two-leaf RFC9162_SHA256 inclusion proof. Both implementations hash the prepared entries with the leaf prefix and verify the detached service signature over the computed root. This corpus covers the fixed bytes only. It does not exercise other CBOR encodings, general tree shapes or the A2 entry construction.

| Output field | Observed hexadecimal SHA-256 value |
|---|---|
| SHA-256(E), used by the archive | `9b93f0314b73610356144f53cb725e04772ef7eb9d8807c0aac7b2e985a1ebbc` |
| Leaf, SHA-256(0x00 &#124;&#124; E) | `730d2c267414f02a35e86eb26d62f29e19b8ea19af2b69f97f5dad00409940a3` |
| Merkle root (the detached signed payload) | `c64e66d077ff1987c94c2d2935a6a1e5fadefc19d24c28a3ca992620d62a868a` |

The tree-size and leaf-index inputs describe the shape checked by this fixture. The report makes an inclusion claim under the service-signed root. Separate authenticated evidence would be needed to extend it to a claim about position or size, time, log history or completeness.

## Reproduce

Start in this directory. The recorded run used CPython 3.12.14 and Go 1.27.4 on Linux. Python dependencies are pinned in [requirements.txt](requirements.txt). Go dependencies are recorded in [go.mod](go/go.mod) and [go.sum](go/go.sum). The replay itself needs no live service. The initial dependency installation needs a package source or a populated local cache.

```sh
work=$(mktemp -d)
python3 -m venv "$work/venv"
"$work/venv/bin/python" -m pip install -r requirements.txt
sha256sum -c inputs.sha256
"$work/venv/bin/python" make_fixtures.py --check
"$work/venv/bin/python" replay_python.py > "$work/python.json"
(cd go && go run -mod=readonly . ..) > "$work/go.json"
"$work/venv/bin/python" compare.py "$work/python.json" "$work/go.json"
```

The final check compares the full parsed reports with one another, the cases with the expected labels, and both run outputs with the archived transcripts. A difference exits with an error. The experiment demonstrates first-party agreement on this corpus. The [candidate](../README.md) remains under discussion.
