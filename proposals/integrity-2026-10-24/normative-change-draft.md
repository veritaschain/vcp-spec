# VCP integrity byte-contract and migration proposal

**Status:** Draft normative-change proposal; **unadopted** and not effective.
**Date:** 2026-10-24 JST.
**Formal proposal number:** Unassigned. **Target release/version:** Undecided.
**Implementation and acceptance tests for this candidate:** Not supplied.
**Independent third-party reproduction:** Unestablished.

## 1. Decision sought and boundaries

This document proposes how a future VCP revision could bind exact event bytes,
Merkle membership, AnchorRecord metadata and numeric values. It is separate
from the [technical-errata proposal, PR #3](https://github.com/veritaschain/vcp-spec/pull/3),
which records observed discrepancies without selecting replacement rules.
Approval of an observation, or merge of either discussion document, is not
adoption of this candidate. No official VSO proposal identifier is allocated here.

All **MUST**, **MUST NOT** and **SHOULD** below are proposed requirements for
this candidate only. They impose no new requirement on current v1.2. The
candidate is intentionally not a complete deployable wire specification:
§8 identifies decisions and artifacts required before adoption or release.

This PR adds only this document. It does not edit an existing specification,
schema, implementation, signed record, fixture, fixed distribution, release,
tag, DOC-SYNC record or K3 material. Existing experimental extensions remain
**unadopted**; independent third-party reproduction remains **unestablished**.
The existing research adapter, gates and OS experiment are not promoted to a
native VCP implementation or conformance test by this proposal.

## 2. Evidence and precedence

The baseline is VCP commit
[`b23acb266f88df81d960d36d58fb64ceaa0dd5ed`](https://github.com/veritaschain/vcp-spec/tree/b23acb266f88df81d960d36d58fb64ceaa0dd5ed):

- [English specification](https://github.com/veritaschain/vcp-spec/blob/b23acb266f88df81d960d36d58fb64ceaa0dd5ed/spec/v1.2/VCP-Specification-v1_2_en.md),
  SHA-256 `ce94399bde111c8b805d3804fad2e6d61cab2f1839533d5009e94e812d15a942`.
- [Adopted VSO-SPEC-CHANGE-001 annex](https://github.com/veritaschain/vcp-spec/blob/b23acb266f88df81d960d36d58fb64ceaa0dd5ed/spec/v1.2/VSO-SPEC-CHANGE-001.md),
  SHA-256 `e810b952099f96c1f0841916be8c3babcb6adbfc48c05a236966d164fe11292b`.
- [Event schema](https://github.com/veritaschain/vcp-spec/blob/b23acb266f88df81d960d36d58fb64ceaa0dd5ed/spec/v1.2/vcp-event-v1.2.json),
  SHA-256 `fa73e3e76ebd939f84f6ac28dd6aadd08007aa753feb25f278d58ff02a74eac4`.

The existing VCP annex's precedence is preserved; this candidate supersedes
nothing. Its optional SCITT/COSE encoding and existing crypto-agility choices
need explicit future mappings, not implicit substitution by the candidate below.

[Pinned research observations](https://github.com/veritaschain/vap-spec/blob/9fa5fbc68075079b4599e16940e9078db976cd59/experiments/vcp-v1.2-integrity-alignment/README.md)
and [saved probe results](https://github.com/veritaschain/vap-spec/blob/9fa5fbc68075079b4599e16940e9078db976cd59/experiments/vcp-v1.2-integrity-alignment/results/probe-output.json)
motivate this proposal. They concern selected examples and synthetic data,
not deployment-wide behavior or tests of this proposed replacement. The P8
distinction is retained: all 40 fixture timestamps are exactly representable
in binary64, but the Python JCS library rejects their integer inputs; arbitrary
nanosecond integers can additionally lose precision. Neither observation
licenses rounding old data.

## 3. Candidate event-to-Merkle contract

### 3.1 One explicit interpretation

The initial candidate uses SHA-256 for event, policy and tree hashes, and
Ed25519 for the AnchorRecord signature. This is a bounded proposal for review,
not removal of existing algorithms. Additional algorithms require separately
specified encodings and vectors; an unsupported algorithm MUST NOT be silently
downgraded or treated as verified.

A future contract MUST assign distinct, authenticated identifiers for the
protocol version, event-hash scheme, tree scheme, numeric encoding, and
AnchorRecord signature scheme. Verifiers MUST select the interpretation from
authenticated context plus their configured acceptance policy, not by trying
several encodings until one passes. The labels and field names below are local
design names, not registered protocol identifiers.

### 3.2 Event preimage: proposed explicit object

The preferred candidate replaces ambiguous concatenation with one JCS object,
called `EventCommitment` here, containing:

- `ContractID` and `EventHashAlgorithm`;
- the complete `Header` and `Payload`, without silently dropping extensions;
- `PolicyIdentification`, as its complete object if present, or explicit JSON
  `null` if absent;
- `ChainMode`, with exactly `none`, `start`, or `linked`, and `PreviousEventHash`.

In `none` and `start`, `PreviousEventHash` is explicitly `null`; in `linked`, it
is the previous event's algorithm-qualified digest. The modes distinguish a
non-chain event from a chain start and continuation. Chain ordering, authorized
recovery and predecessor availability still need their own checks. A digest
alone does not authorize a chain restart. No all-zero magic hash or appended
hex string is accepted as an alternative spelling in this candidate.

The object is encoded as JCS UTF-8 bytes after exact input validation and the
field-specific numeric rules in §5. EventHash is SHA-256 of a dedicated event
domain prefix followed by those bytes. The prefix is an ASCII context label
followed by one zero byte; its final literal and `ContractID` are release gates,
not deployed constants. Distinct labels are required for event, anchor-signing
and external-anchor commitment uses.

The event's own computed `Security.EventHash`, signatures, inclusion proofs,
anchor receipts and transport envelope are excluded to avoid circularity.
`Security.PrevHash` is represented exactly once by `PreviousEventHash`, and
the declared hash algorithm must agree with the committed algorithm. Excluding
the event's own signature does **not** remove authorization signatures already
inside Payload; those remain content. Any other security or extension field
used to authorize an interpretation must have a defined protected location,
or the candidate input is unsupported, rather than silently trusted.

No event-signature requirement is waived: a later byte contract must specify
the event signature's own protected context and its binding to EventHash,
including the optional COSE route. Anchor signing does not substitute for that
work. The preimage proposal changes event hashes even where source values stay
the same; its compatibility cost is explicit, not disguised as an editorial fix.

An alternative is to retain separate JCS(Header) and JCS(Payload) concatenation
and define the missing protected fields separately. That reduces some changes
but retains multiple binding surfaces. The explicit-object option is preferred
for discussion; selecting it requires a recorded decision and full schema mapping.

### 3.3 Tree and paths

Each leaf input is the **32 decoded digest bytes** of the candidate EventHash,
not its textual `sha256:` prefix, hex characters, or a recanonicalized full
event. The event-hash scheme therefore forms part of the signed tree context.

The candidate adopts the tree definition in
[RFC 6962 §2.1](https://www.rfc-editor.org/rfc/rfc6962.html#section-2.1):
ordered inputs, leaf prefix `0x00`, internal prefix `0x01`, and recursive
splitting at the largest power of two below the subtree's leaf count. Odd
nodes MUST NOT be duplicated. The empty-tree root follows the RFC, but this
candidate permits signed **event-batch** AnchorRecords only for nonempty
batches; empty checkpoints would require a separately defined record type.

The committed list preserves producer-declared order. A verifier MUST NOT
sort by timestamps or identifiers, deduplicate entries, or infer order from
an unordered container. The candidate rejects repeated EventIDs within one
batch; this is a proposed validation rule, not a claim about old data. A
full-batch verifier recomputes each event hash, the ordered root and the count.

Inclusion proofs use leaf index and the count authenticated by §4. Verification
follows [RFC 9162 §2.1.3.2](https://www.rfc-editor.org/rfc/rfc9162.html#section-2.1.3.2)
with the leaf hash as its initial hash. The verifier MUST reject out-of-range
indices, invalid digest lengths, incomplete paths and surplus nodes, and
compare the resulting root. A generic tree-depth bound or caller-provided
left/right flags is not a substitute for the size-aware algorithm. This
adopts the tree algorithm only, not the RFC's certificate or TLS data model.

An inclusion proof establishes one member's inclusion at an index. It does
not show that the evaluator received every member. A full-submission check
also needs the agreed submission requirements and every expected index, or
an independently justified expected set; it must distinguish missing,
withheld and unavailable evidence. No record mechanism proves actions that
were never observed.

## 4. Candidate AnchorRecord signature and external receipt

### 4.1 Protected fields

The proposed record has a protected object `AnchorStatement`, an outer
`Signature`, and detached `ExternalReceipts`. The protected object includes
all of the following; omission is not equivalent to a default:

| Field group | Proposed meaning and binding |
|---|---|
| Contract and schemes | ContractID, protocol version, event-hash scheme, numeric encoding, tree scheme, hash and signature algorithms |
| Identity/context | AnchorRecordID, producer identity, stream/batch identity, KeyID; final identifier grammars to be specified |
| MerkleRoot | Algorithm-qualified SHA-256 digest, decoded and checked as 32 bytes |
| EventCount | Exact positive batch size; decimal string, range 1 through 2147483647 in the initial candidate |
| FirstEventID / LastEventID | Identifiers at index 0 and EventCount minus 1 in the committed ordered batch |
| PolicyID / PolicyDigest | Identifier plus SHA-256 commitment to the exact preserved policy-document bytes, including the rules relevant to this batch |
| RecordedAtNs | Signer's claimed record-creation time, decimal nanoseconds; not a third-party-proven anchoring time |
| IntendedAnchorTarget | Target type and stable identifier selected before signature; no subsequently issued receipt inside this object |

All fields and any future authorized extension within `AnchorStatement` are
covered. Unknown semantic extensions cannot be ignored when determining
conformance. Schema/type validation occurs before cryptographic checks; duplicate
JSON keys, booleans used as counts, and coercion between numbers and strings
MUST be rejected. Exact lexical forms are not repaired by the verifier.

### 4.2 Bytes to sign and trust

The to-be-signed message is a distinct anchor-signing domain prefix followed
by JCS UTF-8 of the complete `AnchorStatement`. Ed25519 signs that message,
not MerkleRoot alone. The signature is outside the statement; its encoding
is standard padded base64 with a canonical spelling and no whitespace. Final
domain literals and identifiers must be fixed with the adopted format and
test vectors. This is a proposed scheme, not a reinterpretation of the
current root-signing function.

The verifier MUST bind KeyID and producer identity to a trusted key and an
authorization policy supplied independently of the record. A key embedded in
the same input does not make itself trusted. Algorithm, identity, validity
period and applicable revocation/time policy must be checked. Missing trust
or time evidence remains unknown/unsupported; a valid signature alone does
not resolve it. Reuse or conflict of a batch identity needs separate detection
and retained evidence; a signature does not prevent a signer issuing two records.

Full-batch verification MUST compare the signed count, endpoint identifiers
and policy with the actual committed events. `Header.PolicyID` must agree
with the batch PolicyID in this single-policy candidate; any
`PolicyIdentification.PolicyID` must agree too. Mixed-policy batches are
unsupported pending an explicit contract. Policy bytes must match PolicyDigest
before their content is used as an authenticated rule set. PolicyIdentifier
resolution or a URL alone is insufficient.

A partial disclosure may use size-aware inclusion proofs for its presented
events. Endpoint consistency requires authenticated endpoint event evidence
or a full-batch check; if neither is supplied, the verifier MUST NOT label
the endpoints checked. Signed metadata is an attributable assertion until
its relationship to the events is verified.

### 4.3 Receipt commitment without circularity

The proposed external commitment is SHA-256 of a third, distinct domain prefix
followed by JCS of the object containing exactly `AnchorStatement` and
`Signature`. Receipt adapters submit those commitment bytes and later verify
that the external service's proof refers to the same commitment, subject to
that service's authentication, time and finality rules.

`ExternalReceipts` is excluded from the signed object and commitment so that
the receipt never refers to a preimage containing itself. Receipt bytes,
verification status and observed external time remain separate from the
signer's `RecordedAtNs`. A locally signed time or synthetic service receipt
does not establish independent timestamping.

A changed protected target or corrected metadata needs a new signed record
with a distinct identity and preserved relationship to the prior record;
the prior statement/signature/receipt is retained unchanged. Whether a
supersession relation is authorized, and how it interacts with existing
RECOVERY/failover requirements, must be specified before release. Existing
anchor deadlines and recovery policies are not changed here.

## 5. Candidate exact numeric representation

The preferred rule is decimal JSON strings for exact integer timestamps,
counts and indices in the new contract, with typed validation before JCS.
For nonnegative integers the whole string must be `0` or an ASCII nonzero
digit followed by zero or more ASCII digits. No sign, whitespace, leading
zero, decimal point or exponent is permitted. JSON numbers and booleans are
not accepted as equivalent spellings. Parsing uses exact integer arithmetic.

| Field class | Candidate unit and range | Status of inventory |
|---|---|---|
| Header.TimestampInt; RecordedAtNs | Unix-epoch nanoseconds; 0 through 9223372036854775807 | Proposed nonnegative signed-64-bit range, retaining the Header field name for its logical integer meaning |
| Anchor EventCount | Events; 1 through 2147483647 | Proposed positive signed-32-bit range; empty event batches unsupported |
| Inclusion leaf index | Zero-based position; 0 through EventCount minus 1 | Must use the authenticated count |
| Other timestamp, sequence, counter and duration fields, including annex fields | Exact unit, range and signedness must be assigned per field | Release blocker: complete inventory not yet supplied |
| Financial decimal strings, enums and IDs | Preserve their field semantics; no blanket string-to-number or number-to-string conversion | Review separately; this proposal does not reinterpret prices as integers |

If `TimestampISO` is present alongside TimestampInt, exact conversion under
the selected UTC/Unix time convention MUST agree; clock accuracy is assessed
separately. Leap-second handling and the accepted timestamp lexical subset
must be resolved in the full field inventory. A 64-bit limit here is a
proposed protocol choice, not a claim that JCS itself has that integer range.

[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html#section-3.1) supplies the
canonicalization rules; domain-specific exact decimal strings avoid depending
on binary64 for these fields. The candidate MUST NOT convert an arbitrary
nanosecond integer to floating point, round it, and call the result equivalent.
Duplicate keys and malformed Unicode must be rejected; implementations must
not normalize strings or inject defaults before verification.

An alternative is to limit JSON integers to a precisely defined safe range
and change timestamp units. That would sacrifice the current arbitrary
nanosecond intent unless a separate exact remainder were defined. Decimal
strings are preferred, but their wire-type, schema and hash changes require
explicit approval and migration rather than an unversioned patch.

## 6. Verification result model and limits

Proposed implementations MUST report separately: format support, event-hash
validation, chain linkage when requested, Merkle membership/size, statement
signature, key authorization, metadata-to-event consistency, external receipt,
and satisfaction of agreed submission requirements. They MUST NOT accept
input declarations such as `signature_valid: true` in lieu of verification.

Missing or unsupported evidence is not success. Within required cryptographic
checks, a demonstrated failure takes precedence over unknown items in an
aggregate result, while every unknown item remains visible. An all-required-
checks pass must not become an assertion that all real-world activity was
observed, that the evaluation scope was sufficient, or that a legal or
certification requirement was satisfied.

These output rules do not alter the existing research verifier. Adoption would
require separately reviewed implementation and mappings. In particular, the
VAP event-to-leaf descriptions and its current conformance status still need
clause-level reconciliation. No unseen Draft 2 / RD-001 text is treated as
an adopted source for this candidate.

## 7. Preservation and migration

1. Preserve original event bytes, signatures, roots, proofs, receipts,
   fixed ZIPs, hashes, source revisions and past results. Never overwrite an
   artifact to make an old run appear to have used the new contract.
2. Keep legacy verification explicitly versioned. A legacy signature may
   verify for its original bytes while count/policy binding remains absent
   or unknown. Do not report full new-contract conformance on that basis.
3. Do not auto-detect the scheme by whichever interpretation passes. If the
   original scheme or exact integer value is unavailable, report that limit;
   do not guess the pre-rounding value or regenerate a supposed original.
4. A new attestation over old evidence is a new dated claim, with its own
   authority and source commitments. It cannot retroactively authenticate
   previously unsigned metadata or prove an earlier external timestamp.
5. Publish revised schema identifiers, algorithm/format identifiers, exact
   vectors and producer/consumer transition rules together only after approval.
   Old and new formats must remain distinguishable, including at API boundaries.
6. Assess VCP §1.3's promise of compatibility within v1.x. This candidate changes
   hash preimages, some roots/proofs, signed messages and wire types. A major
   revision or explicitly separate format may be needed; neither a patch
   release nor backward compatibility is preapproved.
7. Keep K3 unchanged. Any impact assessment must identify the actual generator,
   canonicalizer and version used, and record additional runs separately.
   No notification, new evaluation criterion or invalidation of prior results
   is authorized by publication of this document.

## 8. Adoption blockers and proposed acceptance evidence

All items below are **open**; they are deliverables for a later change, not
completed tests or authority to edit the current fixed artifacts.

| Decision / evidence | Required disposition before release |
|---|---|
| Authority and version | Confirm VCP approval procedure, record decision and formal identifier, select version/migration strategy; do not borrow a VAP vote or imply one occurred |
| Byte contract | Select event preimage option; fix all domain literals, scheme identifiers, lexical encodings and extension rules; define event-signature and COSE mappings |
| Schema and numeric inventory | Enumerate every affected path in body/schema/annex, units, ranges, null/absence rules and backwards impact; no unreviewed global conversion |
| Anchor policy | Finalize identity, key/time policy, policy-byte commitment, target binding, correction/supersession and interaction with recovery/failover |
| Merkle vectors | Empty root plus nonempty sizes 1–64 and power-of-two boundaries; every index, odd sizes, duplicate-ID rejection, changed order, missing/surplus/wrong-length proof nodes and wrong signed counts |
| Signed-field mutation vectors | Real signatures; mutate each protected field, algorithm/context, key, signature and policy bytes; reject unauthorized keys and receipt-to-commitment mismatch; do not use validity flags |
| Numeric vectors | Exact values around 2^53 and the chosen 32/64-bit boundaries, the lossy nanosecond example, invalid lexical forms, boolean/number/string substitutions and all timestamp-bearing paths |
| Cross-language reproducibility | At least two independently implemented serializers/verifiers agree on preimage bytes, hashes, roots and signatures; document dependency and environment details, including failures |
| Migration and framework mapping | Preserve legacy verification records; compare affected bytes explicitly; reconcile VAP clauses without claiming conformance from this draft |
| External reproduction | Record who ran which fixed version in whose environment, assistance and relationships; distinguish internal tests from independent reproduction and publication permission |

The existing v1.2 CI can continue to pass while these proposed repairs remain
unimplemented. Passing that CI, the old synthetic probe, or the research
adapter's 14 cases would not constitute acceptance evidence for this candidate.
Document review, normative adoption, implementation validation and independent
reproduction are four separate events and must be reported separately.
