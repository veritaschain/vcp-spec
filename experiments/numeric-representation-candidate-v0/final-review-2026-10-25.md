# PR #12 final review — 2026-10-25

**UNADOPTED research candidate. Independent third-party reproduction has not been
established.** Integrating this experiment is not adoption, native VCP
conformance, validation of existing signed data or a new normative requirement.

Reviewed initial HEAD: `5914539ea1c8930d0f6723a923e82bc72fee3ce0`.
Unchanged source/base: `16018dd405cad45bd8b11a7dc2278f6d95111ea6`.
The review was internal; no independent reviewer or external execution is claimed.

## Findings reproduced and corrected

### 1. Extreme JSON number exponents escaped structured rejection

An input quantity token `1e9223372036854775808` or
`1e-9223372036854775809` raised `decimal.InvalidOperation` during JSON decoding.
The parser caught ValueError/RecursionError but not DecimalException, so the
checker emitted a traceback rather than its structured result. These JSON number
tokens are not accepted candidate quantity strings; no numeric representation
rule needed changing to reject them safely.

The parser now translates DecimalException into `FAIL / json_number_range`.
Two synthetic vectors cover the positive and negative exponent paths. The added
regression also invokes the CLI and checks exit 1, the complete expected JSON,
and empty stderr. Neither a rounded number nor an unassessed success replaces
the rejected input.

### 2. Removing a manifest entry silently reduced fingerprint coverage

The runner checked the hashes that were present but did not require the complete
file inventory. In an isolated temporary copy, a source file was altered and its
`sources` entry removed; `verify_setup()` still accepted all 533 original vectors.
The actual specification file in the repository was never modified.

The runner now checks the closed manifest envelope, exact eight source paths and
six experiment paths, positive integer counts (excluding bool/float substitutes),
and 64-character lowercase SHA-256 strings before reading fingerprints. Missing
or unexpected files fail setup. A copied-source regression reproduces the prior
bypass and verifies rejection; additional cases exercise manifest shape, digest
types and counters. These checks remain relative to the reviewed checkout, not
signature-based provenance or protection against coordinated code/manifest edits.

Machine-readable [before/after controls](final-review-regressions.json) preserve
the original exceptions and omitted-entry acceptance separately from their fixed
outcomes. All alterations used to demonstrate the second finding were confined
to temporary copies.

## Final internal execution evidence

| Runtime | Record | Vector expectations | Regression tests |
|---|---|---:|---:|
| Python 3.12.14, Darwin | [final-python-3.12.json](records/final-python-3.12.json) | 535 / 535 | 18 / 18 |
| Python 3.14.3, Darwin | [final-python-3.14.json](records/final-python-3.14.json) | 535 / 535 | 18 / 18 |

Both executions had zero mismatches, failures, errors, skips, expected failures
or unexpected successes. The expected operation results are **103 PASS, 368 FAIL,
64 UNASSESSED**. Negative and unknown cases are expected outcomes, not accepted
native VCP records. The existing workflow remains responsible for its unchanged
six current-schema tests; actual final-HEAD CI status is available on the PR.

The command remains:

```sh
python3 experiments/numeric-representation-candidate-v0/run.py --output <unused-report-path>
```

| Artifact | SHA-256 |
|---|---|
| Current manifest | `e1cd0f67e557f59c496bcb129c31fcefdadedc9ce404015ab8120c9104635803` |
| Current vectors | `6a6812db1ebb66e0912fe7eb02378804403a5f3ad04f740341ac1018783efdd2` |
| Final Python 3.12 report | `a5ea46127df37b94b4b520526d1ad349d13109f13d514949e542e5c886a9116a` |
| Final Python 3.14 report | `4c4a65dda6be9b45cea3dadb33e319d2471cbc7c15b2e0a916bd2f85a412317f` |

The previous 533 input/expected-result definitions remain identical; only two
new vectors were added. The initial [review record](review-record.md) and both
initial execution reports remain byte-identical to initial HEAD and must be read
as historical evidence for that commit, not as results of the corrected checker.

## Scope and disposition

All 160 tracked baseline files remain byte-identical. Changes are confined to
the new experiment and its separate read-only CI workflow. Current normative
requirements, schemas, VSO-SPEC-CHANGE-001, PR #11's inventory/auditor, earlier
experiments and implementations, signed evidence, distributions, release assets,
fixed tags and K3 were not edited. This review does not introduce a migration
writer or change any acceptance criterion for existing data.

The bounds, arithmetic, exact-string preservation, unit checks, ISO pairing,
aggregation precedence and explicit unknowns were reviewed against PR #11.
Outstanding native mappings, signed policy/unit bindings, authentic counts,
leap/clock policies, version/adoption choices and independent reproduction remain
open as described in [README.md](README.md).

No further blocking finding was identified within this internal review's scope
after the two fixes. The recommended disposition is integration of the synthetic
experiment only, contingent on successful checks for the reviewed final HEAD;
normative adoption and independent reproduction remain separate, unestablished
outcomes.
