# SCITT-VCP Receipt verification context: candidate for review

**Date:** 25 November 2026. **Status:** first-party discussion candidate, unadopted.
Refs [#37](https://github.com/veritaschain/vcp-spec/issues/37).
Baseline: `draft-kamimura-scitt-vcp-07` and repository commit
`dfed70b3ec4acce9063bb5742dd27b4948bd34ca`.

This note supplies candidate contracts for the remaining entry-rule and
service/key questions in Open Issue 6. On 27 November 2026 VSO exercised seven
of the 22 proposed cases locally using two ordinary Receipts and the
[fixed replay package](replay/README.md). Fifteen cases remain unexecuted.
The published -07 source remains the baseline, and [#37](https://github.com/veritaschain/vcp-spec/issues/37)
remains open. Adopting a requirement would require a separate change decision.

## Input and proposed next decision

Bassem's [24 November, 19:20 UTC reply][reply] distinguishes the evidence that a
service committed to a rule from how a verifier initially obtains that rule.
He also identifies historical applicability as necessary when the rule is not
carried in a Receipt. His comments are input, not approval of this candidate.

The proposal compares an authenticated configuration path with a possible future
Receipt extension. The first replay uses the configuration path. The extension
and its historical-selection behavior remain to be tested. Both alternatives
remain unadopted.

## 1. Context contract

Before making an inclusion assertion, the experiment takes an explicit
verification-context record with the following logical fields. These are
requirements for an experimental input package, not a new wire schema.

| Context | Required content and provenance |
|---|---|
| Service | Stable service identity and the relying party's authority for trusting it. A URL, protected issuer claim, or key identifier supplied by the presenter does not establish trust by itself. |
| Receipt keys | Authorized public keys or certification paths, their binding to that service, permitted algorithms, rotation/retirement information, and relevant compromise or revocation evidence. Record the authority behind those bindings. |
| VDS and entry rule | Permitted VDS, immutable rule identifier, version and exact rule-document digest. The rule identifies both the preprocessing and the bytes supplied to the VDS. |
| Applicability | Identify the rule applicable to this service and entry, and separately the authority for the signing key of the Receipt being assessed. Retain historical contexts, epoch boundaries, and the evidence supporting each selection. A date range alone cannot establish when a Receipt was issued. |
| Assessment | Verification time, trust-configuration version/digest, applicable policy, evidence sources, and the precise claim being assessed. |

Configuration can be installed through an authenticated management channel or
an independently trusted authority. If signed configuration is supplied in the
Evidence Pack, its signer must already be trusted for that purpose. Merely
including a public key and a matching configuration signature is insufficient.

The service's registered policy can subsequently make its behavior auditable.
It does not establish the initial rule for checking its own Receipt. Treating
entry-rule metadata as part of that policy would be a profile addition to the
registration preconditions in [RFC 9943 §3][architecture], not an existing
standard discovery field. Key discovery through
[SCRAPI -11 §2.1][scrapi] is likewise separate from authorization of those keys.

## 2. Entry bytes: alternatives to test

[CCF profile -06 §§2.2 and 3.2][ccf] provides the preprocessing precedent:
retain tag 18, empty the unprotected map, preserve the other encoded elements,
and compute the statement digest locally. That does not make CCF's ledger leaf
construction the RFC9162_SHA256 construction.

For an initial **restricted experiment**, define `E` as follows:

1. Accept a well-formed tagged COSE_Sign1 whose tag/array prefix is exactly
   `d2 84`: minimally encoded tag 18 and a definite four-element array.
2. Require definite-length byte strings for protected headers, embedded payload
   and signature. Reject duplicate map labels and malformed COSE structures.
   Detached payloads, other outer encodings and indefinite-length encodings
   are outside this first experimental corpus.
3. Replace the entire unprotected map with the single byte `a0`.
   Preserve the complete encoded byte-string elements for protected headers,
   payload and signature exactly, including their length encodings.
4. Thus `E = d2 || 84 || P || a0 || B || S`, where `P`, `B` and `S`
   are those complete encoded elements, not just their contents.
   Do not parse and reserialize the payload JSON or the protected map.

The extra encoding restrictions above are proposed experimental restrictions,
not requirements attributed to CCF, RFC 9942, RFC 9943 or released VCP.
They would narrow admissibility if adopted; broader CBOR handling needs a
separate explicit rule and vectors.

| Alternative | RFC9162_SHA256 candidate entry | Leaf commitment |
|---|---|---|
| A1, proposed first experiment | `E` | `SHA256(0x00 || E)` |
| A2, comparison only | `SHA256(E)` | `SHA256(0x00 || SHA256(E))` |

These are distinct byte contracts. A2 is not an optimization interchangeable
with A1. The local experimental names A1/A2 are not registered identifiers.
The [RFC 9162 §2.1 leaf construction][tree] is applied only after selecting the
entry bytes; [RFC 9942 §5.2.1][receipts] does not select A1 or A2 for VCP.

Adding Receipts only to the unprotected map leaves `E` unchanged. Changing a
retained encoded element changes `E`, even if a decoder presents equivalent
values. Do not describe *every* CBOR re-encoding as a different entry: changes
confined to the discarded map disappear. Preserve the original transport bytes
alongside `E` for inspection.

An existing service using another entry construction is not retroactively
declared non-conformant. Its legacy context remains separate; its archived
statements and Receipts are never rewritten to fit A1.

## 3. Historical selection and bootstrapping

**Alternative A: context outside the Receipt.** Associate an approved rule and
its applicability with the trusted service. Preserve the authorization chain
for rule changes and key rotation. An archive needs evidence for the historical
context, rather than today's key-discovery result or today's rule alone.

An epoch based on time needs authenticated evidence linking the Receipt to the
relevant interval when the claim depends on issuance time. Compare two
records from an archive authority explicitly trusted for historical rule
selection. [RFC 9943 §4](https://www.rfc-editor.org/rfc/rfc9943.html#section-4)
allows a service to issue a fresh Receipt for the same Signed Statement,
including with a different verification key.

- **Receipt-specific record.** Bind the exact Receipt digest to the service
  and rule epoch. This identifies the archived Receipt bytes. A reissued
  Receipt needs its own binding on this path (CX-12).
- **Entry-specific record.** Bind the stable service identity, hash algorithm
  and `H(E) = SHA256(E)` (using §2's preprocessing) to an identified rule
  and epoch. The authenticated record must identify the preprocessing and
  scope its assertion to that service and entry. Recompute `H(E)` locally
  and compare it and the service identity with the record. This digest selects
  an applicable rule; A1 still passes the full `E` to its VDS. A second
  Receipt for the same statement and service can reuse the record when the
  authority's assertion applies to both. If multiple epochs apply to that
  entry and the record leaves the choice unresolved, report insufficient
  context (CX-19 through CX-22).

Each Receipt, including one reissued under a rotated key, still needs a valid
proof and signature, service-to-key authorization and applicable key history.
The entry-specific record alone establishes neither issuance time nor a
particular Receipt's key epoch. If the relying policy needs such evidence and
it is missing, report insufficient context. A changed entry or different service
cannot reuse this record. An unsigned event time, HTTP retrieval time, file
modification time or the Receipt's unprotected tree size/index cannot establish
issuance time. Both archive paths add an external trust assumption.

A closed, locally authorized list of candidate rules is another bootstrapping
experiment. Bound the list and work performed, and record every attempted rule.
Do not download or try arbitrary rules named by a presenter. A unique
cryptographic match alone does not establish that a rule was authorized in the
relevant epoch. Multiple applicable matches remain ambiguous.

**Alternative B: a future protected Receipt parameter.** Compare a versioned
rule identifier carried in signed Receipt metadata. [RFC 9942 §4.4][receipts]
discusses extensible profile metadata, including `typ`; it does not already
define a VCP entry-rule identifier. Before implementation this alternative
needs identifier allocation/typing, mandatory processing and downgrade rules,
binding to service authorization, and legacy behavior.

A protected identifier is authenticated only after signature verification
under an authorized service key. It is not itself a trust anchor. No field,
media type, code point or additional endpoint is allocated by this note.

## 4. Verification and reporting contract

Proposed experiment order:

1. Validate the container and supported algorithms; load authorized context.
2. Establish the intended service, applicable key history, VDS and entry rule.
3. Derive the entry from the supplied statement, recompute the root, and check
   the Receipt signature with that root as the detached payload.
4. Record the claim and diagnostic evidence. Check issuer signatures and
   application policy separately when required by the chosen assessment.

Use the existing plan's three local reporting categories; reason names below
are illustrative diagnostics, not SDK or protocol enums.

| Condition | Experimental report |
|---|---|
| Context is applicable, proof and authorized Receipt signature pass | `verified under declared context`: inclusion under the identified service's signed root only |
| No service authorization, unavailable historical key, unknown rule, or missing epoch evidence | `context insufficient`, with the missing prerequisite |
| Multiple authorized contexts apply without a defined resolution | `context insufficient`: ambiguous context; no automatic newest-rule preference |
| Known service/rule contradicts authenticated applicable configuration | `rejected`: context conflict |
| Signature or proof fails with complete applicable context, or input is malformed | `rejected`: identify the failed check |
| Receipt from a service explicitly outside the relying party's allowlist | `rejected`: service not authorized, even if its signature is mathematically valid |

Missing context is not evidence that a statement was never registered.
Even rejection of this statement/Receipt pair is not a global non-inclusion
proof. Keep mathematical signature results separate from service trust.
Retirement alone need not invalidate an old Receipt; assess historical
authorization and any compromise/revocation evidence under the declared policy.
A claimed old timestamp alone cannot establish that signing preceded compromise.

As in [-07 §8.5][vcp], this work makes no log-position, log-size, global
consistency or source-completeness assertion. It does not close Open Issue 2
on AnchorRecord coverage or the other VCP integrity questions.

## 5. Evidence, compatibility and remaining work

The [case matrix](cases.md) records the source of each expected outcome. The
[replay package](replay/README.md) supplies the input bytes, separate trust
configuration, expected outcomes, pinned dependencies and rerun commands.
VSO ran both the [Python](replay/results/python.json) and [Go](replay/results/go.json)
checks against the same input bytes. Each produced eight Receipt assessments
across CX-01, CX-09, CX-10, CX-17, CX-19, CX-21 and CX-22. Five verified
inclusion under the declared context, two lacked evidence authorizing the
selected key, and one had ambiguous rule context. CX-19 accounts for two
assessments: the original K1 Receipt and the K2 reissue for the same statement.
All seven cases reuse these two Receipts.

The fixture covers embedded synthetic JSON statements, the restricted encoding
in §2 with an already-empty unprotected map, the A1 entry rule, and a two-leaf
RFC9162_SHA256 tree. A separately trusted authority signs key-use records for
each exact Receipt. CX-17 records the limit of the inclusion claim; the
package supplies no independent evidence of source completeness. CX-22
uses two signed rule records and stops at unresolved applicability, before
comparing either candidate root. It supplies no measured outcome for an A2
inclusion proof. The generic payloads do not exercise the -07 VCP payload and
profile claims.

The next comparison should cover the remaining cases, the compatibility of
both entry rules with historic services and encoding variants, and the
alternative Receipt extension. The recorded runs are first-party research
using off-the-shelf libraries. Independent external reproduction and a
full-profile interoperability assessment remain outstanding.

The immediate review questions are whether A1 is the right first comparison,
what evidence should select a historical rule when a Receipt is unlabelled,
and which common SCITT work could supply the proposed metadata. These remain
questions, not decisions or a claim of Working Group consensus.

Merging this note would record research only. The existing
[change-control status](../../CHANGE-CONTROL.md) and
[proposal register](../../decisions/REGISTER.md) continue to govern their own
subjects; this note assigns no VCP-CP identifier.

Prepared with AI assistance. Independent technical review remains outstanding.

[reply]: https://mailarchive.ietf.org/arch/msg/scitt/qWDPe41grT_TTMYndv9kBcdjWL0/
[architecture]: https://www.rfc-editor.org/rfc/rfc9943.html#section-3
[receipts]: https://www.rfc-editor.org/rfc/rfc9942.html
[scrapi]: https://datatracker.ietf.org/doc/html/draft-ietf-scitt-scrapi-11#section-2.1
[ccf]: https://datatracker.ietf.org/doc/html/draft-ietf-scitt-receipts-ccf-profile-06#section-2.2
[tree]: https://www.rfc-editor.org/rfc/rfc9162.html#section-2.1
[vcp]: https://datatracker.ietf.org/doc/html/draft-kamimura-scitt-vcp-07#section-8.5
