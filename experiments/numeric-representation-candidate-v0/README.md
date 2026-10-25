# Numeric representation experiment v0

**UNADOPTED research candidate. Independent third-party reproduction has not been
established.** No formal proposal number or target release is assigned. Publishing
or merging this experiment is not adoption, VCP conformance, certification, a
security guarantee, or validation of existing signed data.

This is a separate executable exploration of the units, ranges and representation
proposal merged in [PR #11](https://github.com/veritaschain/vcp-spec/pull/11), pinned
at `16018dd405cad45bd8b11a7dc2278f6d95111ea6`. It exercises the candidate in
[`proposals/numeric-fields-2026-10-25`](../../proposals/numeric-fields-2026-10-25/README.md).
It does **not** parse native VCP events or AnchorRecords, perform cryptographic
signature/Merkle verification, or modify current requirements or schemas. The
earlier byte-contract candidate, existing implementations, signed evidence,
fixed distributions/tags, releases and K3 remain unchanged.

## Reproduce

From a checkout of this PR's reviewed commit, with Python 3.12 or 3.14:

```sh
python3 experiments/numeric-representation-candidate-v0/run.py --output /tmp/vcp-numeric-new-run.json
```

Choose an unused output filename: the runner refuses to overwrite an existing
report. No pip install, Docker, root privileges, credentials or network access is
needed. Only the Python standard library is used. This runs the stored synthetic
vectors, compares **all** checks and exact derived values with declared expected
outputs, then runs the regression/negative-control suite. Exit 0 means all
expectations matched with no skipped or expected-failure tests. A mismatch exits
1; setup/integrity/report errors exit 2. Neither exit 0 nor the report's
`all_expectations_matched` is a VCP conformance claim.

The separate [experimental CI workflow](../../.github/workflows/numeric-representation-experiment.yml)
uses the same command on Python 3.12 and 3.14. The existing v1.2 schema workflow is
unchanged. CI runs are internal automated executions, not independent third-party
reproduction. Current local execution records and the two final-review fixes are
described in [final-review-2026-10-25.md](final-review-2026-10-25.md). The initial
[review-record.md](review-record.md) and its 533-case/15-test reports are preserved
as historical results for commit `5914539ea1c8930d0f6723a923e82bc72fee3ce0`.

To inspect one input, create a new research-request JSON file, for example:

```json
{
  "operation": "iso_pair",
  "ns": "1735128000123456789",
  "iso": "2024-12-25T12:00:00.123456789Z",
  "time_basis": "unix_no_leap"
}
```

```sh
python3 experiments/numeric-representation-candidate-v0/checker.py /tmp/numeric-input.json
```

The checker exits 0 for **PASS**, 1 for **FAIL**, and 2 for **UNASSESSED** or a
setup error (the latter emits an error to stderr). It reads at most 262,145 bytes
and rejects an input larger than 262,144 bytes. Inputs are never rewritten. It
uses strict UTF-8 JSON, rejects duplicate keys, NaN/Infinity, lone surrogates,
unknown/missing request members and non-string quantity substitutes. Extreme
JSON-number exponents beyond the exact parser's capacity produce a structured
`FAIL / json_number_range`, not a traceback or a rounded value. This
research envelope is closed; it is **not a proposed replacement VCP schema**.

## What the operations establish

| Operation | Numeric question | Important boundary |
|---|---|---|
| `scalar` | Does the named inventory entry fit its candidate representation, bound and exact unit label? | Header ISO/integer scalars still require pairing; indices require a count; policy-dependent/unmapped fields remain unassessed. A scalar sequence value does not prove continuity. |
| `iso_pair` | Do exact epoch ns and the proposed nine-digit UTC spelling agree? | An explicit `unix_no_leap` assumption is required; clock accuracy and source time basis are not proven. |
| `index_bound` | Is a proposed leaf/party index smaller than the supplied positive count? | This experiment does not authenticate counts, trees or parties; numeric PASS is insufficient for a Merkle proof or native conformance. |
| `within_tolerance` | Is the absolute difference of two epoch-ns values <= whole milliseconds × 1,000,000? | Comparison only; stored milliseconds are not converted or rewritten. |
| `duration_add` | Can seconds/ms/ns be added to epoch ns without exceeding the destination bound? | Arithmetic example only, not determination of a real deadline. N042 is used as a millisecond-quantity example, not a new deadline field. |
| `sequence` | Do two supplied ordinals strictly increase within the same actor/chain labels? | Gaps may pass; different identities remain unassessed. No signatures, authorized reset, origin or completeness are established. |

For each operation, all subchecks are retained. Aggregation is **FAIL before
UNASSESSED before PASS**; a failure does not erase unknown checks. Numeric results
are always accompanied by `protocol_conformance: not_assessed`,
`authentication: not_assessed`, `status: UNADOPTED`, and
`independent_reproduction: not_established`. The hash-pinned field map is local
review data, not an authority to label native input conformant.

The [field map](data/field-map.json) projects all 74 inventory review entries,
including legacy aliases, external formats and unsupported calendar/model types.
Each has one coverage vector. This does not mean 74 mandatory properties per
event, a full native-schema audit, or closure of arbitrary extensions. IDs N001–N074
refer to the prior inventory, not new protocol identifiers. The exact unit labels
(`unix_ns`, `s`, `ms`, `us`, `ratio`, `batch_events`, etc.) are **research-envelope
notation**. A matching caller-supplied label is not evidence of the measurement's
actual unit or of a signed policy binding.

## Corpus and expectations

The current corpus has **535 synthetic cases** with complete expected outputs:

| Expected operation outcome | Cases | Meaning |
|---|---:|---|
| PASS | 103 | The named limited numeric checks pass. |
| FAIL | 368 | Deliberately invalid, inconsistent or out-of-range input is rejected. |
| UNASSESSED | 64 | Missing evidence or an unresolved mapping prevents a full operation result. |

Coverage includes all nine integer classes; lower/upper/adjacent bounds;
2^53−1/2^53/2^53+1; 2^31 and 2^63 limits; signs, leading zeros, Unicode digits,
whitespace, exponent/decimal spellings, bool/number/null substitutions; exact
decimal envelopes, scale/length limits, signed zero and lexical preservation;
epoch/max ISO boundaries, one-ns mismatches, valid year-2000 and invalid year-2100
leap days, the source's 2024/2025 example mismatch; noncandidate offsets and
fraction widths; leap-second/smear uncertainty; seconds/ms/ns confusion;
tolerance boundaries; exact intermediate multiplication and destination overflow;
missing counts, index bounds and sequence wrap/gaps; malformed JSON and envelopes.

[`generate_vectors.py`](generate_vectors.py) declares inputs and expectations
without importing or calling the checker. Invalid verdicts/error codes and ISO
epoch answers are explicitly supplied; small helpers serialize results and use
exact integer arithmetic for expected derived values. The field projection is
shared review data, so this is **not an independent implementation or independent
oracle**. Review mistakes can be shared. By default the generator compares stored
bytes; `--write` replaces only this new experiment's `data/vectors.json`.

[`manifest.json`](manifest.json) pins the eight source files and six executable/
data files by SHA-256, plus case/test counts. The runner requires the complete,
exact file lists, typed positive counts and valid SHA-256 strings before checking
hashes: deleting a fingerprint cannot remove that file from the audit. It checks the
field-map hash embedded in the checker, deterministic fixture bytes, all 74
coverage IDs, all six operations, duplicate/missing cases and complete expected
outputs. Reports include both expected and actual results, category counts,
source and implementation hashes, Python version and regression output. Hashes
detect changes relative to this checkout; they are not signatures, trusted time
receipts or proof of who ran the program. Preserve the report with the exact PR
commit when reproducing. The record writer refuses overwrites, but no filesystem
or release immutability is claimed.

The 18 regression tests include negative controls for lost precision, false
universal PASS, omitted unknown checks, empty results, altered unit catalogs,
removed/duplicate cases, incomplete expectations, JSON type conflation,
duplicate keys, skipped/expected-failure suites, CLI statuses and input
preservation, extreme exponent traps and removal of a changed source copy from
the manifest. No test depends on a `signature_valid` flag; such an extra member is
rejected. No signatures are claimed to have been checked by this experiment.

`lexeme` and `utf8_hex` preserve the decoded numeric **string content** exactly,
including leading/trailing zeros and negative zero. They are not the original
JSON escape spelling, JCS serialization, event hash or signature bytes. No number
is rounded to binary64, and no accepted decimal is trimmed or rescaled. Stored
source records and signed data are not used as mutable fixtures.

## Unresolved decisions and migration boundary

| Decision still open | Experimental treatment |
|---|---|
| Adoption/version, capacity and pre-epoch times | Uses PR #11's signed-63-bit/nonnegative and signed-31-bit candidate ranges only. No assertion that today's schema enforces them; uint64 and negative epochs are not silently accepted. |
| UTC/leap policy and actual clock time basis | Integer calendar conversion under `unix_no_leap`. Syntactically positioned `:60` is unassessed without asserting that a leap occurred; smear/negative-leap/unknown bases are unassessed. Invalid date/clock fields still fail. |
| Required parents/events, aliases and native mapping | Closed research requests only. No whole-event requiredness, flat/nested confidence conflict resolution or legacy/structured precedence. Header pairing is a separate operation. |
| Signed unit/policy bindings, instruments and model semantics | Decimal syntax can pass while unit/semantic checks remain unassessed. No currency, lot, tick, VaR window, slippage convention, feature type or bound is inferred. No percent-to-ratio guess. |
| Count authentication and sequence recovery policy | Supplied counts/identities are synthetic. No proof verification; no authorized chain reset, gap-free requirement or evidence of omitted real events. |
| Calendar durations, external receipts, legacy aliases/enums and extensions | Unassessed rather than converted. External COSE/CBOR formats and their signatures remain under their own contract. |
| New signed bytes and transition | No migration writer is supplied. Number-to-string conversion, changed units or new bounds would require an identified future format and newly produced evidence. Old signatures/data must remain preserved. |
| Real-world operation and external reproduction | Neither is established by these internal numeric exercises. Independent participants must execute and report their own run separately. |

These limitations retain the [prior proposal's release gates](../../proposals/numeric-fields-2026-10-25/README.md#5-migration-impact-and-release-gates).
This experiment supplies evidence for discussing that proposal; it changes no
normative acceptance rule, current schema, registered profile, existing verifier,
production library, published distribution or K3 criterion.
