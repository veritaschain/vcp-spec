# Final review: PR #10, 2026-10-25 JST

**Unadopted synthetic candidate; independent third-party reproduction
unestablished.** This records internal review, not normative adoption or a
native VCP conformance assessment. The implementation of the current protocol,
prior signed data, fixed distributions and K3 are outside this change.

Reviewed initial HEAD: `93e57393a25487622ae29a2b44160088cc70078e`.
Base: `9b88e318aeb9575de66047ed49c8ab86c2879487`.

## Findings and corrections

| Finding | Before correction | Correction and regression evidence |
|---|---|---|
| Node completion was not verified | A test executable returned `{}` and exit 0 without running Node or checking vectors; `check.py` still reported success | Require the expected result shape/status, contract, both input hashes, exact integer check counts and environment metadata. The same stub now exits 1 without a success report; nine invalid-report controls are rejected |
| Identity/role trust coverage was incomplete | A test-only mutation selected keys by role while ignoring ProducerID, StreamID and KeyID; the entire original suite still passed. The original `signature_check` itself did use the correct tuple lookup | Test trust now comes from explicit generator-side public test configuration, not statement fields. Six correctly signed identity substitutions and two role mismatches stay unknown. The same mutated lookup is now caught; raw signature validity stays a separate check |
| Byte-input JSON encoding bypassed the stated rule | Python's default byte parser accepted UTF-8 BOM and UTF-16 inputs despite the documented UTF-8/no-BOM contract | Strict UTF-8 decoding and BOM rejection precede parsing. Six byte/input-type rejection controls and a valid Unicode UTF-8 control pass |

`regressions-before-after.json` retains the observed pre-fix false acceptance
and the post-fix rejection. The mutation was injected only into a temporary
test process; the deliberately incorrect trust lookup was never installed in
the candidate or any existing verifier. The empty executable was also a
temporary local control, not a runtime used to claim real byte agreement.

## Validation and preservation

`python-3.12.json` and `python-3.14.json` contain complete stdout from
`check.py --node <Node 24.19.0 executable>` using Python 3.12.14 and 3.14.3.
Each final run exited 0 with no stderr. Both run in the same internal macOS
development environment; actual crypto/package/runtime details are recorded.
This is not a Linux run, a separately operated evaluation, or host attestation.

The original 135 event vectors, 68 tree sizes, 2,529 positive membership paths,
168 numeric cases, 33 signed-field mutations and eight signed inconsistent
anchors still agree with expected outcomes. Extra review checks cover the
findings above; the separate Python/Node byte computations agree. Counts
overlap and are not a tally of independent tests. The external receipt, time,
production trust, partial-disclosure and native-format limitations remain.

The new `source-data-sha256.json` identifies the corrected candidate inputs and
code used by these runs; it excludes `records/` to avoid recursive hashes.
The containing Git commit identifies the review records. As before, a fully
forged report is not prevented by comparing hashes/counts; this validates
completion/consistency evidence, not the operator or executable's authenticity.

Both `data/vectors.json` and `data/merkle-vectors.jsonl` are byte-for-byte equal
to initial HEAD `93e5739`. No synthetic signature, preimage, root or proof was
replaced. The original 2026-10-24 run outputs and original manifest are retained,
with their historical commit identified in the parent record index.
Only the candidate folder changes in this PR; all 132 paths present at the base
remain unchanged. Existing v1.2 CI is checked separately and is not described as
a test of this candidate. Merging this PR does not complete the open adoption
gates or change any unadopted experiment's status.
