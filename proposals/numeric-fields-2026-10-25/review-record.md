# Internal inventory review — 2026-10-25

**Unadopted discussion material. Independent third-party reproduction has not
been established.** This is an internal document/source-coverage check, not a
native VCP verifier result, cryptographic validation or normative approval.

## Fixed inputs and change boundary

- Inventory sources are pinned to `e984d85311f57338065570d7679ddff92718001b`;
  exact bytes and hashes are identified by [sources.json](sources.json).
- During preparation, main advanced to
  `9d272b93fe6809df25c415390577903e716015de` (PR #6), changing only root README.md
  and spec/v1.2/README.md. The new proposal branch includes that update. None of
  the four inventoried sources changed, so their fixed baseline is retained.
- All **151 files** already tracked at that updated base were compared byte for
  byte against the working tree: **0 changed**. This proposal adds files only
  inside `proposals/numeric-fields-2026-10-25/`.
- No existing tests, implementation, schema, current normative text, previous
  proposal/vector data, signed data, distribution, release, tag or K3 artifact
  was modified. No release or remote setting operation is part of this work.

## Checks performed

From the repository root:

```sh
python3 proposals/numeric-fields-2026-10-25/audit_inventory.py
```

The read-only audit was run with **Python 3.12.14 and 3.14.3**, using only their
standard libraries. Both returned `inventory_consistency_pass`, with:

| Measurement | Result |
|---|---:|
| SHA-256-checked input sources | 4 |
| Matching root mirrors | 2 |
| Schema scalar definition sites | 34 |
| Expanded schema scalar instance paths | 35 |
| Missing/extra snapshotted schema paths | 0 |
| Additional manual/prose/context entries | 39 |
| Total review entries | 74 |

The audit also checks exact scalar constraints and leaf requiredness against the
source, citation line bounds, unique IDs/paths and generated Markdown consistency.
Actual inventory SHA-256 is printed by the command, so the report can be bound to
the JSON bytes without a circular self-hash. The audit file and these records
are themselves identified by the PR commit.

README.md and inventory.md were parsed/rendered locally using `marked` on
Node.js v24.19.0. README produced three tables (7, 9 and 9 data rows), and the
inventory produced all 74 field-entry headings. Local relative links were checked.
The regular repository CI result is separate, visible on the Draft PR; an inventory
audit does not replace the existing v1.2 contract suite.

## Manual review and remaining limits

- Compared the body, GA schema and adopted annex, then consulted v1.0 §§4–5
  because v1.2 explicitly delegates its core/module definitions there.
- Separated current schema constraints, prose descriptions, observations and new
  candidate choices. Kept unit gaps, native-schema gaps and requiredness questions
  visible instead of filling them by name or integer magnitude.
- Recomputed the body §6.3.2 integer time using integer divmod/calendar arithmetic:
  `1735128000123456789` ns is in **2024**, not its paired ISO example's **2025**.
  Also checked the proposed maximum: `9223372036854775807` ns maps to
  `2262-04-11T23:47:16.854775807Z`. No source example was repaired by this work.
- Confirmed the audit's coverage boundary: it enumerates named schema scalars
  and checks the manually recorded entries' consistency; it does **not** prove
  that all possible values in open objects/extensions have been specified.
- Candidate decimal capacities, sign choices, UTC subset, policy units/scale,
  extension mappings, presence rules for prose-only fields, signed-byte mappings
  and migration/version decisions still require review and adoption.
- No new candidate numeric validator, native serialization, cryptographic test
  vectors or production parser was implemented or executed here. The earlier
  byte-contract v0 and its internal test record remain unchanged; this inventory
  does not extend the meaning of their results.

These checks were performed in the implementation team's environment. Two local
Python versions and local rendering do not constitute independent reproduction.
