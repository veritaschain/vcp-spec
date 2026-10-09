# VCP v1.2 GA consistency correction — 2026-10-09

The earlier PR #1 merge (`f833b52e52310900ce82f6d0726b635667a4f55b`)
contained two P1 wire-contract inconsistencies. No `v1.2.0` tag existed when this
correction was prepared. The historical GA declaration (2026-07-06) must not be
confused with a verified tagged release.

## Corrected contract

- Five system codes are registered verbatim in the schema and EN/JA/ZH registry.
  Annex §1.4.10 specifies their module paths, required data and authorization rules.
- ERASURE uses `Payload.VCP-PRIVACY.ErasureDetails`, with one authoritative reason
  enum. The Annex and main text now describe this same representation.
- The pre-GA compact schema remains available only for explicit archival reads.
  Incomplete old records cannot be upgraded by inventing authorization or
  destruction evidence. Signed bytes must never be rewritten; see Annex §3.4.3.
- Inclusion proofs for an ERASURE event are detached from its hashed Payload,
  avoiding a self-referential hash/proof dependency.
- Storage pressure cannot justify dropping unanchored evidence. CHECKPOINT cannot
  bypass advance notice or the two-person emergency route (§10.5).

## Compatibility assessment

| Input / consumer | Impact |
|---|---|
| Existing non-ERASURE structured events | Existing field rules retained; core/error vocabulary retained |
| Old strict event-enum validator | Rejects the five newly registered system codes; update before use |
| Pre-GA compact ERASURE producer | Must migrate to nested detail contract; deliberately rejected by GA schema |
| Pre-GA signed compact ERASURE history | Original bytes and validation context retained; explicit historical schema |
| Former root-level Annex ERASURE sketch | Not a GA encoding; historical inspection only |
| RC1-to-GA technical identity claim | Withdrawn; this correction changes wire format and validation |
| Historical v1.0/v1.1 encoding | Original version-aware verification remains necessary; this structured schema is not a universal decoder |

The untagged v1.2 artifacts are corrected before the first `v1.2.0` freeze.
No published tag is moved. Once created, future incompatible changes require a
new version; this correction is not authority to rewrite a tagged release.

## Reproducible validation

```sh
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
python tools/validate_v1_2.py tests/fixtures/v1.2/valid/erasure.json
```

The fixture manifest includes normal and invalid cases for every new system event,
all erasure reasons and destruction methods, missing/misplaced detail fields,
legacy-format rejection, invalid enum values, empty evidence, recovery approval
bounds, and selected intra-event consistency failures. Regression tests reproduce
both P1 findings using the historical schema, verify canonical examples, internal
schema refs and all four root/canonical document mirror pairs.

**Scope:** these are syntax and selected local-consistency tests, not a full
protocol, legal, cryptographic or certification suite. Fixture hashes, signatures
and certificates are placeholders. Passing tests do not prove signatures, actual
key destruction, advance notice, distinct human approvers, 72-hour incident review,
range membership, chain continuity, anchor authenticity or timely anchoring.
Those require implementation-level and independent operational verification.

## Release gates and order

1. Merge the tested consistency correction, preserving all previous disclosures.
2. Re-run contract CI on the resulting main commit. Confirm no concurrent changes
   alter the validated files, and confirm no `v1.2.0` tag already exists.
3. Create `v1.2.0` at that corrected main commit. **Do not tag the old PR #1 merge.**
   Verify the tag resolves to the exact tested commit; never replace an existing tag.
4. Merge vap-spec PR #9 only after its B-5 explanation acknowledges the pre-GA
   changes and its publication digest is refreshed. VAP requirements are unchanged;
   the historical VCP RC1 mapping does not prove technical identity with this GA.
5. Merge vcp-site PR #78 only after the VAP merge and after its canonical schema is
   byte-identical to this tagged copy. Publish the legacy schema under its separate
   name. Remove unqualified regulatory-compliance claims on the specification page.
6. Verify deployed schema bytes and the public status pages. Until deployment is
   confirmed, distinguish source merged, tag created and website published.

The PR #1 HOLD review is a historical record. A follow-up resolution must identify
the correction and verification; it must not erase or misrepresent that review as
an independent approval.
