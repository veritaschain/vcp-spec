# VCP field placement, numeric interpretation and migration — decision draft

**UNADOPTED discussion draft; not effective. Independent third-party reproduction
has not been established.** Formal proposal number, target release, native
ContractID, schema identifiers and signing domains remain **unassigned**.
The labels L/U/T/M/G below are local discussion labels, not VSO allocations.
Document publication or merge is not adoption, implementation validation,
certification or permission to rewrite evidence.

This follow-up uses the merged [PR #14](https://github.com/veritaschain/vcp-spec/pull/14)
at `e024bba1b2d3967e7a3335c723c9b2dcabda35d5`. It adds **Markdown documents only**.
It does not change current normative text, schemas, implementations, existing
experiments, signed records, fixed distributions, tags/releases, DOC-SYNC or K3.
No new implementation, schema, vector set, converter or execution result is
supplied. Earlier drafts and historical statements retain their original text.

## Reading order and recommended direction

- [Field placement and interpretation candidate](field-layout-candidate.md):
  native logical locations, policy roles, protected hash/signature boundaries,
  per-path units, exact conversion and time representation.
- [Decisions, migration and acceptance gates](decisions-and-migration.md):
  alternatives, remaining blockers, preservation-first migration, separate
  outcomes and required future evidence.

The preferred **proposal**, not an adopted decision, is a separately versioned
native contract: retain the full Header/Payload/PolicyIdentification structure;
put the ns/ISO pair in Header; bind exact interpretation-policy bytes; preserve
decimal lexemes; convert units only in explicit exact calculations or a new,
separately identified derived record. Keep original-contract verification and
creation of new evidence as distinct operations. Do not promote the synthetic
Payload wrapper or its test identity grammar into a native format.

The proposed layout changes the prior closed byte candidate. It therefore needs
a new ContractID/schema/domain set and new vectors before it could be implemented
as an accepted format. Neither existing checker is modified to accept it here.

## What PR #14 establishes, and what it leaves open

The final reviewed research HEAD was `bbf4db88b5a8d2253bb9f611fa4db30a95b62cba`.
Its recorded internal Python 3.12/3.14 runs match **45 expected outcomes**:
12 PASS, 30 FAIL and 3 UNASSESSED; 20 Python regressions and eight Node
report controls succeed per runtime. The Node path checks 40 accepted event
hashes, 44 external commitments, 88 actual Ed25519 results and 450 relations.
These are different overlapping measures, not a sum of independent proofs.
This document reads those records; it does not claim to rerun or extend them.

| Observed case(s) in PR #14 | Consequence for this discussion | Not established |
| --- | --- | --- |
| `header-iso-not-an-extension` | A future native Header with ISO cannot reuse the closed v0 contract | Native schema or all-field mapping |
| `confidence-leading-zero`, `confidence-negative-zero` | Arithmetic equality does not imply equal committed text | A unique decimal spelling or instrument precision policy |
| `epoch-json-number-one`, `confidence-json-number` | Type validation precedes candidate hashing; generic JCS diagnostic bytes are not an EventHash | General numeric-to-string migration or all JCS input handling |
| `one-ns-stale-statements`, `one-ns-rehashed-not-resigned` | Raw signature verification, binding to an event and new signing are different operations | Authorization to convert or re-sign an old record |
| `resigned-wrong-iso-year`, `timestamp-unit-mismatch-signed` | Valid signatures do not repair wrong units or an inconsistent time pair | Physical clock accuracy, truthful events or policy compliance |
| `policy-byte-change-unbound`, `unselected-policy-resigned` | Policy byte binding and permission to use an interpretation are separate | Production policy schema, issuer authority or registry |
| `leap-unmapped`, `smear-unmapped` | Preserve an unresolved time mapping as unassessed | A leap/smear conversion or external timestamp |
| Final-review report controls | Recompute traces/references/relations; do not trust report field presence | Host/operator authenticity or independent reproduction |

PR #14 has **one supplied event per case** and an opaque research Payload. It
does not establish migration of native multi-event chains, approval signatures,
real AnchorRecords, binary/COSE encodings, receipts or customer data. Its 12 PASS
outcomes are passes of covered synthetic checks, not native conformance.

## Evidence baseline and source fingerprints

All links below are fixed to the merge commit above. SHA-256 is over each source
file's exact repository bytes. This records document provenance, not an adopted
policy or independent attestation. The numeric inventory's N001–N074 identifiers
are review references, not protocol field identifiers.

| Source | SHA-256 |
| --- | --- |
| [Current v1.2 body](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/spec/v1.2/VCP-Specification-v1_2_en.md) | `ce94399bde111c8b805d3804fad2e6d61cab2f1839533d5009e94e812d15a942` |
| [Current GA schema](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/spec/v1.2/vcp-event-v1.2.json) | `fa73e3e76ebd939f84f6ac28dd6aadd08007aa753feb25f278d58ff02a74eac4` |
| [Adopted annex](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/spec/v1.2/VSO-SPEC-CHANGE-001.md) | `e810b952099f96c1f0841916be8c3babcb6adbfc48c05a236966d164fe11292b` |
| [Unadopted normative-change draft](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/proposals/integrity-2026-10-24/normative-change-draft.md) | `2fa4c656744bd5fc9dbcba81ac27c6d6af978303563f7303384534b63c2709ef` |
| [Closed byte candidate v0](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/proposals/integrity-2026-10-24/byte-contract-candidate-v0/README.md) | `5cb18c94048930f140bbb05f6679a683a694ea9630155c0c1093e61cb3dc7844` |
| [Numeric inventory: 74 entries](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/proposals/numeric-fields-2026-10-25/inventory.json) | `28645bbdeb1da72a2cb71a703ecc1dab2a54f4f23971b65498e921699568cc63` |
| [Numeric candidate and migration assumptions](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/proposals/numeric-fields-2026-10-25/README.md) | `9c890cbf76cdd86e03706d1e8d74abbf5a1c38cd44bbfbc71ad49b94af5e9531` |
| [Numeric checker experiment scope](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/experiments/numeric-representation-candidate-v0/README.md) | `ad125d880e1e27c92a6b8d4a13ba809f30db261e47e2fe4d5d5bad2f401e36ff` |
| [PR #14 scope and limitations](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/experiments/numeric-byte-binding-v0/README.md) | `9adda516001a53c9a87d3e3feda6da94e38991d6cf97ec57f117fb842be40f0d` |
| [PR #14 final review](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/experiments/numeric-byte-binding-v0/FINAL_REVIEW.md) | `ef528f5070ce016bfdccb9d92c3ecf91eb3d41946cc247397b3cc712c5d02593` |
| [PR #14 fixed cases](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/experiments/numeric-byte-binding-v0/data/cases.json) | `4d581a8f77f4ab281b4e934cdd63c02f8aec27eb28ab492a27cdedec190ad4fb` |
| [PR #14 final Python 3.12 record](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/experiments/numeric-byte-binding-v0/records/final-review-python312.json) | `9dbb334949cde1e6fcf398d0646079e571e21c2db5d076befc472576b317f9c0` |
| [PR #14 final Python 3.14 record](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/experiments/numeric-byte-binding-v0/records/final-review-python314.json) | `0dcd915cd0a78aa8f1755b4d464db0c77bf5573cd52f2b6aad6bc39358de0ae4` |
| [PR #14 final Node crosscheck](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/experiments/numeric-byte-binding-v0/records/final-review-node-python312.json) | `011b3a0d5e36cbd365830b7b48e57865446399750572530725a5d8438c966159` |
| [PR #14 final report controls](https://github.com/veritaschain/vcp-spec/blob/e024bba1b2d3967e7a3335c723c9b2dcabda35d5/experiments/numeric-byte-binding-v0/records/final-review-controls-python312.json) | `18534acbda3b258b37f74f8c88e18d9d0d282de0106dce20abba51464d605c01` |

Read the current body/schema/adopted annex as current sources; read the numeric
inventory, byte-contract candidate and this document as **unadopted** proposals.
The adopted annex's existing precedence is not displaced. This document does
not declare that an earlier open gate was closed merely because a later PR
merged, and does not infer unseen approval records.

## Review status

Every decision in the register remains **OPEN / UNADOPTED**, including the
recommended options. Logical placement is proposed separately from presence,
authorization and full native schema acceptance. Requiredness is not weakened,
and a missing unit, source format or authority is not supplied by a default.

Before creating this Draft PR, the preparation review checked relative links,
the 74-entry disposition accounting, the cited case IDs/results, source hashes,
and that only the three new Markdown files differ from the pinned baseline.
That is documentation validation, not a new protocol or independent reproduction
test. The ordinary repository CI, if successful, validates its existing tests;
it does not execute or adopt the new prose candidate.

### Final document review — 2026-10-25

Review began at `2a1a377823b816dffc2b2b454cf4c8395d4dee1f`. The following
clarifications were made within these proposed documents only:

- Separate event-derived full-batch binding checks from anchor time and target
  evidence. A subset/proof cannot establish full-list checks, and a signed time
  or target claim is not independent timestamp or delivery evidence. Each policy
  role is consistent across the batch; the two roles need not share one binding.
- Separate ISO spelling conversion from target capacity. A known instant outside
  TIME_NS remains unsupported by this candidate after lexical conversion; it
  cannot be moved into range by shifting the epoch or relabeling units.
- State integer maxima explicitly as 2^31−1 / 2^63−1 (signed 32-/64-bit maxima),
  and keep equivalent spellings of one separate from equivalent spellings of zero.

These are corrections to design prose, not findings of newly executed protocol
failures or an adoption decision. The complete native schema, byte contracts,
authority rules and migration vectors remain open. Integration of the documents
does not establish independent third-party reproduction.

The final documentation audit verified all 15 pinned source fingerprints, all
74 inventory dispositions without omissions or duplicates, and 13 cited case
IDs plus the historical PR #14 counts. Local Markdown parsing checked nine
tables and four relative links/anchors. Exact arithmetic separately confirmed
the two illustrated epoch conversions and the unit/decimal equivalences; these
are prose calculations, not native migration tests. All 201 baseline tracked
files remain byte-identical, with only these three new Markdown files added.
