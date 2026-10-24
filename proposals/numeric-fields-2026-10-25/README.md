# VCP numeric-field inventory and migration candidate

**Status: UNADOPTED discussion draft.** No formal proposal number or target
release has been assigned. Independent third-party reproduction has **not been
established**. Publication or merge of these documents is not normative adoption,
implementation validation, certification, or a change to the current v1.2 rules.

This inventory proposes exact units, bounds and representations for review. It
does not modify the specification, schema, adopted VSO-SPEC-CHANGE-001, existing
implementations, signed data, fixed distributions, tags, K3, or the earlier
[byte-contract candidate v0](../integrity-2026-10-24/byte-contract-candidate-v0/README.md).
In particular, this inventory does not make that closed synthetic format a native
VCP event/AnchorRecord verifier.

## 1. Sources and coverage

The baseline is `e984d85311f57338065570d7679ddff92718001b`. Full SHA-256 digests
and immutable source links are in [sources.json](sources.json). Sources are:

- The English v1.2 body, `spec/v1.2/VCP-Specification-v1_2_en.md`.
- The GA schema, `spec/v1.2/vcp-event-v1.2.json`, not the RC legacy schema.
- The adopted annex, `spec/v1.2/VSO-SPEC-CHANGE-001.md`.
- English v1.0 §§4–5, explicitly inherited by v1.2 §§4 and 5.1–5.4. Its header
  examples and Appendix C are also consulted for legacy-encoding ambiguity.

The root English body and annex copies have the same hashes as their `spec/v1.2`
counterparts at this baseline. Translation parity, SBE/FlatBuffers schemas,
independent SCITT service profiles, deployed databases and proprietary extension
schemas are not audited here. V1.2's stated precedence of its annex over the
summary is retained; proposed bounds below do not override either source.

[The field inventory](inventory.md) has **74 review entries**, including legacy
aliases, calendar durations, external receipt examples and numeric enum codes.
They are not 74 distinct required numeric properties of every event:

- **34 schema definition sites expand to 35 instance paths**: 24 integer sites,
  seven DecimalString references, one number-or-string confidence field and two
  date-time strings. The shared ApprovalTimestamp definition occurs in both
  ERASURE and emergency CHECKPOINT paths.
- **39 further entries** cover prose-only/inherited fields and explicitly
  separated configuration, external-receipt and legacy contexts.
- Schema snapshots preserve the actual constraints, conditional context and
  whether each leaf is required *within its containing object*. Required parents,
  event type and authorization route still matter; this is not a replacement for
  schema validation.

This is coverage of the named fields in these sources, **not closure of all
possible numeric values**. VCP-RISK, VCP-XREF, several module members,
DecisionFactors, VerificationDepth and arbitrary `VCP-*` module contents are open
or weakly typed. `SYS_CHECKPOINT.RecoveryAction`, conversely, is closed and does
not admit the general-recovery `RecoveredEvents` field. An extension registry and
native-format mapping remain adoption blockers. The audit script checks schema
coverage mechanically; prose coverage and semantic proposals are manual review.

## 2. Findings that affect a numeric migration

1. **Bounds are not implemented by type names.** Header.TimestampInt describes
   a 64-bit value, but the schema has minimum 0 and no maximum. No integer property
   in the GA schema has a maximum. The policy EffectiveDate/ExpirationDate
   properties have neither a minimum nor maximum. A candidate range must not be
   described as a bound already enforced by today's schema.
2. **Units need full paths.** Annex §3.4 assigns epoch nanoseconds to timestamps
   in the structured encoding, except ISO/RFC 3339 fields; `*Sec` durations and
   MaxOutageDuration are seconds. ToleranceMs is milliseconds. MaxSkipDuration
   lacks an explicit wire unit. A FailoverDeadline timestamp and a relative
   failover deadline in §7.3.2 are different quantities. AnchorTarget's int64
   LastHealthCheck and the configuration example's ISO LastHealthCheck are also
   different encodings. External AnchorRecord time units are not restated locally;
   the candidate makes them explicit without claiming all legacy records used ns.
