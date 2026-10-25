# Internal preparation review — 2026-10-25

**UNADOPTED. Not effective. Independent third-party reproduction not established.**
No current native-format support or formal adoption is claimed.

The recorded executions used implementation commit `c9694a4bd7372b79108ae13bdc9e2eab8a691e0e` on the author's
macOS environment, Python 3.12.14 and 3.14.3.
Both runs identify the same code/input manifest digest:
`sha256:13f15e978ba7b0791c3307cb80defdb8a39fb51b8c59e385c2124d0ce04b82c0`.
This content digest identifies the experimental files, not a signed operator or
host attestation. The later record/document commit does not change that code.

## Executed checks

| Check | Result in each runtime |
| --- | --- |
| Synthetic bundle cases | 55 expectations matched: 6 PASS, 36 FAIL, 13 UNASSESSED |
| Separate unit-conversion cases | 14 matched: 5 PASS, 4 FAIL, 5 UNASSESSED |
| Additional regression controls | 25 passed; no skipped/expected-failure/unexpected-success tests |
| Complete saved-report recomputation | Matched, including all fields and environment/dependencies |
| Report mutation controls | All eight edited/omitted/forged reports rejected |
| Cross-runtime comparison | Case verdicts, unit results, regression outcomes and implementation/input digest identical |

The measures overlap and must not be summed into an independent-validation count.
A suite success means that the expected negative and unsupported outcomes were
observed, not that all evidence qualified. The fresh runner computes every verdict;
it does not accept a supplied success flag or replay a stored report as evidence.

## Review boundaries and counterexamples

- Placement: the selected full Header and limited module paths are committed;
  missing/misplaced ISO, unknown fields/modules, an input validity flag and
  stripped/relabelled Origin cannot pass the closed research schema.
- Interpretation: exact ns integers survive the binary64 boundary. ISO offsets
  need known semantics; out-of-range times, smear/leap bases, unsupported source
  formats/inner approvals and inexact integer-destination conversions are not
  converted into successes. Preserving fractional microseconds can pass while a
  separate integer-ns conversion is unsupported. Ratio 75 is not treated as 75%.
- Authority: a selected policy digest does not implement new policy semantics.
  Signatures are actually verified with distinct public test roles/domains.
  Missing configured authority stays unassessed. Known failures remain failures
  when another role/event is unassessed; the controls exercise both mixtures.
- Retention: changed raw copies/signatures, omitted old proofs and changed opaque
  receipts fail. Coherently replacing source records and their manifest also fails
  against the separately retained manifest pin. This pin is an input trust
  boundary, not evidence authenticated by this program.
- Derivation: explicit source-entry mapping, new IDs and target chain, protected
  origin/acyclic plan, exact conversion and separately signed target-artifact
  binding are checked. Correctly re-signed false content still fails the relevant
  semantic/binding checks. Original opaque receipt authenticity stays unassessed.
- Reports: expected totals alone are insufficient. Whole-report typed comparison
  rejects omission, altered verdicts, forged input/implementation hashes,
  dependency changes and boolean-for-integer replacement.

No new native converter, real receipt/clock adapter, production authorization,
COSE/PQC support, general per-field attestation schema or operating migration was
validated. The plan uses one selected rule, and its attestation binds artifacts
rather than signing the checker verdicts. The README and coverage map retain all
74 dispositions: nine selected exercises, one new claimed-time scalar with no
legacy equivalence, and 64 unassessed entries. No existing VCP record is invalidated
by failure against this research subset.

## Preserved scope and records

All **204** files present at base `517d407f507fd6401bc6edb4979b5a6673122d40`
were checked byte-for-byte unchanged. Changes add only this experiment directory
and `.github/workflows/native-layout-migration-experiment.yml`. Existing CI,
specification/schema files, implementations, signed artifacts, fixed distributions,
release tags, DOC-SYNC and K3 remain untouched. No external evaluation, notification,
release, deployment or merge is authorized by this preparation record.

The following are internal saved outputs, not independent evaluator reports.
The records can be freshly verified in the matching recorded runtime. Their hashes
identify these exact files; neither hashes nor CI authenticate who ran them.

| Saved output | SHA-256 |
| --- | --- |
| [records/python312.json](records/python312.json) | `dbb9086d5e5d5b1a1fe404f1d82ffd9c1ca61f709fc773f0c26faff77f53d2cd` |
| [records/report-controls312.json](records/report-controls312.json) | `c86018153d1959c106dbd354e667a79c46a1009adf49187e3aee716b176c75f8` |
| [records/python314.json](records/python314.json) | `dd0419e3fe7873733ecf1ac51f1ab38735a29e609566bf2ba21a5ffa2aff6383` |
| [records/report-controls314.json](records/report-controls314.json) | `c86018153d1959c106dbd354e667a79c46a1009adf49187e3aee716b176c75f8` |
