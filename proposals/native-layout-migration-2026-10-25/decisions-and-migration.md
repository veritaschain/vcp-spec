# Open decisions, concrete alternatives and migration boundaries

**UNADOPTED discussion draft; not effective. Independent third-party reproduction
has not been established.** No change to current VCP requirements, schema or
implementation is authorized by this document. The following recommendations
are proposals only; no decision is inferred from PR #14's tests or merge.

## Decision register

Every row has status **OPEN / UNADOPTED**. “Preferred” is the authoring
recommendation to review, not an approved rule or a scheduled release. The gates
are deliverables for a later, separately authorized change.

| Local topic | Preferred concrete candidate | Alternative and trade-off | Evidence/decision still needed |
| --- | --- | --- | --- |
| L-01 Native layout | Full native Header/Payload/PolicyIdentification in a new commitment; Header ns/ISO pair; protected Origin and policy bindings | Retain a synthetic Payload wrapper: smaller experimental scope, but does not resolve native meaning | Complete nested schema, presence/event matrix, identity namespaces and unknown-field handling; new IDs/domains |
| L-02 Numeric paths | Retain 63 logical paths and separate the other 11 as listed in the layout document | Collapse aliases into one universal wrapper: simpler shape but may erase distinct meaning/context | All 74 dispositions reviewed against requiredness/approvals; typed feature/control and open extension registry |
| L-03 Protected evidence | New event statement uses ActorID/ChainID; full anchor statement signed; receipts/observations detached | Treat a valid root signature as binding unsigned metadata: unacceptable because it does not supply the missing binding | Each protected preimage, COSE/PQC route, count/proof/target mapping and key authority independently specified |
| L-04 Policy roles | Distinct registration/numeric bindings with exact byte digests and configured authority | One typed policy document can serve both roles, but requires explicit role separation and immutable section semantics | Policy schema, issuer/version/revocation rules, path grammar and nested dependencies; no mutable-URI default |
| U-01 Exact quantity units | Fixed unit per full path; exact comparison conversions; any new wire value is separate derived evidence | Per-value alternate units increase ambiguity and change the signed contract; not selected implicitly | Capacity survey, allowed dimensional transformations and complete exact arithmetic vectors |
| U-02 Lexemes and rounding | Preserve accepted decimal strings during verification; no implicit rounding | Unique normalized decimal emission could aid interop, but changes preimages and requires a new rule | Explicit output spelling for newly derived decimals, scale/overflow/rounding-or-rejection rules and loss declaration |
| T-01 Time pair | Required Header ns/ISO pair, nine UTC fractional digits, 0…2^63−1 ns, bound unix_no_leap policy | Broader date range, offsets, variable precision or numeric remainder formats change complexity/capacity | All timestamp paths, range boundaries, original precision and source-format pair semantics |
| T-02 Other time bases | Preserve and mark unsupported until an exact, identified mapping exists | Add leap/smear/TAI/GPS conversion with pinned tables/functions | Mapping authority, version, provenance, ambiguity/inversion and actual vectors; no clamping |
| M-01 Preservation/derivation | Read-only legacy verification plus explicitly marked new derived records and detached migration attestation | Retain/archive only is valid where derivation cannot be justified | Derivation format/authority, source evidence, target mapping and absence of cycles |
| M-02 Chains, anchors and deployment | New target format/context/chain identity; preserve old roots, receipts and results; separate routing | In-place type/byte rewrite invalidates existing commitments and is not selected | Approval of target version, chain restart/continuation, actor identity and rollback/consumer compatibility |
| M-03 Authorization signatures | Preserve and verify original approval objects; reissue only through an authorized new approval process | Treat converter signature as an original approver's signature: unacceptable | Every inner approval preimage, actor/role/time policy and source-to-target relation |
| G-01 Adoption/reproduction | Record document review, normative decision, implementation validation and external reproduction separately | Inferring adoption or independence from merge/CI has no supporting evidence | VCP governance decision, assigned identifiers, new reviewed implementation and separately operated reproduction |

No row grants a license to extend current rules or relax tests to make a source
convertible. The current v1.x compatibility promise needs an explicit release
decision: this work does not assume a patch/minor revision is compatible.

## M-01 — Preserve, verify and derive as separate operations

### 1. Capture the original artifact set

Retain exact raw event files, policy bytes, signature envelopes, roots, proofs,
receipts, version/source information and historical reports. Record raw-file
hashes separately from protocol EventHash: those hashes cover different bytes
and must not share a misleading label. An ordered source manifest describes
which objects were actually received, missing or unavailable. It does not prove
all real-world events were captured. Never replace an old file, ZIP, release,
tag or CI record with a newly generated version under the same identity.

### 2. Verify the identified original format unchanged

