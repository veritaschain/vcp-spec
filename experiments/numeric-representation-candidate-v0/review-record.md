# Internal review and execution record — 2026-10-25

**UNADOPTED; independent third-party reproduction has not been established.**
These are internal synthetic executions performed during preparation of a Draft
PR. They neither adopt the numeric proposal nor validate current VCP signed data.

## Fixed inputs and scope

- Source/base: `16018dd405cad45bd8b11a7dc2278f6d95111ea6`, the merge of PR #11.
- Source and experiment SHA-256 manifest: [manifest.json](manifest.json).
- Manifest SHA-256: `e9c9a6efcf32e16d15d34bfa5ea170cbb4823fcd9dd9950a34b1af5e46aa76a3`.
- Stored vectors SHA-256: `659eb4aa96f27d5eef77ea2a1086f7c37e42b261380c6ea11db2529f4c4e2b2c`.
- All **160 tracked baseline files** were compared byte-for-byte with that base;
  none changed. Additions are the isolated experiment directory and a separate
  read-only CI workflow. No existing workflow, normative body, schema, inventory,
  implementation, signature/evidence data, fixed distribution or K3 file changed.
  No release/tag/data replacement is part of this work.

The field-map source hash is checked against the PR #11 inventory. Unit labels
and open-decision flags are additionally pinned as experiment data. All 74 review
IDs have mapping examples; class boundary tests are representative of the shared
parsers, not a claim that all possible native paths/conditional combinations are
exhaustively validated.

## Internal executions

Both runs used the Python standard library on Darwin. The command, from the
repository root, was:

```sh
python experiments/numeric-representation-candidate-v0/run.py --output <new-report-path>
```

| Python | Report | Expected results matched | Regression tests |
|---|---|---:|---:|
| 3.12.14 | [python-3.12.json](records/python-3.12.json) | 533 / 533 | 15 / 15 |
| 3.14.3 | [python-3.14.json](records/python-3.14.json) | 533 / 533 | 15 / 15 |

There were zero mismatches, skips, expected failures or unexpected successes.
Expected operation outcomes were **103 PASS, 366 FAIL, 64 UNASSESSED**. Thus
"533 matched" means that deliberate failures and unknowns were retained, not that
533 inputs were accepted. Each report preserves every expected and actual check,
exact derived values, file hashes, runtime, test counts and test output.

Report SHA-256 digests:

- Python 3.12: `c959ba85fd4d4a39997e83777071db760ebb13fec9805995c7b5d77e32d42bff`.
- Python 3.14: `d04f5954e575f50a271aa83c9d12135c8d8a5e0dfd57bb3a7272233cd63aa0cc`.

## Arithmetic and harness review

Eight accepted ISO conversions were also recomputed internally using Node
24.19.0, independently of Python's `date` arithmetic: parse the whole-second
portion with `Date.parse`, convert its exact integral milliseconds to BigInt,
multiply by 1,000,000 and add the nine-digit fraction as BigInt. No ns value is
parsed through a JavaScript Number. All eight values agreed:

| Case | Exact converted epoch ns |
|---|---|
| Epoch | 0 |
| Epoch + 1 ns | 1 |
| 2000-02-29 | 951782400000000000 |
| 2100-03-01 | 4107542400000000000 |
| Source's 2024 date | 1735128000123456789 |
| Upper bound | 9223372036854775807 |
| Deliberate 1 ns pair mismatch | 1 |
| Source's 2025 date/pair mismatch | 1766664000123456789 |

The latter two confirm the conversion value while the pair check deliberately
fails. This spot check is not a second full checker or third-party reproduction.

Negative controls confirmed that the harness detects an implementation returning
empty results, unconditional PASS, removal of UNASSESSED checks or removal of
exact values. It rejects empty/duplicate/missing coverage, partial expected
results, ambiguous transports, and skipped/expected-failure regression summaries.
A modified field-map unit is rejected by its hash. True/1 and 1/1.0 do not compare
equal as typed JSON records. Duplicate keys, non-finite tokens, invalid Unicode
and oversized/deep JSON are rejected. CLI checks also confirmed distinct result
exit codes and preservation of the input file.

## Limits and review decisions still open

- The checker, expectations and field map are authored in the same work. Their
  agreement is internal validation and can share mistakes; hashes do not certify
  the author, execution host or observation time.
- Unit-label matches are syntax/relationship checks. Count, identity, time-basis
  and policy authenticity are not established. No signature or Merkle proof is
  verified here; the prior byte-contract experiment is untouched.
- The candidate's capacities, UTC/leap policy, native mapping/requiredness,
  decimal policy bindings, external formats, recovery policy, transition/version
  and approval authority remain unresolved as listed in [README.md](README.md).
- Existing v1.2 data must still be judged under its identified existing contract.
  This code supplies neither a migration writer nor new acceptance requirements.
- The separate workflow runs this experiment in CI. Its results are additional
  internal executions; merely defining the workflow does not claim a CI run or
  independent reproduction. Check the Draft PR's actual checks for CI status.

Publication remains a **Draft PR**, not a merge or adoption decision.
