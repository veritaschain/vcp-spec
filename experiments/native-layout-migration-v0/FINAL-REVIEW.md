# Final internal review — 26 October 2026

**UNADOPTED. Not effective. Independent third-party reproduction remains not established.**
This review permits research material to be merged; it is not normative adoption,
a native VCP migration claim, or an independent evaluation.

Reviewed starting HEAD: `61a6b812f90ef13f0438484c63dd403d17687f5a`. Repaired implementation: `5330244c714f6c548a87114bd394fc6d7113b0de`.
The final report/document commit adds records without changing the checked code.
The code/input manifest digest is `sha256:78f5c1316bd7dd524d8645ce3a998b0be2a37a3de3419522e2182516350bb2f5`.

## Reproduced defects and repairs

[Before/after counterexamples](records/final-counterexamples.json) were executed
against the actual old and repaired checker in the same internal environment.
They are not merely extracts of the relevant functions.

| Counterexample | Before | After |
| --- | --- | --- |
| Decoded policy is an array | Uncaught AttributeError | policy_binding FAIL |
| Source ISO second is 99 | UNASSESSED | FAIL |
| Inexact duration plus ratio 75 | Known invalid ratio hidden by UNASSESSED | FAIL; both findings retained |
| Unknown source time plus another row's changed milliseconds | UNASSESSED | derivation_binding FAIL; source interpretation remains UNASSESSED |
| Unknown source/target time plus invalid ratio in that event | UNASSESSED | numeric_time and derivation_binding FAIL |
| Source ActorID and configured SourceActorID both null | Covered-subset PASS | Malformed context FAIL |
| Missing event key plus malformed signature encoding | UNASSESSED | cryptographic_integrity FAIL |

Policy parsing now checks object type explicitly, rather than broadly catching
AttributeError. Both roles are tested with array, null, string, integer and
boolean values: all ten inputs return structured FAIL, including through the
actual CLI (exit 1, JSON output, no traceback). They do not represent a
cryptographic bypass; the original defect was an input-handling crash.

The context repair closes a separate false-PASS path for a malformed selected
source identity; it does not authenticate a production identity. Calendar and
second ranges are checked before treating leap mapping as unavailable. Known
numeric, signature-encoding and derivation checks run independently of missing
keys/pins and unsupported fields. Unsupported formats are not guessed: only
identified, supported source fields can supply comparison values. Every source
prerequisite is still required for PASS. No new unit, time basis or native format
was introduced, and unknown fields still cannot become successful conversions.

## Executed validation

Each runtime, Python 3.12.14 and 3.14.3 on
macOS, produced:

- 62 bundle expectations matched: 6 PASS, 43 FAIL, 13 UNASSESSED.
- 14 exact-unit expectations matched: 5 PASS, 4 FAIL, 5 UNASSESSED.
- 39 regression tests passed, with no skips, expected failures or unexpected successes.
- Complete saved-report recomputation matched; all eight report mutations rejected.
- Case/unit/regression results and code/input digest agree across both runtimes.

The original 55 authored expectations remain unchanged. Seven counterexamples
and fourteen regression tests extend coverage; counts overlap and are not an
independent-validation total. Reports:
[3.12](records/final-python312.json), [3.14](records/final-python314.json),
[3.12 mutations](records/final-report-controls312.json),
[3.14 mutations](records/final-report-controls314.json).
Historical reports and [preparation review](REVIEW.md) are preserved for their
stated original commit and are not relabeled as results of this revision.

## Baseline and remaining limits

While review was ongoing, main incorporated separate PRs #13, #17 and #18.
Those changes are retained. The baseline manifest now pins all 204 existing
files at `943d513fec3c0eaa7eb683120e2d82d5eb748285`; all were checked unchanged
by this PR. PR #15 remains the proposal source at its separately cited commit.
The diff adds only this experiment directory and its dedicated read-only CI
workflow. Current norms, current schemas, existing implementations, signed data,
fixed distributions and K3 are not modified by this PR.

All L/U/T/M/G decisions listed in the README remain open. The 74-entry coverage
map still has nine selected exercises, one different-semantics claimed time
scalar and 64 unassessed entries. Physical clock truth, opaque receipt meaning,
production authority, full native schemas, inner approval handling and external
independent reproduction remain unassessed. A merge is solely acceptance of
bounded research material and these internal records.