Select the original interpretation from its recorded contract/version and
configured acceptance policy, then authenticate its protected context. A header
version can select a parser provisionally; it is not trusted merely because it
is present. Do not try encodings until one signature passes. Record:

- exact bytes and scheme used for the original cryptographic check;
- which metadata, units, count and policy that signature actually covered;
- original numeric/ISO consistency under that format;
- key authority, proof/receipt/target/time checks and any unavailable evidence.

If the historical algorithm/format is ambiguous, label the interpretation
unresolved, retaining any narrowly reproducible checks. Do not announce either
full validity or universal invalidity. In particular, a legacy root-only
signature cannot become proof of a batch count, policy or timestamp it did not
cover, even if the root's signature verifies correctly.

### 3. Determine derivation eligibility before changing values

Require the source's exact value/type, its evidenced unit/time basis, the
applicable field/context mapping, target capacity and a conversion rule with
authority. Keep all unanswered conditions visible. Examples:

| Source condition | Proposed disposition |
| --- | --- |
| Exact original integer token and known ns basis | Eligible for a separately described number-to-string derivation, subject to target range and all other gates |
| Only an already-rounded float is available | Original exact integer is unknown; no reconstructed “original” or qualified exact conversion |
| Timestamp magnitude looks like seconds or us, but unit is undocumented | No magnitude/digit-count inference; retain as unresolved |
| Ns and ISO disagree under an identified source basis/pair rule | Original consistency FAIL; do not select a winner silently. A later correction is a new attributed claim |
| Decimal value is outside target capacity or needs unspecified rounding | No target candidate value under this exact-conversion option; preserve source |
| Known instant is before epoch zero or above the proposed TIME_NS maximum | Unsupported by this target candidate even if its source ISO spelling can be normalized; no epoch shift, clipping or unit relabeling |
| Equal ratio text uses trailing/leading zeros | Preserve accepted source lexeme for an unchanged quantity; no verifier normalization |
| Missing policy bytes or unconfigured authority | Do not invent approved policy. Binding/interpretation/authority remain unassessed as appropriate |
| Approval timestamp/object is signed and would change | Block reuse as a valid new approval; require separate authorized reissuance or retain the original evidence only |

If the source time basis or pair interpretation is unresolved, its equality
check remains UNASSESSED rather than applying the proposed future rule to the
past. There is no automatic migration merely because a checker can serialize the
source. Format support, exact conversion, cryptographic integrity and authority
are separate conditions. If a known failure exists, an unsupported/unknown check
does not erase it. A source failure may be described in a new analysis/attestation,
but cannot be promoted into a verified source by conversion.

### 4. Create new evidence with an acyclic derivation link, if later authorized

Prefer a new, detached **DerivationPlan** and **MigrationAttestation**, with
their own identifiers and signed-byte definitions to be reviewed separately.
The following is a concrete semantic design, not an implemented schema:

| Object | Proposed content and binding |
| --- | --- |
| DerivationPlan (fixed before output) | Plan ID/version; exact source-manifest digest and stable source-entry IDs; source format IDs; selected target contract/policy bindings; conversion-rule digest; allocated target record IDs; per-field source/target path, type, unit and rule. No target artifact digest or attestation digest, avoiding a cycle |
| New target EventCommitment.Origin | `Kind = derived`, DerivationPlanDigest and SourceEntryID, all inside EventHash. A different `capture` variant is reserved for an attributed new capture claim, not for relabeling a conversion |
| MigrationAttestation (after output) | Plan digest; source and target artifact manifests/digests; old/new event-hash identifiers where available; exact before/after lexemes/units, comparison outcomes and source limitations; converter identity/key, claimed creation time, support/intervention and authority references |
| Attestation signature | Separate protected domain and full attestation message, by the converter/attestor; no claim to reproduce an original producer/approver signature |

The source manifest and plan commit exact retained bytes, not URLs alone. Prefer
a one-source-event to one-new-event mapping for the first derivation option,
with explicit source-entry IDs; no merging, deduplication or omission is implied.
An unsupported source entry stays explicitly unconverted. Any partial target
batch has its own count/list and cannot be labeled a complete source migration.

The target's Origin binds the plan **before** hashing/signing; the detached
attestation binds resulting target artifacts **after** signing. It is excluded
from those target preimages. Thus stripping/changing Origin changes EventHash
under this proposed contract; it cannot be achieved by merely relabeling a
report. An authorized signer can still issue a false claim, so Origin itself
does not establish observation truth or legitimate converter authority.

The target has new record IDs and its own timestamp/signature history. Preserve
the original event's described occurrence time when supported; do not replace it
with conversion time. Keep conversion/attestation creation time separately as
a new claimed time. No observation, signature or anchor is backdated.

