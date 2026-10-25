# Proposed native placement and numeric/time interpretation

**UNADOPTED; not effective. Independent third-party reproduction not established.**
This is a concrete design option for review, not a complete wire specification.
Names here are local design names. No native schema, registry allocation or
implementation is created. Current requirements and prior experiments remain
unchanged. See the [source baseline](README.md#evidence-baseline-and-source-fingerprints)
and [open decisions/migration gates](decisions-and-migration.md).

## L-01 — Complete event commitment, with native logical paths

Prefer a new native `EventCommitment` that contains the **complete selected
future-format** Header and Payload, complete PolicyIdentification when present
(explicit null when absent), and explicit chain and policy bindings. This is a
new record shape: existing v1.2 objects are not accepted merely by deleting
Security, renaming fields or coercing their values. No unrecognized field may be
silently removed to fit a hash preimage.

The proposed outer members are:

| Logical member of future EventCommitment | Proposed placement / rule |
| --- | --- |
| `ContractID`, `EventHashAlgorithm` | A new assigned contract and its selected algorithm, never the unchanged research-v0 identifier |
| `Header` | Preserve native EventID, ActorID, ChainID, SequenceNum, EventType, PolicyID and all other fields permitted by the selected future Header. Keep required TimestampInt and TimestampISO together here |
| `Payload` | Preserve domain module structure and every admitted key/value; numerical fields stay at their field-specific logical paths |
| `PolicyIdentification` | Preserve the whole admitted object, including any dates and verification declarations; null only where the selected format allows absence |
| `RegistrationPolicyBinding` | Proposed exact members `PolicyID`, `PolicyVersion`, `PolicyDigest`; bind the operating/registration policy bytes relevant to this event |
| `NumericPolicyBinding` | Proposed exact members `PolicyID`, `PolicyVersion`, `PolicyDigest`; bind the field, unit, time and representation interpretation described below |
| `Origin` | Protected distinction between a claimed new capture and a derived record. For derived records, commit the derivation-plan digest and source-entry identifier; see migration M-01 |
| `ChainMode`, `PreviousEventHash` | Explicit none/start/linked treatment as in the prior proposal, but under the new contract; predecessor appears once |

The set above is the preferred outer layout, not a complete definition of its
nested native objects. Each admitted nested field still needs schema, presence,
nullability, authority and extension rules before a native verifier can be built.
For example, inherited clock precision/status claims must not be inserted into
today's closed Header just because they appear in prose. Their protected native
location is a separate mapping blocker; do not drop them if a source uses them.

Propose native **ActorID/ChainID**, not the synthetic ProducerID/StreamID aliases,
in the future event-signature statement. Bind ContractID, selected schemes,
EventHash, EventID, ActorID, ChainID and KeyID; compare the identity values with
the committed Header. Identifier namespace/uniqueness, producer-to-actor roles,
delegation and key authority still require a recorded decision. Do not equate
an ActorID to a legal identity or infer authority from a key carried by the event.

For the first candidate, prefer a single actor/chain across a batch, with each
policy binding identical across its events. The registration and numeric
bindings need not equal each other. A future AnchorStatement binds those
identities, bindings, schemes, count, endpoints, root, claimed creation time and
intended target. Recompute root/count/endpoints from the complete ordered batch
and compare event-derived identities, schemes and policy bindings with its events.
A subset and valid inclusion proofs do not establish these full-batch checks;
unavailable checks remain UNASSESSED, and any demonstrated mismatch remains FAIL.
The anchor's claimed creation time and intended target are not event fields to
equate with that list. Check them separately under the selected time policy and
receipt/target mapping; signing those claims does not establish external time
or successful delivery. Mixed-policy or mixed-actor batches are unsupported
pending a separate design; no permissive fallback is inferred. Existing native
requirements are not restricted by this unadopted proposal.

## L-02 — Disposition of every inventoried numeric path

The following accounting covers all **74** review entries in the pinned
inventory. It is placement accounting, not proof of a complete native schema.
“Retain path” means place that future field beneath `EventCommitment` while
retaining the remainder of its inventory path. It does **not** mean copy its
existing integer type or accept every source event/extension containing it.

| Inventory entries | Count | Proposed disposition |
| --- | ---: | --- |
| N001–N016 | 16 | Retain Header and Payload paths; N001/N002 are the required Header ISO/ns pair |
| N018–N035 | 18 | Retain PolicyIdentification and Payload paths and their event/authorization-route conditions |
| N041–N069 | 29 | Retain Payload paths subject to the context exceptions below; no blanket adoption of prose-only/open members |
| N017 | 1 | `InclusionEvidence.LeafIndex`, detached from EventCommitment, checked against the authenticated AnchorStatement count and proof |
| N036 | 1 | New `AnchorStatement.RecordedAtNs` is the signer's claimed creation time. It is **not** an automatic rename or semantic equivalence of legacy `AnchorRecord.Timestamp` |
| N037 | 1 | `AnchorStatement.EventCount`, positive decimal string and compared with the actual ordered list |
| N038–N040 | 3 | Detached `TargetObservation.Confirmations`, `.FinalityTimestamp`, `.LastHealthCheck`; explicit provenance/target/time evidence required, not retroactively added to an already signed anchor |
| N070 | 1 | Retain as configuration at `SecondaryAnchorConfiguration.Secondary.LastHealthCheck`, not as an event or AnchorRecord field |
| N071–N072 | 2 | Keep external receipt `tree_size`/`leaf_index` in the external service's original encoding and signed-byte contract |
| N073–N074 | 2 | Keep legacy aliases/codes under their identified original format; future mapping only through an explicit source-format rule |
| **Total** | **74** | **63 retained logical paths + 11 explicitly separated dispositions** |

The retained-path group has important limits:

- N012 flat ConfidenceScore and N056 DecisionFactors.ConfidenceScore remain
  distinct. Prefer future formats with an explicit permitted location for each
  event/model form; where both are permitted, require an explicit equivalence or
  distinct-meaning rule. Until that rule exists, conflicting or ambiguous dual
  representations block native acceptance; do not choose whichever validates.
- N050 general-recovery RecoveredEvents does **not** become a SYS_CHECKPOINT
  member. The current closed CHECKPOINT RecoveryAction rejects it. Propose its
  location only in a separately defined general-recovery form. N047–N051 also
  need an event-type/presence matrix; existing recovery permissions are unchanged.
- N053 feature Value and N067 TriggerValue require a typed feature/control
  declaration. A categorical string is not a decimal just because it contains
  digits. Financial/risk/model units require instrument/model policy; fixed
  lexical bounds alone are insufficient.
- N069 calendar RetentionPeriod is not elapsed seconds; its calendar semantics
  and supported subset remain open. No legal retention policy is changed.
- N070 and N040 share a field name, not a format or meaning. No global
  `LastHealthCheck` rewrite is allowed. If configuration affects acceptance,
  bind the relevant configuration/version under the appropriate approved policy;
  an unsigned mutable configuration URL cannot define signed-event meaning.
- N071/N072 external tree size/index do not become a VCP batch count/index.
  External receipts remain detached; no VCP string conversion is applied.

Preserve required-parent, event-type, approval-route and optional-field rules
from the source inventory. No missing, null or unsupported value becomes zero,
empty text or a fabricated default. Prose-only requiredness and unknown module
extensions stay open until explicitly mapped. Unknown fields can be preserved
as original evidence, but cannot be ignored when claiming native conformity.

## L-03 — Security and evidence placement without circularity

| Current / research element | Proposed future treatment |
| --- | --- |
| Event's computed `Security.EventHash` | Outside EventCommitment; recompute under the selected new contract and bind in the event-signature statement |
| `Security.PrevHash` | Exactly once as committed PreviousEventHash with an explicit chain mode; no append/redundant copy |
| Hash/signature/version identifiers | Protected ContractID and scheme fields; verify agreement with the selected native format, not an unsigned version hint |
| Own event Signature | Detached from EventCommitment; signature statement binds recomputed EventHash and native identity/context |
| PQC/dual signatures, COSE | Require explicit protected mappings and algorithm negotiation; preserve legacy records and do not silently drop a required signature or substitute Ed25519 |
| MerkleRoot, MerkleIndex, anchor references | Detached inclusion evidence tied to the signed AnchorStatement; verify index/count/path. Reference aliases/locators are not authenticated rules by themselves |
| Authorization/approval signatures inside Payload | Remain committed content; verify their own defined signed messages and authority separately |
| ExternalReceipts / later target observations | Outside the anchor commitment; each must prove its link to that commitment and target under its own trust/mapping rules |

Use new, distinct event/event-signature/anchor-signature/external-commitment
domains for the new format. Their final literals are unassigned. Preserve the
proposed dependency direction:

```text
exact policy bytes -> PolicyDigest bindings -> complete EventCommitment
 -> domain-prefixed canonical bytes -> EventHash -> digest-byte leaf / root
EventHash + protected event identity/schemes -> event signature statement
root + count + context + policy bindings + claimed time -> anchor signature
complete AnchorStatement + anchor signature -> external commitment
external commitment <- detached receipt / target observation evidence
```

This is a design relationship, not a new executed vector. Event signatures
remain outside EventHash/root in this option; an anchor over that root does not
authenticate which event-signature bytes were submitted. Changing that property
would require another selected contract, not a report-label adjustment.

N038–N040 observations obtained later cannot be put inside the original anchor
preimage without changing it. Prefer separately versioned observations referring
to the exact anchor commitment, observer/target, claimed observation time and
the measurement, with authenticated service proof or an observer signature and
independently configured trust. A locally signed finality claim is still only
that observer's claim. The observation format, signed bytes, freshness and
authority checks are **not specified or implemented** here; native acceptance
of those observations remains blocked.

## L-04 — Policy roles and path registry

Registration-policy authority and numerical interpretation are distinct roles.
The PR #14 fixture used one synthetic policy; it did not validate this separation.
Prefer two explicit bindings as above. Header.PolicyID and any
PolicyIdentification.PolicyID match the **registration** binding. They are not
automatically equated to a numeric-policy identifier. An alternative is a single
policy document with separately typed registration/numeric sections; it still
needs explicit authority, exact byte binding and role checks.

For either choice, hash the **exact retained policy-document bytes** with the
selected algorithm. Do not reserialize, change newlines or follow a mutable URI
before hashing. PolicyID and PolicyVersion inside the document match the signed
binding. Signature validity/digest equality alone does not approve an issuer or
allow a policy to redefine units: configured trust and the selected format's
permitted interpretation remain independent checks. Re-signing an unsupported
policy leaves interpretation unassessed, not automatically accepted.

Proposed numeric-policy content (a semantic checklist, **not a JSON schema**):

- Its role, identifier/version and selected new ContractID/schema identifier.
- A complete admitted field-path registry: path, event/context predicate,
  quantity kind, string grammar, unit, bound/scale, null/absence treatment,
  and associated count/operand paths where needed.
- Time basis `unix_no_leap`, epoch and unit for each timestamp class; designated
  Header ns/ISO pairing; separate resolution/accuracy policy references.
- Instrument, currency, feature/control definitions or digest-bound versions
  supplying otherwise unresolved dimensions. Fixed units cannot be overridden
  by an unsigned label or by a per-value alternate unit.
- Approved conversion rules by **source format + full path + source unit +
  target path/unit**, with exact factors, domain checks and authority limits.

Array path notation `[]` in the inventory is documentation, not an implemented
wildcard grammar. Prefer explicit array-element mapping with no overlapping
wildcards or last-match precedence. Final path/predicate grammar, registry
completeness, extension negotiation, resource bounds and authority/revocation
are open decisions. Until supplied, this is not a native conformance policy.

## U-01 — Exact units and conversions

Prefer the PR #11/12 field-specific scalar candidates unchanged for discussion:
canonical unsigned decimal strings for integer quantities; exact decimal
strings for financial/model values, preserving accepted lexical spelling. The
20-integer/18-fractional-digit decimal capacity and maxima of 2^31−1 / 2^63−1
(the positive maxima of signed 32-/64-bit integers) are proposed domain bounds,
not present-schema or JCS bounds. Negative prices and rebates remain
policy-dependent; confidence is [0,1] while utilization need not be. Boolean
fields with genuine boolean semantics remain booleans.

| Quantity / inventory anchor | Stored unit proposal | Permitted arithmetic proposal; no silent wire rewrite |
| --- | --- | --- |
| TIME_NS, Header N002 | Epoch ns, 0…9223372036854775807 | Exact integer calendar/time arithmetic |
| N028 MaxOutageDuration, N031 TotalDowntimeSec | Whole seconds, SECONDS63 | Multiply by 1,000,000,000 only for a typed ns comparison/addition; validate destination range |
| N042 ToleranceMs | Whole ms, 0…2147483647 | Multiply by 1,000,000 for comparison with ns; keep original stored ms |
| N048 MaxSkipDuration | Elapsed ns, proposed DURATION_NS63 | A new explicit unit choice; historical unit remains unknown without source evidence |
| N058 LatencyImpact | Exact decimal microseconds | Multiply by 1,000 for ns arithmetic; if an integer-ns destination cannot represent the result exactly, reject that conversion |
| N012/N056/N057 ratios | Unitless fraction [0,1] | Percent-to-ratio is only a separately authorized derived conversion with an identified percent source, not interpretation of a ratio field |
| Financial/risk quantities | Instrument/quote/fee/model-specific | No currency, lot, tick, sign or model-unit conversion without the referenced dimensional policy and data |

For conversion to an **integer** destination, propose computing `x * p / q`
with exact arithmetic; require `q > 0`, an integral result and the destination's
allowed range. For a decimal destination, require a terminating decimal within
its selected scale/capacity and an explicitly selected emission rule. Never use
binary floating point, truncation, saturation, modulo or inferred default units.
No default rounding rule is proposed. If exact representation fails, report
unsupported conversion and preserve the source; any future rounding mode would
need its own authorized, versioned rule and disclosed loss, never “equivalent”.

Worked **arithmetic examples, not executed migration vectors**:

- `1 s = 1000 ms = 1000000000 ns`. Equal duration does not make signed
  `{Value:"1", Unit:"s"}` and `{Value:"1000", Unit:"ms"}` byte-identical.
  PR #14 intentionally rejects the latter at its seconds-only duration path.
- `0.001 us = 1 ns`; `0.0001 us = 0.1 ns` cannot be written into an integer-ns
  field by the exact conversion rule. Neither becomes zero by truncation.
- Converting `75 percent` to ratio `0.75` is meaningful only for an identified
  percent-valued source. A value `"75"` already labeled `ratio` is invalid, not
  an invitation for a verifier to divide it by 100.
- Numerically equal strings such as `"1"`, `"1.0"` and `"01.00"` retain
  different string bytes when already accepted. Separately, `"0"` and `"-0"`
  compare equal arithmetically but retain different bytes. The verifier does
  not normalize either group. A new derived record's output spelling requires
  a specified rule recorded with the transformation; that rule is not selected
  here.

For units, always distinguish calculation used to **compare** immutable evidence
from transformation used to **create** new evidence. Current deadlines, retry
limits, SKIP limits, precision tiers and approval conditions are not converted
into new operational permissions by a scalar range or unit conversion.

## T-01 — Time representation and meaning

Prefer the prior candidate's exact pair at Header.TimestampInt (decimal ns
string) and Header.TimestampISO (`YYYY-MM-DDTHH:mm:ss.nnnnnnnnnZ`). Both are
required in the proposed native Header and must denote the same instant under
the bound `unix_no_leap` policy. The proposed range is epoch zero through
`2262-04-11T23:47:16.854775807Z`. Timestamp zero is an instant, not “missing”.
This choice is narrower than current accepted date-time syntax and needs a
new schema/version; it does not amend today's schema in place.