3. **Examples are not reliable conversion rules.** In body §6.3.2, integer
   `1735128000123456789` represents `2024-12-25T12:00:00.123456789Z` under the stated
   ns convention, while the paired ISO example says 2025. Body §3.2.1 and older
   annex diagrams also use shorthand Timestamp or shorter integers. Do not infer
   seconds/us/ns by digit count or multiply an old value until it matches a date.
   These observations are recorded here; the source examples are not changed.
4. **Financial strings are already strings.** DecimalString permits signed
   decimal text, including leading/trailing zeros, with no length, scale or value
   bound. The schema does not supply instrument units, tick size, fee currency or
   slippage sign convention. These are policy questions, not a reason to round or
   reinterpret prices as integers.
5. **Confidence and model data differ.** The flat ConfidenceScore permits either
   number or string, without enforcing its documented [0,1] range. The inherited
   nested DecisionFactors.ConfidenceScore is a different path. Feature values can
   be categorical; weights/contributions need not be probabilities. Exposure
   utilization may exceed 1 when a limit is breached.
6. **A representation change changes evidence.** Replacing `1` with `"1"` changes
   JCS bytes. A successful legacy signature does not authenticate newly introduced
   units, new bounds or legacy unsigned anchor metadata. No previous claim becomes
   stronger through a conversion performed by the verifier.

## 3. Concrete candidate scalar contracts

All rules in this section are **proposed** for a separately identified future
format. They are not new acceptance criteria for existing v1.2 data. Candidate
class and unit are assigned to each path in inventory.json/inventory.md.

### 3.1 Exact integer quantities

For the following classes, JSON representation is a **string** matching the
entire ASCII grammar `0|[1-9][0-9]*`, then checked with exact integer arithmetic.
No signs, leading zeros, whitespace, exponent, decimal point, boolean or JSON
number substitutes. A lexical match alone does not establish an in-range value.

| Candidate class | Unit | Inclusive range and extra check |
|---|---|---|
| TIME_NS | Unix-epoch ns | 0–9223372036854775807 |
| DURATION_NS63 | Elapsed ns | 0–9223372036854775807; chosen explicitly for MaxSkipDuration |
| SECONDS63 | Whole seconds | 0–9223372036854775807; keep existing seconds units |
| MILLISECONDS31 | Whole milliseconds | 0–2147483647 |
| UINT63 / POS63 | Count or sequence ordinal | 0 / 1 through 9223372036854775807 |
| UINT31 / POS31 | Count | 0 / 1 through 2147483647 |
| INDEX31 | Zero-based index | 0–2147483646 **and** less than the authenticated/validated associated count |

These are reviewable design choices: positive/nonnegative signed-32-bit bounds
retain the prose int32 capacity; signed-64-bit bounds align with the earlier
candidate's timestamp cap and give schema-only counters a finite exact range.
They are neither JCS limits nor operational quotas. A 2^64−1 alternative would
need a 20-digit parser, new vectors and an explicit capacity decision; it is not
silently supported by the prior 19-digit candidate. Counts/sequence capacity and
the nonnegative time domain remain open decisions for adoption.

Use arbitrary-precision intermediates (or explicitly checked overflow) for
duration multiplication, time differences and deadline addition, then validate
the destination range. For example, ToleranceMs × 1,000,000 is a **comparison**
conversion, not a rewrite of stored milliseconds. Seconds stay seconds. No
saturation, modulo wrap, rounding or replacement with zero is permitted in the
candidate. Timestamp 0 is the epoch, not a missing/unknown sentinel.

SequenceNum is proposed to increase strictly within (ActorID, ChainID), with no
wrap; origin and continuation after recovery require a separate chain policy.
This proposal does not require a gap-free sequence or make a jump proof of
unobserved real-world events. Count zero is permitted only where its class allows
it; AnchorRecord.EventCount and affected-event counts are positive. Proof indices
require an authenticated count. Multi-actor PartyIndex requires a validated
TotalParties; when the currently optional total is absent, that bound is
unassessed rather than assumed satisfied.

### 3.2 ISO pair and leap-second proposal