Final member names, serialization, domain literals, plan/attestation signatures,
authority and presence rules are **OPEN**; no existing verifier validates them.
This proposal does not allocate a migration event type or add a VCP module.

### 5. Preserve inner authorization and all old commitments

Approval signatures already inside Payload remain content covered by the new
outer EventHash, but their own verification continues to use their original
specified preimages. Changing an approval timestamp's type, unit, identifier or
time spelling may invalidate that inner signature. A new outer event/anchor
signature does not repair it or assert that the original approver approved the
new representation. Where an approved mapping cannot retain valid inner
evidence, keep it as an explicitly original artifact or obtain a new approval
through the proper actor/process; otherwise do not emit a qualified native
replacement. No new approval is obtained or requested by this document.

Changing one committed event can change its EventHash, its leaf/root, subsequent
linked PreviousEventHash values, signature statements, proofs and external
commitments. Allocate a new target context/ChainID and authorized chain start
for a translated sequence. A separately authenticated relation can refer to the
old chain endpoint, but does not pretend a new hash is a byte-identical
continuation. Do not sort, deduplicate or resequence source entries to make
verification pass. Chain restart authority and sequence-origin rules remain
separate requirements.

Old proofs and receipts stay attached to their old root/commitment. New hashes
require newly generated proofs/signatures and, if needed, a new external receipt;
the old receipt cannot establish the new record's earlier existence. Unchanged
semantic values do not imply reused hashes/signatures, since the proposed new
layout and domains themselves alter preimages.

## M-02 — Rollout and result model

Propose separate producer/consumer format routing keyed by explicit protected
contract/schema identifiers, not an endpoint that tries number/string or unit
variants until a check passes. A consumer that cannot handle the selected new
format reports unsupported; it does not fall back to weaker legacy validation
and call the new data accepted. Keep legacy verification available for retained
originals, with each result labeled by its actual contract and limitations.

Dual publication, if later approved, creates two distinctly identified artifacts
plus their derivation relation. Do not overwrite one database field or URL with
the other. Numeric comparisons and indexes use exact quantities, not lexicographic
sorting of strings. Binary formats and external COSE/CBOR signatures need their
own mappings; a JSON example is not such a mapping. API/storage migration and
deployment are not part of this PR.

For rollback, stop producing/accepting the new format according to the separately
approved operating plan; retain already issued records and append any revocation
or supersession with explicit authority. Do not delete a bad run, move a fixed
tag or silently replace a ZIP to restore a successful result. Operational rollback
is not retroactive cryptographic reversal.

Reports should retain separate fields for source-format support, source byte
integrity, source semantic/policy validity, conversion eligibility/exactness,
target-format checks, target signatures/authority, receipt/time evidence and
derivation binding. No single “migration successful” flag can replace them.
Across required checks, known FAIL takes precedence over UNASSESSED, with all
individual unknowns retained. No output promotes a conversion or internal CI
run to native conformance, official adoption or independent reproduction.

The PR #14 review also motivates checking a report's **complete expected byte
trace and reference relationships**, not merely a subset of fields that happens
to remain. This is a requirement to consider for future tooling, not a new
report verifier supplied by these documents. A consistent report still does
not authenticate its operator or environment.

## Evidence required before these proposals could become a native contract

1. A recorded VCP decision on target version/compatibility, IDs/domains and all
   open rows above; no borrowed VAP approval or implicit decision from merge.
2. A complete native schema and path/context/presence inventory covering all
   admitted fields, signatures and extensions, with both policy roles and the
   proposed Origin/derivation objects explicitly resolved. The 74 known numeric
   entries do not close every open module or nonnumeric field.
3. Fresh vectors for the **new** Header/layout and policy bindings, each protected
   field, all actual time/numeric paths and conversions, edge capacities,
   conflicting aliases, missing units and identities, partial batches, inner
   approvals and every admitted receipt/signature encoding. Neither PR #12's
   scalar tests nor PR #14's one-event cases substitute for these.
4. Multi-event source/target chain and root/proof migration, a mutation of one
   middle event, unsupported/partial conversion, unknown original format,
   lossy-source rejection, failed inner approvals, stripped derivation context
   and retained old receipt limitations. Preserve original and new outputs.
5. Independent implementations of the selected bytes and interpretation, plus
   separately operated external reproduction with environment ownership,
   assistance, failures/deviations and relationships reported. Execution consent
   and publication permissions stay separate; no such external run is asserted.

These are proposed acceptance gates, not completed tests or authorization to
perform them now. K3's versions, inputs, expectations and results remain fixed;
any future impact study would be a separate recorded exercise. This PR sends no
K3 notification, changes no evaluation criterion and invalidates no prior result.
