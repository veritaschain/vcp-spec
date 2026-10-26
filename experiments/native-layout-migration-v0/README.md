# Native-layout and migration subset experiment

**UNADOPTED, not effective. Independent third-party reproduction is NOT
established. This is a closed synthetic subset, NOT a native VCP v1.2 verifier,
replacement schema, complete migration tool or approved future protocol.**

This follows [PR #15](https://github.com/veritaschain/vcp-spec/pull/15), fixed at
`517d407f507fd6401bc6edb4979b5a6673122d40`. Its [layout candidate](../../proposals/native-layout-migration-2026-10-25/field-layout-candidate.md)
and [open decisions](../../proposals/native-layout-migration-2026-10-25/decisions-and-migration.md)
remain unadopted. This experiment selects **local test options**, not resolutions
of those decisions. Formal version, registry, normative adoption and production
schema identifiers remain unassigned. The `urn:vcp-research:...` identifiers and
`RESEARCH_LAYOUT_ONLY` event type belong only to this experiment; they do not
allocate a VCP event type or replace native UUID/identity rules.

Only this new directory and its new CI workflow are added. Current specifications,
GA/RC schemas, existing implementations/experiments, signed records, distributions,
release tags, DOC-SYNC and K3 are unchanged. All 204 current baseline files at `943d513fec3c0eaa7eb683120e2d82d5eb748285` are fingerprinted
in [sources.json](sources.json); execution checks those exact bytes. Use a checkout
of this experiment's reviewed commit, not a subsequently edited baseline.

## Run a fresh internal reproduction

From the repository root, using Python 3.12 or 3.14:

```sh
python3 -m venv /tmp/vcp-layout-research-venv
/tmp/vcp-layout-research-venv/bin/python -m pip install -r experiments/native-layout-migration-v0/requirements.txt
/tmp/vcp-layout-research-venv/bin/python experiments/native-layout-migration-v0/run.py --output /tmp/vcp-layout-report.json
/tmp/vcp-layout-research-venv/bin/python experiments/native-layout-migration-v0/run.py --verify-report /tmp/vcp-layout-report.json
/tmp/vcp-layout-research-venv/bin/python experiments/native-layout-migration-v0/report_controls.py /tmp/vcp-layout-report.json
```

Choose a new output filename on each run: the runner refuses to overwrite an
existing file. No Docker, root, network endpoint, real API call or production key
is used by the checker. Package installation needs its normal package source.
Do not run scripts supplied by an evaluator as part of accepting a report.

The suite returns zero only when **all authored per-axis expectations**, all
14 unit outcomes and all 39 regression controls match, without skipped or expected
failures. Negative and unsupported cases are supposed to return FAIL/UNASSESSED;
“suite succeeded” does not mean all evidence passed. `--verify-report` performs
fresh execution and strict typed comparison of the **entire report**, including
input fingerprints, per-case verdicts, environment/dependencies and summary.
It requires the same recorded runtime/platform/dependencies; a different
environment should produce its own fresh report. Matching reports do not
authenticate the operator or host. Eight report mutations are checked separately.

Inspect one synthetic example without the suite:

```sh
/tmp/vcp-layout-research-venv/bin/python experiments/native-layout-migration-v0/checker.py experiments/native-layout-migration-v0/data/example-bundle.json --context experiments/native-layout-migration-v0/data/example-context.json
```

The standalone checker exits 0 for a covered-subset PASS, 1 for FAIL and 2 for
UNASSESSED. Every output keeps `native_conformance: UNASSESSED` and
`independent_reproduction: not_established`, including a covered PASS.
The context is a **separately configured input**, not authority obtained from the
bundle. Fixture keys/seeds are public test material, never production identities.
`fixtures.py` regenerates only the new synthetic fixtures. The standalone checker
does not import its signing keys. The suite's regression controls do import the
public fixture keys to construct deliberately re-signed adversarial examples;
those keys never supply a verdict or production authority.

## Selected candidate schema and coverage

[candidate.schema.json](candidate.schema.json) is a closed JSON Schema 2020-12
research bundle with local `$defs` only; `schema_builder.py` reproduces its exact
structure. JSON Schema establishes structure, not signature validity, exact unit
conversion or time equality. The Python checker supplies those separate checks.
[JSON Schema Core](https://json-schema.org/draft/2020-12/json-schema-core)
describes the schema vocabulary; no remote schema is retrieved during checking.

The retained Header names are EventID, ActorID, ChainID, SequenceNum, EventType,
PolicyID, TimestampInt and TimestampISO. Header time is the exact proposed ns/string
plus nine-digit UTC pair. Quantities remain at the selected full paths:

| Inventory entries | Selected exercise |
| --- | --- |
| N001/N002/N003 | Header ISO/ns/sequence, exact bounds and strictly increasing sequence; equal timestamps allowed |
| N012 | Flat `Payload.VCP-GOV.ConfidenceScore`; [0,1] and original decimal lexeme |
| N031 | `Payload.VCP-ANCHOR.FailoverDetails.TriggerCondition.TotalDowntimeSec`; exact conversion from **synthetic** source milliseconds |
| N042 | `Payload.VCP-XREF.SharedEventKey.ToleranceMs`; stored milliseconds retained |
| N058 | `Payload.VCP-GOV.PerformanceMetadata.LatencyImpact`; microseconds and lexeme retained |
| N017/N037 | Detached index/count/proof and complete ordered synthetic batch |
| N036 (different semantics) | New RecordedAtNs claimed creation-time scalar; NOT verification/mapping of legacy AnchorRecord.Timestamp |

[data/coverage.json](data/coverage.json) accounts for all 74 inventory entries:
**9 exercised in this subset, 1 different-semantics time scalar, 64 UNASSESSED**.
These are inventory entries, not counts of fully supported native fields/modules.
The schema intentionally does not admit arbitrary VCP modules, clock claims,
SCITT profiles, nested approval objects or the other numeric paths. Such a target
fails this closed research layout while its native validity remains unassessed.
The selected mixed-module fixture is not an approved event/module presence matrix.

PolicyIdentification is explicitly null or the selected small PolicyID/Version
object. This is not the GA PolicyIdentification schema: no tier certification or
registration authority is inferred. Two distinct policy documents are retained
as exact bytes; their bindings cover PolicyID, PolicyVersion and SHA-256. Each
role's binding must agree throughout the batch; registration and numeric roles
need not have the same identifier. Header/PolicyIdentification match the
registration role. The context selects exact policy digests, and the checker also
requires the **implemented policy semantics**: allowlisting a new digest cannot
add a new time basis or unit interpretation. No mutable policy URI is followed.

## Bytes, actual signatures and aggregation

Every domain prefix is UTF-8 `VCP RESEARCH native-layout-migration v0 `, followed
by the role below and one zero byte. These local prefixes are not proposed as
formal registered values. All `sha256:` values have 64 lower-case hex digits.

| Check | Exact research input |
| --- | --- |
| EventHash | SHA-256(`event` domain + JCS(complete selected EventCommitment)) |
| Event signature | Ed25519 over `event-signature` domain + JCS(Statement); statement binds recomputed EventHash and EventID/ActorID/ChainID plus ContractID, algorithm and KeyID |
| Anchor signature | Ed25519 over `anchor-signature` domain + JCS(complete Anchor.Statement), including count/root/endpoints, both policy bindings, actor/chain, tree scheme, time and synthetic target |
| Original simulated-source signature | Ed25519 over `source` domain + exact original JSON bytes, including whitespace; **not** VCP's existing signing format |
| DerivationPlanDigest | SHA-256(`plan` domain + JCS(DerivationPlan)) |
| Migration attestation signature | Ed25519 over `attestation` domain + JCS(complete attestation Statement) |
| Policy, source manifest and target artifact digests | Unprefixed SHA-256 of exact policy bytes, JCS(SourceManifest), or JCS({Events, Anchor, InclusionEvidence}), respectively |

JCS processing uses [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html).
The synthetic source's large JSON integer is **never** passed through JCS or a
float to preserve it: raw bytes are retained, and strict JSON decoding preserves
the exact integer token. The target commitments use strings for quantities.
Duplicate JSON keys and non-JSON constants are rejected. No `signature_valid`
input or unsigned success flag supplies a verdict.

Merkle leaves are SHA-256(0x00 + decoded EventHash); internal nodes use SHA-256
(0x01 + left + right), with recursive largest-power-of-two splitting as in
[RFC 9162 §2.1.1](https://www.rfc-editor.org/rfc/rfc9162.html#section-2.1.1).
Three-event fixtures exercise a non-power-of-two tree; odd leaves are not copied.
With a **complete supplied list**, the checker recomputes count/root/endpoints,
unique IDs, order, predecessor links and each expected path/index. It does not
provide a partial-batch acceptance mode or establish delivery of all real activity.
Own event signatures remain outside EventHash/root. The separate target-artifact
attestation binds the supplied event signatures, anchor and proofs as well.

Reports retain ten axes: layout, source retention, source authentication, source
interpretation, policy binding, numeric/time checks, cryptographic integrity,
batch binding, inclusion evidence and derivation binding. A raw valid signature
can coexist with semantic FAIL or UNASSESSED. Known FAIL dominates UNASSESSED;
individual unknown axes remain visible. Proof PASS means covered path arithmetic,
not production anchor trust. External target delivery/time and actual signer
identity, revocation and authority always remain unassessed.

## Exact conversions and retained migration evidence

The source adapter is explicitly `urn:vcp-research:raw-source:2026-10-25:v0`.
Its DurationMs is a **new synthetic source field**, not a renamed native field.
Sources bind their units/basis inside the original signed bytes. Supported source
integers, offsets, quantities and fields are intentionally narrow; no magnitude
heuristics, extra-field dropping, binary-float recovery or inner-approval mapping
is attempted. Unmapped source members/approvals/units/clock bases stay unassessed.

The selected conversion is exact whole milliseconds to whole seconds. Nonintegral
results are unsupported, not rounded. ToleranceMs and decimal confidence/latency
strings remain lexically unchanged. Additional unit vectors cover seconds/ms/us
to an integer-ns destination, overflow, boolean/negative inputs and unresolved
percent-to-ratio conversion. These are explicit arithmetic requests; they do not
add alternate wire units. Range checks use exact arithmetic. ISO spelling/offset
conversion cannot make pre-epoch or above-capacity instants eligible. `-00:00`,
leap seconds, smear and other unmapped bases remain unassessed. Clock accuracy,
freshness, physical chronology and external creation-time proof are not measured.

The evidence flow is:

1. Supply original event bytes/signatures and separate retained copies, plus
   opaque original proof/receipt bytes and their retained copies. A source manifest
   lists exact raw/signature digests and the ordered inventory. Its digest must
   match the **separately supplied receipt-time context pin**. This detects even
   a coherent replacement that also rewrites/re-signs the input manifest.
2. Verify the original simulated signature and interpret only the identified
   source adapter. This does not revalidate native VCP signatures or an old receipt.
3. Fix a DerivationPlan before target hashing. It binds the source manifest,
   target context/policies, explicit conversion-rule ID and one-to-one entry/ID
   mapping. It contains no target hash or final attestation hash, avoiding a cycle.
4. Each new EventCommitment includes protected `Origin.Kind=derived`, plan digest
   and source-entry ID. IDs cannot reuse any original EventID. Target ChainID is
   separate; all source entries/order and occurrence instants remain accounted for.
   The plan rule performs no merges, omission, resequencing or decimal normalization.
5. After signing the new artifacts, a detached signed attestation binds plan,
   source manifest and the full target artifact digest. Converter signatures do
   not become original approver signatures or proof of independent operation.

This candidate uses one hard-coded conversion-rule ID, not PR #15's eventual
general per-field rule registry. The attestation binds the full input/output
artifacts; it does **not** sign the checker's verdicts or provide the final
per-field transformation/authority/limitation record proposed in that document.
Exact before/after values can be inspected in the retained artifacts, and checks
are recomputed. The general attestation schema and authorization process remain
open; a digest-binding PASS does not assert they have been implemented.

This is a **read-only check of supplied evidence copies**, not filesystem storage
or a live converter. It does not prove pre-receipt completeness, protect a host
administrator from rewriting a context pin, or verify the old opaque receipt's
meaning. Changing either retained copy or omitting its inventory fails. Changing
old roots/receipts is not necessary to derive a new record. Original signed data
outside these generated fixtures is never opened for mutation.

## Open decisions and limits

| PR #15 topic | Still unresolved after this experiment |
| --- | --- |
| L-01/L-02 | Complete native schema, all 74 numeric paths, identifiers/UUIDs, module/event requiredness and extensions |
| L-03/L-04 | COSE/PQC and inner approval preimages, production policy issuance/revocation, permission and trust |
| U-01/U-02 | All financial/model units and capacities; approved output spelling/rounding for new derived decimals |
| T-01/T-02 | Other time bases, leap/smear mapping provenance, real precision/synchronization/freshness |
| M-01/M-02/M-03 | Actual legacy formats and customer data, partial migration rules, original approval reissuance, operating rollback |
| G-01 | Formal adoption/version allocation, implementation review and independently operated reproduction |

A candidate-schema PASS is not a claim that these gates are closed. No current
normative requirement or schema is changed, and none of the new failures makes an
existing native record invalid. Known unsupported features are not silently filled
with defaults. Independent reproduction remains unestablished even after CI passes.

The case matrix contains **62 bundle cases** (6 PASS, 43 FAIL, 13 UNASSESSED) and
**14 unit cases** (5 PASS, 4 FAIL, 5 UNASSESSED), with authored per-axis expectations.
These are candidate outcomes, not all-positive evidence. The 39 additional
regressions and eight report mutation controls are separate measures, not a count
of independent validations. Actual run records and runtime limitations are in
[REVIEW.md](REVIEW.md). The new CI checks Python 3.12/3.14; prior experiment and
contract workflows remain untouched. CI artifacts have ordinary finite retention;
the local recorded runs in this directory are retained in Git, not represented as
external evaluator reports or a new fixed research release.

Final-review repairs and new run records are in [FINAL-REVIEW.md](FINAL-REVIEW.md).
The earlier 55-case reports remain historical records for their stated commit;
verify them at that commit, not against this revised implementation. The current
baseline incorporates separately merged PRs #13, #17 and #18 without reverting
any of their changes. No existing baseline file is modified by this PR.
