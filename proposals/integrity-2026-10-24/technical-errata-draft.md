# VCP integrity-layer technical errata proposal

**Status:** Draft for review; **unadopted**. Not an issued erratum, a normative
annex, or a released protocol revision. Formal document number unassigned.
**Date:** 2026-10-24 JST.
**Subject:** Merkle construction and proofs, AnchorRecord signature coverage,
and exact numeric representation in VCP v1.2, with a limited v1.1 source comparison.
**Disposition:** Open. Publication or merge of this proposal is not adoption.

## 1. Scope and authority

This document proposes notices about contradictions and limitations in the
published material. It does not replace the published algorithms, schemas,
signature contract, or versioning rules. A separate normative-change draft
will propose candidate replacement rules and migration decisions. The two
documents require separate dispositions: accepting an observation does not
approve a new wire format.

No existing specification, implementation, signed data, fixed distribution,
release, tag, K3 baseline, input, criterion, or result is modified by this
proposal. Existing experimental extensions remain **unadopted**. Independent
third-party reproduction remains **unestablished**. The research adapter is
not a verifier of native VCP v1.2 events or proof of full VAP conformance.

The authoritative VCP sources are under `spec/`. VCP v1.2's adopted
VSO-SPEC-CHANGE-001 annex takes precedence where the specification summary and
annex differ; this proposal has no such precedence. In particular, the annex's
optional SCITT/COSE route (§5) and local AnchorRecord retention (§7.7) do not
make the root-only example a signature over the complete record. An
implementation with additional authenticated bindings must be assessed on its
actual signed bytes. No blanket conclusion about all VCP implementations is made.

## 2. Fixed sources and evidence

