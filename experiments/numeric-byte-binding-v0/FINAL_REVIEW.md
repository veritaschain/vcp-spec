# Final review of PR #14 — 25 October 2026

**UNADOPTED research only. Independent third-party reproduction not established.**
Integrating the experiment is separate from adopting any numerical, byte,
signature, schema or migration rule.

Reviewed initial HEAD: `02b98c44cf973edc5ce704d8360cb8042caaac36`.
Pinned pre-PR base: `1131901d0b83f87c1c60674697574a60cc88fee1`.
This was an internal implementation/review exercise, not an external evaluator's
report or independent reproduction.

## Reproduced finding and correction

The internal Node crosscheck let presence of fields in the Python report select
which bytes to check. It also compared reported relations with expectations
without checking the report's comparison reference or deriving the relations.
Two altered copies of the stored Python 3.12 report exited **0 / PASS**:

1. In `event-malformed-signature`, insert an invented `event_signature` of 64
   zero bytes into the trace even though signature decoding was unavailable.
2. In `one-ns-stale-statements`, replace `reference` with `nonexistent-case`.

These are false acceptance of inconsistent **stored reports**, not demonstrated
false acceptance of the original signed evidence by the Python composition
checker. The original 45 fixture definitions/expectations and all initial
execution records are preserved. The initial reproduction observations are in
`records/review-reproduction-before.json`; the historical code and manifest
remain available at the reviewed initial commit.

The corrected crosscheck selects byte availability from the fixed fixture
expectations, recomputes the full expected trace and rejects extra/missing fields.
It verifies each reference and derives all 450 relations from those recomputed
traces. Per-case unadopted/independence/real-world-limit labels must also match.
The new `test_crosscheck.cjs` contains one positive and seven negative controls:
invented unavailable signature, changed reference, missing available signature,
invented invalid-anchor message, changed relation, swapped diagnostic
availability and false per-case independent-reproduction claim. A nonzero exit
must be an assertion rejection, not a subprocess/infrastructure failure.

## Validation and limits

- Both Python 3.12.14 and 3.14.3: all 45 cases match (12 PASS / 30 FAIL /
  3 UNASSESSED), and all 20 Python regression tests succeed without skips or
  expected failures. These counts mean expected failures are detected, not that
  45 evidence bundles are accepted.
- Node 24.19.0: 40 accepted candidate event hashes, 44 external commitments,
  88 actual Ed25519 verification outcomes and 450 relations match for each
  runtime's fresh report. All eight report controls pass for both reports.
- An additional review probe changed each of seven numeric/unit/time fields to
  nine invalid or stale values (63 checks); none became PASS or caused an
  unhandled exception. This is a bounded review probe, not an all-input claim.
- The fix changes only files newly introduced by this PR. All 176 pre-existing
  tracked files remain byte-identical to the pinned base. The current normative
  text, schemas, existing implementations/experiments, signed data, fixed
  distributions and K3 are unchanged. No tag/release operation is performed.

Node still does not independently implement numeric semantics, schema/shape
decisions or every JCS input. Its selection uses fixed fixture expectations,
and its exact comparison is local report consistency, not proof of who ran the
tests. Source/manifest consistency is not author/host authentication. Native
mapping, normalization, unit conversion, leap/smear policy, policy authority,
migration provenance and independent reproduction remain unresolved as stated
in the README. No new native VCP conformance or production claim is made.