UTC_NS is proposed as a narrower RFC 3339 subset:
`YYYY-MM-DDTHH:mm:ss.nnnnnnnnnZ`, uppercase T/Z, exactly nine fractional digits,
valid Gregorian date, hour 00–23, minute/second 00–59. It must map exactly into
TIME_NS: `1970-01-01T00:00:00.000000000Z` through
`2262-04-11T23:47:16.854775807Z`. Convert with integer calendar arithmetic,
not floating-point seconds or a millisecond-only date object.

Header.TimestampISO **and** TimestampInt remain required together in this
candidate native mapping, and must denote exactly the same instant. ScheduledTime
and the configuration date string use the same lexical subset when present,
without inventing an extra TimestampInt field. Offsets, variable fractional width
and lower-case spellings may be valid RFC 3339 but are not this proposed subset.
The current GA schema is not changed to reject them.

The candidate uses a Unix-time convention that does not count leap seconds. It
does not encode `:60`, a negative leap-second adjustment, or a clock smear as
equivalent to an ordinary UTC reading. Such evidence is **unsupported pending an
explicit mapping**, retained unchanged, and not rounded to `:59` or the next
minute. This is a proposed limitation, not a claim that RFC 3339 prohibits leap
seconds. Instrument resolution and clock accuracy remain distinct: padding nine
fractional digits does not establish nanosecond observation accuracy. Existing
TimestampPrecision and clock/tier policies are not redefined here.

