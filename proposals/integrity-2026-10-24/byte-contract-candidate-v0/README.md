# Integrity byte-contract candidate v0 and synthetic vectors

**Status: unadopted research proposal; not effective.** No formal proposal number
or target VCP release is assigned. **Independent third-party reproduction remains
unestablished.** Merging this folder would retain an experiment, not adopt a
normative rule, certify a product or establish VAP/VCP conformance.

This is a separate follow-up to the [normative-change draft at its merged
revision](https://github.com/veritaschain/vcp-spec/blob/9b88e318aeb9575de66047ed49c8ab86c2879487/proposals/integrity-2026-10-24/normative-change-draft.md).
That document's open decisions and historical statement that it supplied no
implementation/tests are not rewritten. This folder supplies **one closed,
synthetic candidate and a subset of the requested evidence**, not completion of
all its acceptance gates. The [technical-errata draft](../technical-errata-draft.md)
records legacy observations separately.

Only new files in this folder are introduced. Existing specification text,
schemas, implementations, signed data, fixed distributions, tags, DOC-SYNC and K3
remain untouched. The VAP research verifier, gates and OS experiment are not
invoked or modified. This is not a converter for existing signed records.

## 1. Decisions made for this experiment, and decisions still open

“Selected below” means selected for reproducible **synthetic review**, not
approved for a release. The identifiers explicitly say research and v0; they
are not VCP registry allocations or a new profile/version announcement.

| Topic | Concrete candidate here | Still required before adoption or implementation integration |
|---|---|---|
| Event hash input | Explicit JCS object; exact fields and four domain prefixes below | Select this option through change control; map every real Header, module, Security and extension field |
| Event signatures | Separate protected event statement binds digest, identity, stream, key and schemes | Map existing event signatures, delegated identities, SCITT/COSE and algorithm agility; no requirement is waived |
| Anchor signatures | Sign the whole protected statement, not the root alone | Production identity grammar, key lifecycle, clock/revocation policy and authorized corrections |
| Numbers | Decimal strings; four field classes and exact ranges below | Complete per-field body/schema/annex inventory, timestamps/UTC/leap seconds and migration |
| Merkle trees | RFC split rule; digest-byte leaves; authenticated size/index | Deployment limits, resource bounds and migration from legacy roots/proofs |
| External commitment | Hash the signed statement plus signature; receipts excluded | Actual receipt formats, service trust, target matching, time/finality and recovery/failover integration |
| Disclosure and scope | Full supplied-list consistency is checked separately from signatures | Partial disclosure, expected-set derivation, withheld/unavailable items and submission sufficiency |
| Chain | Distinct none/start/linked encodings; local predecessor comparison | Restart authority, recovery, sequence/order policies and unavailable predecessors |
| Cross-language evidence | Python and Node recompute the same bytes using separate code paths | Independent implementers/review, full format/trust validators and externally managed fresh runs |
| Governance/migration | No adoption, release number or compatibility promise | Recorded decision; explicit old/new routing, migration plan and VAP mapping |

No “all gates passed” verdict is produced. The check report includes unassessed
items even when every covered byte test passes. Existing experimental extensions
remain unadopted; this work does not change their status.

## 2. Exact shared encodings

The experiment's `ContractID` is:

```text
urn:vcp-research:integrity-byte-contract:2026-10-24:v0
```

The following ASCII labels are followed by **exactly one byte `00`**, then the
canonical bytes. The text spelling `\0` is not part of the input. There is no
BOM, newline, length prefix or additional separator. Exact prefix hex values
also appear in `data/vectors.json`.

| Purpose | ASCII label before `00` |
|---|---|
| EventHash | `VCP-RESEARCH-20261024-V0/EVENT` |
| Event signature | `VCP-RESEARCH-20261024-V0/EVENT-SIGNATURE` |
| Anchor signature | `VCP-RESEARCH-20261024-V0/ANCHOR-SIGNATURE` |
| External commitment | `VCP-RESEARCH-20261024-V0/EXTERNAL-COMMITMENT` |

`JCS(X)` means RFC 8785 canonicalization to UTF-8. The **closed synthetic input
subset contains no JSON numbers anywhere**: objects, arrays, Unicode strings,
booleans and null are permitted subject to field rules. This deliberate
restriction avoids an unreviewed conversion of existing numeric payloads.
It is stricter than RFC 8785 and is not a statement that JCS prohibits all
integers above 2^53. In particular, an existing native VCP event is not an input
to this candidate and must not be stripped down to fit it.

Duplicate JSON keys (including escaped equivalent keys), lone surrogates,
non-JSON constants and an input BOM are rejected. Property sorting uses UTF-16
code-unit order as required by JCS. Strings are never Unicode-normalized.
No field is silently omitted, repaired, defaulted or converted. Unknown fields
are rejected in the closed outer/header/statement shapes. Payload is an opaque
object of the supported JSON subset: every key/value is committed, but it does
not grant authorization or claim native module semantics.

Digests in fields have exactly `sha256:` plus 64 lowercase hexadecimal digits.
Merkle leaf/proof/root calculations use decoded 32-byte digests. The identifiers
for events, keys, policies, producers, streams, batches and targets use the
**test-only** ASCII grammar `urn:vcp-research:[a-z0-9][a-z0-9:._-]{0,127}`
over the whole string. Real VCP UUIDs and policy identifiers need a separate
mapping; this grammar does not replace them.

## 3. Event commitment, own signature and tree

`EventCommitment` has exactly these seven mandatory members:

| Member | Candidate encoding |
|---|---|
| ContractID | Literal above |
| EventHashAlgorithm | `SHA-256` |
| Header | Exactly EventID, ProducerID, StreamID, PolicyID, TimestampInt; test identifiers and timestamp rules below |
| Payload | Entire supported synthetic object, not a field selection |
| PolicyIdentification | Explicit null, or exactly `{ "PolicyID": ... }` matching Header.PolicyID |
| ChainMode | `none`, `start` or `linked` |
| PreviousEventHash | Null for none/start; algorithm-qualified previous EventHash for linked |

```text
EventHash = SHA256(event-prefix || JCS(EventCommitment))
leaf     = SHA256(00 || decoded-EventHash)
```

The event's own computed digest/signature, proofs, receipts and transport
envelope are **not fields of EventCommitment**. Passing a native envelope with
Security fields is rejected; no automatic projection of it is provided.
Authorization signatures inside Payload, if supplied as opaque strings, remain
content. None/start have different bytes even with the same null predecessor.
Linked events commit the predecessor once, rather than also appending its hex.
Checking adjacent digests does not authorize a restart or establish full history.

The candidate's protected event-signature statement has exactly:

```text
ContractID, ProtocolVersion, EventHashScheme, NumericEncoding,
SignatureScheme, SignatureAlgorithm,
EventHash, EventID, ProducerID, StreamID, KeyID
```

Constants are `ProtocolVersion=unassigned-research-v0`,
`EventHashScheme=jcs-object-sha256-v0`, `NumericEncoding=decimal-string-v0`,
`SignatureScheme=ed25519-event-v0` and `SignatureAlgorithm=Ed25519`.
Other fields use the grammars above. EventID/ProducerID/StreamID must match the
committed Header, and EventHash must be recomputed from the event.

Ed25519 signs `event-signature-prefix || JCS(statement)` directly, with no
extra prehash. This is ordinary Ed25519 over a domain-prefixed message, **not**
the Ed25519ctx or Ed25519ph variants. Signatures are canonical padded standard
base64 of 64 bytes, with no whitespace or alternate spelling. Event statement
and signature are outside EventCommitment. Anchor signing cannot substitute for
the event signature. This local JSON statement is not a COSE mapping.

The ordered tree uses RFC 6962 §2.1 / RFC 9162 §2.1.1:
empty root `SHA256(empty)`, single leaf above, and internal node
`SHA256(01 || left || right)` with recursive largest-power-of-two splitting.
Odd nodes are **not duplicated**. Empty-tree vectors are arithmetic evidence;
empty event-batch AnchorStatements are rejected.

Proof nodes are ordered from leaf to root and use index plus authenticated
EventCount. The checker uses RFC 9162's size-aware fold; short, surplus,
wrong-length and changed nodes do not pass. No ordering flags, sorting or
deduplication are inferred. Batch-wide duplicate EventIDs are rejected when
the complete batch is available. A proof for a subset is not proof of delivery
of the entire batch, batch-wide uniqueness or all real-world activity.

## 4. Anchor statement, trust boundary and external commitment

The protected `AnchorStatement` contains **exactly** these members; all are
required and signed. There are no unprotected interpretation fields:

| Members | Candidate values/constraints |
|---|---|
| ContractID, ProtocolVersion, EventHashScheme, NumericEncoding | Same constants as above |
| TreeScheme | `rfc6962-sha256-digest-leaf-v0` |
| HashAlgorithm | `SHA-256` |
| SignatureScheme, SignatureAlgorithm | `ed25519-anchor-v0`, `Ed25519` |
| AnchorRecordID, ProducerID, StreamID, BatchID, KeyID | Test identifier grammar |
| MerkleRoot | Algorithm-qualified SHA-256 digest |
| EventCount | Positive exact decimal string |
| FirstEventID, LastEventID | Test IDs at the first and last supplied ordered positions |
| PolicyID, PolicyDigest | Single-policy test ID and SHA-256 of exact policy bytes |
| RecordedAtNs | Signer's claimed creation time, not proven external time |
| IntendedAnchorTarget | Exactly Type=`synthetic-unconnected` and Identifier in test grammar |

```text
message   = anchor-signature-prefix || JCS(AnchorStatement)
Signature = base64(Ed25519_sign(test-anchor-private-key, message))
external  = SHA256(external-prefix ||
             JCS({"AnchorStatement": AnchorStatement, "Signature": Signature}))
```

The external object has exactly those two fields. Receipts and timestamps
returned later are outside both preimages, avoiding self-reference. PolicyDigest
is SHA-256 of the exact preserved policy bytes, **without** a domain prefix,
text decoding, newline normalization or JSON recanonicalization. The fixture
policy text is synthetic and its bytes are supplied as hex.

The full-list binding check recomputes event hashes, ordered root/count,
endpoints, duplicate IDs, shared producer/stream/policy and policy-byte digest.
It is deliberately separate from signature verification. Eight synthetic
AnchorStatements are correctly signed but inconsistent with that batch.
They pass raw signature verification and fail list binding. A separately
re-signed wrong event digest likewise fails event binding.

The public keys/seeds in the vector file are **PUBLIC TEST MATERIAL ONLY**.
They are not VSO identities or production credentials. The harness's explicit
test trust configuration binds role + producer + stream + KeyID; a key from
the record is never self-authorizing. Missing trust is unknown; a supplied
wrong key fails. Key lifetimes, revocation, actual signer authorization and
trusted time are **not assessed**. Even the test-trust pass is not a production
identity verdict. Event and anchor roles use distinct test keys.

There is **no external service or receipt adapter** here. The target is
intentionally unconnected. The vectors test only the commitment bytes and show
that a changed target changes them. External receipt status remains unknown;
receipt-to-target authentication, inclusion/finality and independent timestamping
are open, not tested successes. A future target change or metadata correction
requires a new record and retained original; no existing record is rewritten.

## 5. Exact numeric rules and remaining inventory

Whole-string ASCII syntax is `0|[1-9][0-9]*` with at most 19 digits, followed by
field-specific range validation using arbitrary-precision integers. No sign,
whitespace, Unicode digit, exponent, point, leading zero, JSON number, boolean
or null is an alternative spelling. String/number coercion is prohibited.

| Supported field | Unit | Inclusive range |
|---|---|---|
| Event Header.TimestampInt | Unix-epoch nanoseconds | 0–9223372036854775807 |
| Anchor RecordedAtNs | Unix-epoch nanoseconds | 0–9223372036854775807 |
| Anchor EventCount | Events | 1–2147483647 |
| Inclusion LeafIndex | Position | 0–authenticated EventCount minus 1 |

The ranges are proposal choices, not JCS numeric limits. Neighboring values
around 2^53, 2^31 and 2^63, and `1791504000000000000` versus
`1791504000000000001`, are retained exactly. No timestamp passes through binary64.
`TimestampISO` is rejected in this minimal shape until lexical form, Unix/UTC
conversion and leap-second handling are specified; it is not silently ignored.

The existing [v1.2 schema at b23acb2](https://github.com/veritaschain/vcp-spec/blob/b23acb266f88df81d960d36d58fb64ceaa0dd5ed/spec/v1.2/vcp-event-v1.2.json)
also contains Header.SequenceNum, SCITTAlignment.RegistrationPolicy.IssuedAt,
ApprovalTimestamp, erasure counts/authorization/destruction timestamps,
migration overlap counts/times, failover attempts/activation times and durations.
These are **not mapped** by this subset. The adopted annex's structured encoding
distinguishes nanosecond timestamps from second-based `*Sec` and
MaxOutageDuration fields. A complete inventory must follow schema references
and check body/annex units and signedness; a list of name matches is not enough.
Prices, quantities, percentages, enums and IDs are not globally converted.
Changing Header shapes or these numeric wire types requires version/migration
review; this folder supplies no producer upgrade or automatic transformer.

## 6. Reproduction, files and expected outcomes

Prerequisites: Python 3.12 or 3.14 and the pinned packages below. Node 24 is
optional for a second byte-computation path; no Node packages are required.
Installing dependencies may need network access. **The checks themselves are
offline**, do not read credentials, do not access a service, and require no
Docker, root privileges or changes to the existing implementation.

From this folder, create an isolated environment and run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python check.py --node node
```

Omit `--node node` for Python only; the output will explicitly say Node was not
run. A mismatch, missing input, dependency failure or cross-check failure exits
nonzero. No failed case is silently skipped. The output is a JSON internal
check report, not a conformance certificate. Preserve stdout/stderr and the
source commit when reporting either success or failure.

| File | Purpose |
|---|---|
| contract.py | Isolated minimal candidate byte/checking functions; not imported by existing implementations |
| generate.py | Deterministic public synthetic inputs and expected outputs; refuses an existing destination directory |
| check.py | Compare frozen expected bytes, regenerate exactly, and exercise negative checks |
| crosscheck.mjs | Separate restricted JCS encoder, incremental tree builder, recursive proof fold, signatures and BigInt numeric checks |
| data/vectors.json | Inputs, preimages, digests, signatures, mutations, numeric and malformed JSON cases |
| data/merkle-vectors.jsonl | One tree per line; roots and all indexed proof paths refer to the first N event digests in vectors.json |
| records/ | Internal execution/environment records and source/data hashes |

For a new local comparison, not overwriting checked-in or distributed artifacts:

```sh
.venv/bin/python generate.py /tmp/vcp-candidate-v0-fresh
.venv/bin/python check.py --vectors /tmp/vcp-candidate-v0-fresh --node node
```

The destination must not already exist. Regeneration is not preservation of a
past execution log. Check reports record the hashes of the files actually read.
An altered saved vector or omitted proof record fails exact regeneration before
cryptographic checks. The second language recomputes bytes from inputs, but
does not implement full schema, duplicate-key, trust or receipt validation.

Expected covered evidence:

- 135 event byte vectors: a 129-event synthetic chain plus six standalone/
  numeric-boundary variants. Only the first three chain events have event
  signature vectors; this is not a signed 129-event deployment trace.
- Empty root and 68 nonempty tree sizes: every size 1–64, plus 65/127/128/129;
  **2,529 positive membership paths**, with missing/surplus/modified proof checks.
- Three event signatures and one anchor signature, 33 protected-field signature
  mutations (including nested target fields), 18 event-preimage field mutations,
  eight correctly re-signed inconsistent anchors, wrong keys/domains/signatures
  and malformed base64. Mutation bytes are checked even when the mutated scheme
  would first fail format selection; there is no algorithm auto-detection.
- 168 numeric input/range cases across four field classes, 12 malformed or
  unsupported JSON examples, and explicit no-normalization/unknown-field checks.
- Full-list duplicate-ID, policy, order, omission, endpoint and count checks;
  wrong-event-digest binding; external **commitment** bytes only.

Case counts are not added together as “independent tests”: many are assertions
over the same synthetic records. Python generation and checking share candidate
helpers, so regeneration alone is a self-consistency check. Node independently
codes the listed byte operations within the **same internal work**, and uses
the same saved inputs. Neither is independent third-party reproduction.
The previous observational probe's 19/136, 0/136 and 40-fixture results concern
legacy code; they are not these candidate test results. Existing v1.2 CI also
checks the existing contract only, not this proposal.

## 7. Review and later acceptance

Review the byte choices and limits before any integration: especially the
number-free subset, protected event identity, policy-byte treatment, identity
grammars, unsigned receipt boundary and full-list versus partial-disclosure
claims. Every normative-change draft §8 gate not explicitly covered above stays
open. Unsupported input is not a successful native VCP check. Known failure
takes precedence over unknown in required-check aggregation, while the report
keeps unassessed categories visible. The aggregate helper cannot select which
requirements an external evaluator should accept.

An eventual independently operated run must record the fixed source/data hashes,
operator, environment owner, support provided, dependencies, deviations and
failures. Execution consent and publication permissions remain separate. There
is no claim that such a run occurred, no communication to K3, and no change to
past results or fixed distributions.

Primary algorithm references: [RFC 6962 §2.1](https://www.rfc-editor.org/rfc/rfc6962.html#section-2.1),
[RFC 9162 §2.1](https://www.rfc-editor.org/rfc/rfc9162.html#section-2.1),
[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html), and
[RFC 8032](https://www.rfc-editor.org/rfc/rfc8032.html).