The VCP baseline is commit
[`b23acb266f88df81d960d36d58fb64ceaa0dd5ed`](https://github.com/veritaschain/vcp-spec/tree/b23acb266f88df81d960d36d58fb64ceaa0dd5ed),
the commit identified by `v1.2.0` when reviewed. Commit links, rather than the
movable `main` branch, fix the observations below.

| Source at that commit | SHA-256 |
|---|---|
| [VCP v1.2 English specification](https://github.com/veritaschain/vcp-spec/blob/b23acb266f88df81d960d36d58fb64ceaa0dd5ed/spec/v1.2/VCP-Specification-v1_2_en.md) | `ce94399bde111c8b805d3804fad2e6d61cab2f1839533d5009e94e812d15a942` |
| [Adopted VCP v1.2 annex](https://github.com/veritaschain/vcp-spec/blob/b23acb266f88df81d960d36d58fb64ceaa0dd5ed/spec/v1.2/VSO-SPEC-CHANGE-001.md) | `e810b952099f96c1f0841916be8c3babcb6adbfc48c05a236966d164fe11292b` |
| [VCP v1.2 event schema](https://github.com/veritaschain/vcp-spec/blob/b23acb266f88df81d960d36d58fb64ceaa0dd5ed/spec/v1.2/vcp-event-v1.2.json) | `fa73e3e76ebd939f84f6ac28dd6aadd08007aa753feb25f278d58ff02a74eac4` |
| [Python quickstart](https://github.com/veritaschain/vcp-spec/blob/b23acb266f88df81d960d36d58fb64ceaa0dd5ed/examples/python/quickstart.py) | `7f8351344667c349bd7d1c7897f388459f2548e58525e0c63d8b731b57279881` |
| [VCP v1.1 English specification](https://github.com/veritaschain/vcp-spec/blob/b23acb266f88df81d960d36d58fb64ceaa0dd5ed/spec/v1.1/VCP-Specification-v1_1_en.md) | `4224c41dd121aa8018b5f38284c5c56889b405c53023ee93472800b49b6f4050` |

Executable observations are preserved separately at vap-spec commit
[`9fa5fbc68075079b4599e16940e9078db976cd59`](https://github.com/veritaschain/vap-spec/tree/9fa5fbc68075079b4599e16940e9078db976cd59/experiments/vcp-v1.2-integrity-alignment):
[explanation](https://github.com/veritaschain/vap-spec/blob/9fa5fbc68075079b4599e16940e9078db976cd59/experiments/vcp-v1.2-integrity-alignment/README.md),
[probe](https://github.com/veritaschain/vap-spec/blob/9fa5fbc68075079b4599e16940e9078db976cd59/experiments/vcp-v1.2-integrity-alignment/probe.py),
and [saved result](https://github.com/veritaschain/vap-spec/blob/9fa5fbc68075079b4599e16940e9078db976cd59/experiments/vcp-v1.2-integrity-alignment/results/probe-output.json).
Their probe and result SHA-256 values are, respectively,
`88ffef24994da7640c3ca4b38aa3cce900c401d9ae6f7bfa79f038cc7c7c5e4e`
and `1a97314b4fe3ce0b4c9d401588cf2b1a1a9cacc46c175bec42c09c87f5ba594e`.

The probe reconstructs selected published algorithms and uses synthetic data;
it is not a test of every deployed producer. Counts below are those recorded
there, not a claim that this document reran or extended the experiment. The
v1.1 comparison here is textual, not a separate execution against that version.

## 3. Proposed technical erratum: Merkle construction and proof examples

**Affected material:** VCP v1.2 §§6.2.1–6.2.3 and the quickstart proof verifier;
the same specification examples appear in v1.1 §§6.2.1–6.2.3.

The specification requires RFC 6962 construction, but its tree builder
duplicates the last node on an odd level. Its path generator omits a sibling
when that sibling is absent from the stored level. Those choices do not form
a consistent implementation of the cited construction.

[RFC 6962 §2.1](https://www.rfc-editor.org/rfc/rfc6962.html#section-2.1)
defines recursive splitting by leaf count, with distinct leaf and internal-node
prefixes, rather than odd-node duplication. RFC 9162 retains that tree
construction. This discrepancy therefore predates RFC 9162; it is not merely
failure to follow a newer RFC.

The saved probe reports:

- Different roots at 11 tested sizes between 1 and 16: 3, 5, 6, 7, and 9–15.
- 19 of 136 generated paths fail against the builder's own root when folded
  using its domain-separated hashing rules.
- The quickstart's fold, which omits the leaf/internal prefixes, accepts 0 of
  those 136 paths.
- The duplicate-node construction gives the same root for `[e0,e1,e2]` and
  `[e0,e1,e2,e2]`; the RFC comparator distinguishes them. This is a structural
  ambiguity, not a collision attack on SHA-256.

**Proposed notice:** The published builder and path examples do not implement
the required RFC 6962 construction consistently. The quickstart verifier is
also incompatible with those prefixed hashes. Do not infer RFC conformance or
authenticated batch cardinality solely from successful root comparison using
these examples. The finite test counts above are not a universal failure rate.

**Separate repair decision:** Aligning construction, paths, and strict
size/index-aware verification is a technical correction in intent, but changes
some existing roots and proofs. Exact algorithms, scheme identification, legacy
verification, and the release/version decision belong in the normative-change
proposal. Existing signed roots and proofs must not be silently regenerated.

## 4. Proposed technical erratum: AnchorRecord coverage

**Affected material:** VCP v1.2 §§6.3.1 and 6.3.3; the corresponding v1.1 examples.

The sample `sign_merkle_root` signs only decoded Merkle-root bytes. The
AnchorRecord schema also carries `EventCount`, `FirstEventID`, `LastEventID`,
`PolicyID`, `Timestamp`, algorithm information, and an external target/proof.
The shown signature does not directly cover those additional fields. The
Silver example submits root bytes to the external timestamp service, rather
than a digest of the complete record. A signed root commits to leaf contents
under a specified tree construction, but does not by itself authenticate
arbitrary metadata attached to that root.

In probe P6, an actual synthetic Ed25519 root signature remains valid after
changing the claimed count from 8 to 6, the final event identifier from `e7`
to `e5`, and the policy identifier. All six presented paths pass a size-free
fold, including one with a generic depth check. The RFC size-6 comparator
rejects indices 4 and 5, while 0–3 still pass. Checking proof shape is necessary
but does not replace authentication of the claimed count and context.

**Proposed notice:** Validity of the example's root signature does not establish
the authenticity of the other AnchorRecord fields. Claims based on count,
endpoints, or policy need an explicit authenticated binding. The general
requirement to sign events and the optional SCITT encoding do not specify that
this particular signature covers the full record. An implementation with
separately signed metadata is outside this root-only demonstration until its
binding is examined.

**Separate repair decision:** A precisely encoded, domain-separated signature
over root, count, endpoint identifiers, policy commitment, version and algorithm
context is a proposed normative change, not an editorial reinterpretation of
an old signature. External receipts need an explicit commitment target that
avoids including a receipt in the bytes from which that same receipt is made.
Old root signatures may remain valid for their original message without
satisfying new metadata-authentication requirements.

## 5. Proposed technical erratum: exact numbers and JCS

**Affected material:** VCP v1.2 §§6.1.1 and 6.3.2, event-schema
`Header.TimestampInt`, and timestamp fields in annex syntax fixtures. The v1.1
§6.3.2 nanosecond integer example raises the same representation question.

The schema requires a nonnegative JSON integer for `TimestampInt`, describing
nanoseconds since the Unix epoch and preservation of 64-bit precision. The
hashing example uses JCS. [RFC 8785 §3.1](https://www.rfc-editor.org/rfc/rfc8785.html#section-3.1)
uses binary64 numbers and recommends strings where applications need greater
integer range or precision. Some integers above 2^53 are exactly representable;
it would be incorrect to say that JCS forbids every such value.

Probe P8 records a narrower result: Python `rfc8785==0.1.4` rejects all 40
fixture Header inputs when their timestamps are parsed as Python integers.
All 40 actual timestamp values in that set are exactly representable in
binary64, and equal-valued diagnostic float inputs are accepted for all 40.
This distinguishes a library input policy from numeric precision. It does
not show that those 40 timestamps were rounded, or that every JCS library
rejects them.

The additional diagnostic `1791504000000000001` does lose one nanosecond when
converted to binary64. Supporting arbitrary nanosecond integers exactly is
therefore a real cross-language serialization issue. Converting inputs to
floating point merely to pass canonicalization is not a proposed repair.

**Proposed notice:** The published integer wire type, exact-nanosecond intent,
and JCS processing need a single interoperable contract. The observed
library rejection and potential rounding are distinct findings. Schema-valid
JSON alone does not establish portable canonical bytes or preservation of an
arbitrary timestamp's exact value.

**Separate repair decision:** Decimal strings are the preferred candidate for
exact timestamps. Field-by-field units, lexical forms, signedness, ranges,
schema changes, hash inputs, and migration require normative review. Existing
financial strings, counters, enums, durations and future extension fields must
not be indiscriminately converted without such a field inventory.

## 6. Boundaries with other records

- The VAP observation's P5 identifies a separate event-to-leaf mapping issue:
  VCP hashes decoded EventHash bytes into leaves, whereas VAP Mechanism B
  describes canonical events. Settling the VCP preimage and leaf contract does
  not automatically settle that framework mapping.
- P7 concerns a reference verifier that identifies itself as **v1.1**. It is
  not evidence about a v1.2 production implementation. No implementation fix
  is included here.
- P9's alleged lost Draft 2 / RD-001 changes cannot be established without
  those originals and their disposition evidence. This proposal neither
  restores them nor treats them as adopted requirements.
- [VAP's compatibility-status correction](https://github.com/veritaschain/vap-spec/blob/2c5f4b6fc7078a3362c55c9ed5a8271f27360737/spec/v1.2/VAP_Framework_Specification.md)
  records v1.2 alignment under review and full conformance unestablished.
  Publication of this errata proposal does not establish a conformance mapping.
- K3 impact has not been determined. No baseline, fixture, expectation or
  prior result is invalidated or changed here; any future impact check must
  identify the actual version and code used and retain its own record.

## 7. Disposition requested

Review each of the three proposed notices independently and record whether
its source attribution, technical statement and scope are accepted, revised,
or rejected. Keep unresolved questions visible. These local section labels
are not allocated VSO erratum identifiers.

Before issuing an erratum, confirm the approval authority and record its
decision, affected versions, publication date and relationship to the separate
normative proposal. VCP §1.3's versioning commitments must be addressed before
any changed byte contract is released. No patch-version or backward-compatible
classification is presumed. No implementation, adoption vote, native-VCP
conformance run, or independent reproduction is claimed by this document.