[RFC 3339 §§5.6–5.7](https://www.rfc-editor.org/rfc/rfc3339.html#section-5.6)
defines a broader date-time syntax, including leap-second considerations.

### 3.3 Decimal quantities and policy-dependent fields

DEC_SIGNED keeps the existing full-match ASCII decimal grammar
`-?[0-9]+(\.[0-9]+)?`. The proposed resource bound is at most **20 integer digits
and 18 fractional digits** (38 digits total, excluding sign/point). The exact
numeric range is therefore ±99999999999999999999.999999999999999999.
DEC_NONNEG uses the same grammar/size limit but numeric value must be >=0.
RATIO01 adds the exact inclusive [0,1] check. These finite limits are candidate
choices for interoperability/resource control, not existing schema limits;
instrument/model owners must confirm capacity before adoption.

Use scaled integers or exact decimal arithmetic. The candidate preserves each
accepted string's **exact lexical bytes**, including leading/trailing zeros and
signed zero. Thus `"1"`, `"1.0"` and `"01.00"` may compare equal arithmetically
but remain distinct signed strings. Do not trim, rescale or normalize them during
verification. This deliberately does not invent a unique decimal spelling beyond
JCS's treatment of strings. A future unique-spelling rule would be another
explicitly versioned change.

The bounds are only an outer envelope. The following bindings are required before
claiming semantic validity in a future native mapping:

- Price/ExecutionPrice: quote currency per identified instrument unit, tick and
  scale. Negative prices remain representable where instrument policy permits.
- Quantity/ExecutedQty/RemainingQty: common instrument units and lot conversion;
  nonnegative magnitude is the candidate choice, with side carried separately.
- Commission: identified fee currency, which need not equal quote currency;
  negative rebates permitted only under a stated policy.
- Slippage: candidate signed execution price minus identified reference price in
  price units. Bps, side-adjusted cost and other legacy conventions are not aliases.
- Risk sizes/amounts: instrument or currency basis, valuation/window, VaR horizon
  and confidence level. Utilization may exceed 1; zero-denominator utilization is
  undefined, not coerced to 0. ThrottleRate stays orders/s and may be fractional.
- Model Weight/Contribution: signed values in explicitly named feature/model
  output units; no sum-to-one assumption. Feature Value and TriggerValue require
  a per-feature/control type; categorical strings are not parsed as decimals.
- SamplingRate/ConfidenceScore: unitless [0,1], not percent points. LatencyImpact
  remains microseconds and can contain fractional microseconds.

The policy bytes supplying units/scale/bounds must be bound to the new signed
contract and identified by version/digest; a mutable URI or an unsigned label
alone does not establish the interpretation. The policy schema/registry and
model-specific bounds are **unresolved**, so this inventory does not close those
fields' conformance gates. No unit values are guessed from a currency symbol or
field name. Out-of-envelope or unrecognized data remains preserved legacy
evidence, not a rounded candidate value.

### 3.4 Explicit non-conversions and presence rules

Calendar RetentionPeriod stays an ISO calendar-duration string; years/months
cannot become fixed seconds without a calendar/start/policy. Its supported
subset/range is unresolved here. This proposal changes no legal retention rule.
SCITTReceipt tree_size/leaf_index stay under the selected external service's
COSE/CBOR and signed-byte contract; do not run VCP decimal-string conversion on
external receipts. An external tree need not equal a VCP batch.

Numeric EventType codes, version strings, algorithm names, UUIDs, tags, hashes,
signatures and enum values are identifiers, not quantities. Legacy numeric event
codes need their own format-specific mapping, not generic number-to-string
conversion. Unknown extensions cannot be declared conformant simply because all
their numbers were converted to strings.

Requiredness is **not relaxed** by a representation change. No missing, null or
unsupported value is replaced by zero, empty text or an invented default. For
schema-declared fields, retain the event/parent/authorization-route conditions
recorded in the inventory. Prose-only requiredness and optional external fields
need an explicit future mapping. Contradictory flat/nested confidence values or
legacy/structured aliases require a conflict disposition, not precedence chosen
by whichever value validates. Existing reference resolution, notice periods,
approval identities/signatures and event-range checks remain separate checks.

## 4. Numeric thresholds are not wire fields

The inventory excludes loop counters, array lengths implied by examples, tag
numbers, cryptographic byte sizes, years/versions, hardware/benchmark figures and
business-cost estimates from quantity conversion. Named configuration examples
and the receipt diagram are included but labeled separately. The following
normative/policy thresholds must be reviewed independently of scalar bounds;
**none are changed** by this proposal:

| Source | Existing thresholds/meaning | Migration treatment |
|---|---|---|
| Body §§1.5.4, 2, 6.3.3 | ns/us/ms precision; clock/tier, 10min/1h/24h anchors | Precision labels do not change TimestampInt's ns unit; preserve tier policy |
| Annex §§1.4.1–1.4.3 | REORG max 100 events; SKIP 10/100/1000 and 1s/1min/1h | Ns candidate SkipDuration limits 10^9 / 60×10^9 / 3600×10^9, retaining anchor boundaries |
| Annex §§1.4.6–1.4.10 | 24h/72h notice; >=2 distinct human approvers; <=72h review | Exact elapsed comparison and referenced evidence; not scalar schema success |
| Annex §2 | Blockchain classification, finality/monitoring criteria and illustrative weights | Do not convert an approximate security-weight formula into an authenticated timestamp or new normative numeric field |
| Annex §6 | Tier latency budgets and p99/sample methodology | Performance measurement units, not event integer encodings; no benchmark rerun claimed |
| Annex §7.3.2 | Outage 10min/2h/48h, relative failover 30min/4h/7days, RPO | Distinguish relative allowance from absolute FailoverDeadline; no new deadline calculation without trigger evidence |
| Annex §7.8.2 | Retry 3/5/10; initial/max backoff; failure OR elapsed-time triggers | Preserve comparisons and seconds conversions; a count's type ceiling is not the retry limit |
| Annex §§7.8.4–7.8.5 | Configuration health date, health frequency, success % and latency | Configuration is distinct from evidence time; percent thresholds are not ConfidenceScore |
| Schema minItems/minLength, predicates | e.g. two emergency approvals, justification length, count>0 endpoints | These numeric schema constraints are not serialized quantities; keep existing semantics |

## 5. Migration impact and release gates

| Boundary | Concrete impact | Required future treatment |
|---|---|---|
| Existing JSON integers / mixed ConfidenceScore | Wire type changes, new bounds and exact lexemes | Select a distinct schema/format identifier; no string-or-number fallback within the new contract |
| Header/Payload hash inputs | Numeric conversion changes preimages, EventHash, dependent PrevHash, leaves and roots | Preserve original bytes/chain; new runs/attestations use a new context and record relation to originals |
| Anchor metadata / approval signatures | New representations alter signed messages where covered; legacy root-only signatures leave metadata unbound | Define each signed preimage explicitly; a new signature is a new claim and never restores old coverage |
| ISO pair / unit gaps | Current examples and possible deployments can disagree; pre-epoch and >2262 dates outside candidate | Identify format and value provenance; report unsupported/ambiguous or inconsistent evidence, no magnitude heuristic |
| Financial/risk/model strings | New length/value bounds and policy bindings may reject legacy values even without wire-type change | Capacity and semantics review; no trimming/rounding of signed text; preserve accepted source lexemes |
| API/DB/SDK/analytics | Integer columns, numeric comparisons and date tooling may not accept strings; lexical sort is not numeric sort | Separately versioned API/storage adapters with exact arithmetic and index strategy; no deployed implementation edited now |
| SBE/FlatBuffers/COSE/external receipts | JSON spelling is not a binary signed-byte mapping | Separate explicit mappings/algorithm identifiers and cross-format vectors before release |
| Operational policy | Scalar validity does not prove notice, authorization, delivery, finality or complete observation | Keep policy/range-resolution/evidence judgments distinct from byte integrity |
| Release compatibility | Body §1.3 promises v1.x backward compatibility | Major revision or distinct format may be required; no patch/minor release assumed compatible |

Legacy verification uses its identified original contract and separately reports
missing coverage. Never auto-select whichever interpretation verifies. If the
original exact value was lost through floating-point parsing, do not reconstruct
a guessed pre-rounding integer. A new metadata attestation or unit annotation is
a dated, attributed claim stored separately; it does not authenticate the old
source or an earlier external time. Keep distributions, historical records and
K3 inputs/criteria/results untouched. Any later extra K3 assessment requires a
separate decision and record.

Open decisions: capacity/sign of each class; final UTC/leap-smear policy; financial
and model units/scale/registry; inherited versus structured field/presence mapping;
open extension policy; native binary/COSE mapping; policy-byte binding and all
signature preimages; source/target version, rollout and approval authority. This
inventory supplies a concrete starting point, **not a declaration that these
release gates are closed**.

Future acceptance evidence must exercise every mapped path, just outside and on
its bounds, unknown/null/boolean/number substitutions, aliases, overflow,
leap/ISO disagreements, decimal scale and unit conflicts. Include 2^53−1, 2^53,
2^53+1, 2^31−1, 2^31 and 2^63−1/2^63, plus TIME_NS's upper date. Record exact
bytes/hash/signature consequences with separately versioned synthetic data and
independently implemented parsers. Existing byte-contract v0 vectors are retained
unchanged; their success does not cover all these native paths.

[RFC 8785 §3.1 and Appendix D](https://www.rfc-editor.org/rfc/rfc8785.html#section-3.1)
describe binary64-compatible JSON numbers and strings for larger exact values.
This proposal does **not** claim every integer above 2^53 is forbidden by JCS;
some are exactly representable, while arbitrary ns values are not preserved by
that number model. The proposed decimal strings are a domain contract, not a
change to JCS.

## 6. Review and reproducibility

Run from the repository root (Python 3.12+ standard library only):

```sh
python3 proposals/numeric-fields-2026-10-25/audit_inventory.py
python3 -m unittest discover -s proposals/numeric-fields-2026-10-25 -p 'test_audit_inventory.py' -v
```

The read-only default rejects duplicate JSON keys and non-JSON numeric constants,
and checks source hashes, reachable schema scalar coverage,
snapshotted constraints/requiredness, reference line ranges, unique inventory
paths and the generated Markdown. Snapshot comparison preserves parsed value
types: `false`, `0` and `0.0` are not interchangeable source snapshots even where
two numeric constraints could be semantically equivalent. This audit rule is not
a change to VCP's scalar rules. `--render` regenerates only inventory.md in
this new proposal directory. No network, signatures, deployment configuration or
existing fixture is executed or modified. The script is an inventory consistency
audit, **not a numeric/protocol verifier**, and does not mechanically validate the
manual prose judgments. The regression suite mutates temporary copies only.
See [review-record.md](review-record.md) for the initial checks and
[final-review-2026-10-25.md](final-review-2026-10-25.md) for the final findings,
repairs and validation. No external evaluator run is claimed.
