# Final review of PR #11 — 2026-10-25

**UNADOPTED discussion draft. Independent third-party reproduction has not been
established.** Incorporation of the inventory, candidate choices and migration
analysis does not adopt numeric requirements or amend the current v1.2 contract.

Reviewed head: `0a5072d39af83a02790a823b443293a9d47b6c59`.
Base: `9d272b93fe6809df25c415390577903e716015de`.
The original [review record](review-record.md) describes preparation at that
head; it is not evidence that the negative cases below had been tested then.

## Findings and repairs

### 1. Type-coercing comparison could accept an inaccurate schema snapshot

In a temporary copy, change N002's recorded minimum from integer `0` to `false`,
or N013's `1` to `true`, and regenerate the corresponding inventory.md. The old
audit reports `inventory_consistency_pass`: Python equality treats these pairs
as equal. Changing integer `0` to floating-point `0.0` also passes. The boolean
changes are not valid numeric constraints; the float example illustrates that
the claimed exact parsed snapshot was not actually preserved.

Repair: recursively compare both type and value in snapshots, including nested
structures and repeated schema expansions. The audit now rejects all three
mutations. This is a source-record comparison rule, not a claim that JSON Schema
numeric minimum `0.0` has different mathematical semantics from `0`, and not a
change to a VCP parser.

### 2. Duplicate JSON keys could hide contradictory status or constraints

In a temporary copy, prepend `"status":"ADOPTED"` before the existing
`"status":"UNADOPTED_DISCUSSION_DRAFT"`. The old parser keeps the latter and
the audit passes, although the file contains conflicting status claims.

Repair: reject duplicate keys at every nesting level while reading the manifest,
inventory and source schema. Also reject `NaN`, `Infinity` and `-Infinity`, which
Python's default JSON parser accepts as extensions. Existing unique-key source
files and the 74-entry inventory are unchanged.

The controlled before/after results are preserved in
[final-review-regressions.json](final-review-regressions.json). The corresponding
executable regressions are in [test_audit_inventory.py](test_audit_inventory.py).
All malformed inputs are generated in temporary copies; no live specification,
schema, signed record or fixed fixture was mutated.

## Final validation and scope

- Re-ran the inventory audit on Python **3.12.14** and **3.14.3**: both pass,
  with **34 definition sites, 35 schema instance paths, 74 review entries**.
- Ran the new audit regression suite on both versions: **10 tests pass** on each,
  with no skips/expected failures. It covers the two findings, non-JSON constants,
  missing schema paths, constraint drift, requiredness types, source hash drift,
  generated Markdown drift and the read-only success path.
- Rechecked named integer/decimal/time fields against the pinned body, schema,
  annex and inherited v1.0 sections. No additional manual field was inferred from
  a numeric code or benchmark value. Open extensions and prose-requiredness gaps
  remain explicit; a matching inventory is not full protocol conformance.
- Candidate 31/63-bit bounds, decimal capacities, unit/policy bindings and the UTC
  subset remain proposed choices. No byte-contract v0 mapping or native VCP
  parser is implied. No undocumented authority or adoption decision is supplied.
- Inventory JSON, generated field inventory and source-hash manifest remain
  byte-identical to the reviewed head. Review fixes are confined to this proposal
  directory's audit, its documentation and new regression/review records.
- The existing **151 base files** are byte-identical. Current requirements,
  schemas, existing implementations/vectors, signed data, distributions and K3
  are untouched. The regular GitHub v1.2 contract CI is separate and must pass
  on the final PR head before merge; see the PR's check run for that result.

No blocking issue remains for **incorporating this unadopted discussion material**
after the final-head checks pass. This conclusion is limited to the reviewed
sources and scope. It does not resolve the documented adoption blockers, approve
production use, establish independent reproduction or authorize a new release.