No digit-count guessing, millisecond date-object conversion or floating-point
rounding is permitted. Keep instant, elapsed duration, sequence order, observed
resolution and claimed clock accuracy separate. `RecordedAtNs` is the signer's
creation-time claim, not receipt time, finality time or independent timestamp.
Integer/ISO agreement does not establish physical truth, clock synchronization
or the order of simultaneous events; retain chain/sequence and clock policies.

For new evidence produced at the source, select the time basis before capture
and derive the pair from one exact reading. For legacy evidence, preserve both
original fields even when they disagree. The illustrative ns integer
`1735128000123456789` corresponds to `2024-12-25T12:00:00.123456789Z` under the
selected convention; a paired 2025 string is inconsistent, not a choice of two
equivalent encodings. An optional corrected attestation needs explicit source
evidence/authority and does not validate or replace the original pair.

Offsets and lower-case/variable-fraction spellings require explicit source
interpretation and an exact, separately approved transformation before any
new-format output. The resulting instant still has to lie within TIME_NS.
An instant before the epoch or beyond the proposed maximum cannot be made
eligible merely by changing its spelling or unit; preserve it as unsupported
by this candidate. Wider capacity or a different epoch needs a separate format
decision, not an offset, clamp or relabeling of the value. Syntactic right-padding
can preserve a known value, but cannot prove nine-digit measurement accuracy.
Do not fill a missing original counterpart and report the source pair verified.

Leap seconds, negative-leap handling, smear and TAI/GPS mappings remain
**unassessed/unsupported pending a specified conversion**. Preserve original
bytes and declared basis. Do not clamp `:60`, select the nearest second or assume
a smear function. Future support requires a named mapping/table/version with
authenticated provenance, range and inversion/ambiguity rules plus fresh vectors.
This is not a claim that all such source time representations are invalid.
