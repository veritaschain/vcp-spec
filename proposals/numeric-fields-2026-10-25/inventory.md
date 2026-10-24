# Numeric-field inventory

**UNADOPTED discussion draft; independent reproduction not established.**

Generated from [inventory.json](inventory.json). Read the [candidate rules and
migration limitations](README.md) before using the proposed classes. Full source
hashes are in [sources.json](sources.json). Required-at-leaf is not required-in-every-event.

The `Payload.` prefix on inherited module blocks is an inventory projection,
not a claim that the GA schema defines all these nested paths. LegacyHeader,
AnchorRecord, configuration and SCITTReceipt are separate contexts.

## N001: `Header.TimestampISO`

- **Context/group:** Header
- **Current definition:** Explicit schema field; exact scalar constraints attached.
- **Current unit/range evidence:** RFC 3339 date-time string; Header description specifies UTC and up to ns.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/Header/properties/TimestampISO`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"string","format":"date-time","description":"ISO 8601 / RFC 3339 timestamp, UTC, up to nanosecond precision."}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537)
- **Candidate:** `UTC_NS` — UTC date-time with exactly 9 fractional digits; maps exactly to TIME_NS.
- **Migration/limits:** New narrower UTC lexical subset; exact pair checking where Header.TimestampInt is present. Do not rewrite old ISO strings.

## N002: `Header.TimestampInt`

- **Context/group:** Header
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds; description says 64-bit, schema only enforces minimum 0.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/Header/properties/TimestampInt`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0,"description":"Nanoseconds since the Unix epoch (UTC), as a 64-bit integer.","$comment":"Values exceed 2^53; parsers must preserve 64-bit integer precision."}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [body L951–961](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L951-L961)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence.

## N003: `Header.SequenceNum`

- **Context/group:** Header
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Event ordinal within the Actor chain; schema says monotonically increasing; origin/step and maximum unspecified.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/Header/properties/SequenceNum`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0,"description":"Monotonically increasing sequence number within the Actor's chain."}`
- **Candidate:** `UINT63` — Count of events/occurrences (specified by field); SequenceNum is an ordinal.
- **Migration/limits:** Propose no wrap, strict increase per (ActorID,ChainID); gaps are not themselves proof of missing real activity. New upper bound; do not renumber old chains.

## N004: `Header.SCITTAlignment.RegistrationPolicy.IssuedAt`

- **Context/group:** Header
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Optional within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/SCITTAlignment/properties/RegistrationPolicy/properties/IssuedAt`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L933–954](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L933-L954)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence.

## N005: `Payload.VCP-TRADE.Price`

- **Context/group:** TRADE
- **Current definition:** Explicit schema field; exact scalar constraints attached.
- **Current unit/range evidence:** Order price; currency/instrument quantity basis not specified here.
- **Presence:** Optional within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/Payload/properties/VCP-TRADE/properties/Price`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"string","pattern":"^-?[0-9]+(\\.[0-9]+)?$","$comment":"Specification Section 4.2.2: all financial numeric values MUST be encoded as strings to avoid IEEE 754 precision loss under RFC 8785 canonicalization."}`
- **Text evidence:** [body L407–415](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L407-L415); [inherited L330–370](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L330-L370)
- **Candidate:** `DEC_SIGNED` — Quote-currency units per instrument unit, with tick/scale and permitted sign from an authenticated instrument policy.
- **Migration/limits:** Already a decimal string. Preserve its exact lexeme (including trailing zeros); proposed size bounds and unit/scale policy can narrow accepted inputs. No blanket integer conversion.

## N006: `Payload.VCP-TRADE.Quantity`

- **Context/group:** TRADE
- **Current definition:** Explicit schema field; exact scalar constraints attached.
- **Current unit/range evidence:** Quantity; instrument/lot/contract unit not specified here.
- **Presence:** Optional within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/Payload/properties/VCP-TRADE/properties/Quantity`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"string","pattern":"^-?[0-9]+(\\.[0-9]+)?$","$comment":"Specification Section 4.2.2: all financial numeric values MUST be encoded as strings to avoid IEEE 754 precision loss under RFC 8785 canonicalization."}`
- **Text evidence:** [body L407–415](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L407-L415); [inherited L330–370](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L330-L370)
- **Candidate:** `DEC_NONNEG` — Instrument units defined by policy (shares/contracts/base-asset/lot conversion explicit).
- **Migration/limits:** Already a decimal string. Preserve its exact lexeme (including trailing zeros); proposed size bounds and unit/scale policy can narrow accepted inputs. No blanket integer conversion.

## N007: `Payload.VCP-TRADE.ExecutedQty`

- **Context/group:** TRADE
- **Current definition:** Explicit schema field; exact scalar constraints attached.
- **Current unit/range evidence:** Quantity; instrument/lot/contract unit not specified here.
- **Presence:** Optional within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/Payload/properties/VCP-TRADE/properties/ExecutedQty`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"string","pattern":"^-?[0-9]+(\\.[0-9]+)?$","$comment":"Specification Section 4.2.2: all financial numeric values MUST be encoded as strings to avoid IEEE 754 precision loss under RFC 8785 canonicalization."}`
- **Text evidence:** [body L407–415](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L407-L415); [inherited L330–370](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L330-L370)
- **Candidate:** `DEC_NONNEG` — Instrument units on the same basis as Quantity.
- **Migration/limits:** Already a decimal string. Preserve its exact lexeme (including trailing zeros); proposed size bounds and unit/scale policy can narrow accepted inputs. No blanket integer conversion.

## N008: `Payload.VCP-TRADE.RemainingQty`

- **Context/group:** TRADE
- **Current definition:** Explicit schema field; exact scalar constraints attached.
- **Current unit/range evidence:** Quantity; instrument/lot/contract unit not specified here.
- **Presence:** Optional within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/Payload/properties/VCP-TRADE/properties/RemainingQty`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"string","pattern":"^-?[0-9]+(\\.[0-9]+)?$","$comment":"Specification Section 4.2.2: all financial numeric values MUST be encoded as strings to avoid IEEE 754 precision loss under RFC 8785 canonicalization."}`
- **Text evidence:** [body L407–415](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L407-L415); [inherited L330–370](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L330-L370)
- **Candidate:** `DEC_NONNEG` — Instrument units on the same basis as Quantity.
- **Migration/limits:** Already a decimal string. Preserve its exact lexeme (including trailing zeros); proposed size bounds and unit/scale policy can narrow accepted inputs. No blanket integer conversion.

## N009: `Payload.VCP-TRADE.ExecutionPrice`

- **Context/group:** TRADE
- **Current definition:** Explicit schema field; exact scalar constraints attached.
- **Current unit/range evidence:** Fill price; currency/instrument quantity basis not specified here.
- **Presence:** Optional within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/Payload/properties/VCP-TRADE/properties/ExecutionPrice`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"string","pattern":"^-?[0-9]+(\\.[0-9]+)?$","$comment":"Specification Section 4.2.2: all financial numeric values MUST be encoded as strings to avoid IEEE 754 precision loss under RFC 8785 canonicalization."}`
- **Text evidence:** [body L407–415](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L407-L415); [inherited L330–370](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L330-L370)
- **Candidate:** `DEC_SIGNED` — Quote-currency units per instrument unit, same explicit price basis as order/reference policy.
- **Migration/limits:** Already a decimal string. Preserve its exact lexeme (including trailing zeros); proposed size bounds and unit/scale policy can narrow accepted inputs. No blanket integer conversion.

## N010: `Payload.VCP-TRADE.Commission`

- **Context/group:** TRADE
- **Current definition:** Explicit schema field; exact scalar constraints attached.
- **Current unit/range evidence:** Commission amount; fee currency not specified here.
- **Presence:** Optional within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/Payload/properties/VCP-TRADE/properties/Commission`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"string","pattern":"^-?[0-9]+(\\.[0-9]+)?$","$comment":"Specification Section 4.2.2: all financial numeric values MUST be encoded as strings to avoid IEEE 754 precision loss under RFC 8785 canonicalization."}`
- **Text evidence:** [body L407–415](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L407-L415); [inherited L330–370](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L330-L370)
- **Candidate:** `DEC_SIGNED` — Fee-currency units specified by policy; do not assume it equals quote Currency; negative rebates permitted if declared.
- **Migration/limits:** Already a decimal string. Preserve its exact lexeme (including trailing zeros); proposed size bounds and unit/scale policy can narrow accepted inputs. No blanket integer conversion.

## N011: `Payload.VCP-TRADE.Slippage`

- **Context/group:** TRADE
- **Current definition:** Explicit schema field; exact scalar constraints attached.
- **Current unit/range evidence:** Slippage amount; absolute/relative unit and sign convention not specified here.
- **Presence:** Optional within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/Payload/properties/VCP-TRADE/properties/Slippage`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"string","pattern":"^-?[0-9]+(\\.[0-9]+)?$","$comment":"Specification Section 4.2.2: all financial numeric values MUST be encoded as strings to avoid IEEE 754 precision loss under RFC 8785 canonicalization."}`
- **Text evidence:** [body L407–415](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L407-L415); [inherited L330–370](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L330-L370)
- **Candidate:** `DEC_SIGNED` — Signed execution-price minus declared reference-price in price units; alternate bps/cost conventions require a distinct mapping, not silent conversion.
- **Migration/limits:** Already a decimal string. Preserve its exact lexeme (including trailing zeros); proposed size bounds and unit/scale policy can narrow accepted inputs. No blanket integer conversion.

## N012: `Payload.VCP-GOV.ConfidenceScore`

- **Context/group:** GOV
- **Current definition:** Explicit schema field; exact scalar constraints attached.
- **Current unit/range evidence:** Unitless confidence [0,1] described, but neither schema range nor numeric-string grammar enforced.
- **Presence:** Optional within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/Payload/properties/VCP-GOV/properties/ConfidenceScore`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":["string","number"],"description":"Confidence in [0.0, 1.0]. String encoding is RECOMMENDED for precision (Specification Section 5.1.1)."}`
- **Text evidence:** [inherited L400–411](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L400-L411)
- **Candidate:** `RATIO01` — Unitless fraction in [0,1], not a percentage value in [0,100].
- **Migration/limits:** Current schema permits number|string; candidate accepts decimal strings only and checks [0,1]. Distinct from nested DecisionFactors.ConfidenceScore; no alias or silent promotion.

## N013: `Payload.VCP-PRIVACY.ErasureDetails.Scope.AffectedEventCount`

- **Context/group:** ERASURE
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Affected event count; schema minimum 1.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/ErasureDetails/properties/Scope/properties/AffectedEventCount`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"integer","minimum":1}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L517–552](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L517-L552)
- **Candidate:** `POS63` — Count of affected events.
- **Migration/limits:** Verify explicit EventIDs count/order/endpoints or resolve source range; no continuity inferred from UUIDs. Candidate bound new; preserve old signed payload.

## N014: `Payload.VCP-PRIVACY.ErasureDetails.Authorization.AuthorizationTimestamp`

- **Context/group:** ERASURE
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/ErasureDetails/properties/Authorization/properties/AuthorizationTimestamp`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L517–552](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L517-L552)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence. Authorization <= destruction <= event timestamp; approval ordering requires its own policy, not a rule inferred from CHECKPOINT.

## N015: `Payload.VCP-PRIVACY.ErasureDetails.Authorization.ApprovalChain[].ApprovalTimestamp`

- **Context/group:** ERASURE
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/Approval/properties/ApprovalTimestamp`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L517–552](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L517-L552)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence. Authorization <= destruction <= event timestamp; approval ordering requires its own policy, not a rule inferred from CHECKPOINT.

## N016: `Payload.VCP-PRIVACY.ErasureDetails.CryptoShredding.DestructionTimestamp`

- **Context/group:** ERASURE
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/ErasureDetails/properties/CryptoShredding/properties/DestructionTimestamp`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L517–552](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L517-L552)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence. Authorization <= destruction <= event timestamp; approval ordering requires its own policy, not a rule inferred from CHECKPOINT.

## N017: `Security.MerkleIndex`

- **Context/group:** Security
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Zero-based leaf position; prose int32, schema minimum 0 only.
- **Presence:** Optional within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/Security/properties/MerkleIndex`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [body L1077–1105](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L1077-L1105)
- **Candidate:** `INDEX31` — Zero-based position within the identified batch/party topology.
- **Migration/limits:** Must be less than authenticated AnchorRecord.EventCount; string conversion changes enclosing bytes. Without authenticated count, size-bound result is unassessed.

## N018: `PolicyIdentification.RegistrationPolicy.EffectiveDate`

- **Context/group:** PolicyIdentification
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Optional within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/PolicyIdentification/properties/RegistrationPolicy/properties/EffectiveDate`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"integer"}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [body L423–443](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L423-L443)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence. Current schema permits negatives and has no minimum/maximum; pre-epoch values require legacy retention, not clamping.

## N019: `PolicyIdentification.RegistrationPolicy.ExpirationDate`

- **Context/group:** PolicyIdentification
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Optional within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/PolicyIdentification/properties/RegistrationPolicy/properties/ExpirationDate`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: all structured events.
- **Exact scalar snapshot:** `{"type":"integer"}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [body L423–443](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L423-L443)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence. Current schema permits negatives and has no minimum/maximum; pre-epoch values require legacy retention, not clamping.

## N020: `Payload.VCP-RECOVERY.Announcement.ScheduledTime`

- **Context/group:** RECOVERY
- **Current definition:** Explicit schema field; exact scalar constraints attached.
- **Current unit/range evidence:** RFC 3339 date-time string; Header description specifies UTC and up to ns.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/RecoveryAnnouncement/properties/ScheduledTime`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_RECOVERY_ANNOUNCE.
- **Exact scalar snapshot:** `{"type":"string","format":"date-time"}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L312–348](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L312-L348)
- **Candidate:** `UTC_NS` — UTC date-time with exactly 9 fractional digits; maps exactly to TIME_NS.
- **Migration/limits:** New narrower UTC lexical subset; exact pair checking where Header.TimestampInt is present. Do not rewrite old ISO strings. Preserve 24h/72h advance notice and authentic referenced-notice checks.

## N021: `Payload.VCP-RECOVERY.RecoveryAction.EmergencyOverride.ApprovalChain[].ApprovalTimestamp`

- **Context/group:** RECOVERY
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed. This is the emergency=true authorization route; the normal notice route does not admit this approval chain.
- **Schema site:** [`/$defs/Approval/properties/ApprovalTimestamp`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_CHECKPOINT.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L312–348](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L312-L348)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence. CHECKPOINT emergency approval times <= event time; per-human authorization is separate.

## N022: `Payload.VCP-GOV.AuditDetails.ReviewedAt`

- **Context/group:** RECOVERY
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/AuditDetails/properties/ReviewedAt`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_AUDIT.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L312–348](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L312-L348)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence. Preserve referenced incident/checkpoint and <=72h review checks; no invented zero for a missing review.

## N023: `Payload.VCP-ANCHOR.MigrationDetails.OldAnchorTarget.LastAnchorTimestamp`

- **Context/group:** MIGRATION
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/MigrationDetails/properties/OldAnchorTarget/properties/LastAnchorTimestamp`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_ANCHOR_MIGRATION.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L1204–1260](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1204-L1260)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence.

## N024: `Payload.VCP-ANCHOR.MigrationDetails.NewAnchorTarget.FirstAnchorTimestamp`

- **Context/group:** MIGRATION
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/MigrationDetails/properties/NewAnchorTarget/properties/FirstAnchorTimestamp`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_ANCHOR_MIGRATION.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L1204–1260](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1204-L1260)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence.

## N025: `Payload.VCP-ANCHOR.MigrationDetails.DualAnchorPeriod.StartTimestamp`

- **Context/group:** MIGRATION
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/MigrationDetails/properties/DualAnchorPeriod/properties/StartTimestamp`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_ANCHOR_MIGRATION.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L1204–1260](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1204-L1260)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence.

## N026: `Payload.VCP-ANCHOR.MigrationDetails.DualAnchorPeriod.EndTimestamp`

- **Context/group:** MIGRATION
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/MigrationDetails/properties/DualAnchorPeriod/properties/EndTimestamp`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_ANCHOR_MIGRATION.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L1204–1260](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1204-L1260)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence.

## N027: `Payload.VCP-ANCHOR.MigrationDetails.DualAnchorPeriod.OverlapEventCount`

- **Context/group:** MIGRATION
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Overlapping event count; schema minimum 0.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/MigrationDetails/properties/DualAnchorPeriod/properties/OverlapEventCount`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_ANCHOR_MIGRATION.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L1204–1260](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1204-L1260)
- **Candidate:** `UINT63` — Count of events/occurrences (specified by field); SequenceNum is an ordinal.
- **Migration/limits:** Actual overlap evidence still required. Count 0 is not an absent count. Type/bound changes require a new format.

## N028: `Payload.VCP-ANCHOR.MigrationDetails.TierSpecificRTO.MaxOutageDuration`

- **Context/group:** MIGRATION
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Whole seconds, explicitly excepted by Annex §3.4.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/MigrationDetails/properties/TierSpecificRTO/properties/MaxOutageDuration`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_ANCHOR_MIGRATION.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L1204–1260](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1204-L1260)
- **Candidate:** `SECONDS63` — Whole seconds (unchanged).
- **Migration/limits:** Only wire type changes; do not multiply the stored seconds into nanoseconds. Tier thresholds remain unchanged.

## N029: `Payload.VCP-ANCHOR.MigrationDetails.TierSpecificRTO.FailoverDeadline`

- **Context/group:** MIGRATION
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/MigrationDetails/properties/TierSpecificRTO/properties/FailoverDeadline`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_ANCHOR_MIGRATION.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L1204–1260](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1204-L1260)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence. Absolute timestamp in fixture, not the relative 30min/4h/7day deadline interval from §7.3.2; trigger/start evidence is required to relate them.

## N030: `Payload.VCP-ANCHOR.FailoverDetails.TriggerCondition.FailureCount`

- **Context/group:** FAILOVER
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Failure or queued-event count, respectively; schema minimum 0.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/FailoverDetails/properties/TriggerCondition/properties/FailureCount`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_ANCHOR_FAILOVER.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L1341–1398](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1341-L1398)
- **Candidate:** `UINT63` — Count of events/occurrences (specified by field); SequenceNum is an ordinal.
- **Migration/limits:** Do not convert an absent count to zero. Queued-event endpoint obligations for Count>0 and actual queue reconciliation remain separate.

## N031: `Payload.VCP-ANCHOR.FailoverDetails.TriggerCondition.TotalDowntimeSec`

- **Context/group:** FAILOVER
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Whole seconds, explicitly named *Sec and covered by Annex §3.4.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/FailoverDetails/properties/TriggerCondition/properties/TotalDowntimeSec`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_ANCHOR_FAILOVER.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L1341–1398](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1341-L1398)
- **Candidate:** `SECONDS63` — Whole seconds (unchanged).
- **Migration/limits:** Type conversion only; no unit change. Preserve > thresholds and cross-event evidence.

## N032: `Payload.VCP-ANCHOR.FailoverDetails.TriggerCondition.LastSuccessfulAnchor`

- **Context/group:** FAILOVER
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/FailoverDetails/properties/TriggerCondition/properties/LastSuccessfulAnchor`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_ANCHOR_FAILOVER.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L1341–1398](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1341-L1398)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence. This is an absolute timestamp despite the name, not an anchor counter; missing success is not epoch 0.

## N033: `Payload.VCP-ANCHOR.FailoverDetails.PrimaryAnchor.LastAttemptTimestamp`

- **Context/group:** FAILOVER
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/FailoverDetails/properties/PrimaryAnchor/properties/LastAttemptTimestamp`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_ANCHOR_FAILOVER.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L1341–1398](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1341-L1398)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence.

## N034: `Payload.VCP-ANCHOR.FailoverDetails.SecondaryAnchor.ActivationTimestamp`

- **Context/group:** FAILOVER
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Epoch nanoseconds under Annex §3.4 structured-encoding rule; not restated on this schema property.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/FailoverDetails/properties/SecondaryAnchor/properties/ActivationTimestamp`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_ANCHOR_FAILOVER.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L1341–1398](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1341-L1398)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** JSON integer to exact decimal string changes hashed/signed bytes; range is newly bounded. Preserve original evidence.

## N035: `Payload.VCP-ANCHOR.FailoverDetails.QueuedEvents.Count`

- **Context/group:** FAILOVER
- **Current definition:** Explicit schema field; exact scalar constraints attached. No maximum enforced.
- **Current unit/range evidence:** Failure or queued-event count, respectively; schema minimum 0.
- **Presence:** Required within its containing schema object; ancestors/conditional context still control presence. No null allowed by this scalar schema; no new default proposed.
- **Schema site:** [`/$defs/FailoverDetails/properties/QueuedEvents/properties/Count`](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/vcp-event-v1.2.json); context: SYS_ANCHOR_FAILOVER.
- **Exact scalar snapshot:** `{"type":"integer","minimum":0}`
- **Text evidence:** [annex L534–537](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L534-L537); [annex L1341–1398](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1341-L1398)
- **Candidate:** `UINT63` — Count of events/occurrences (specified by field); SequenceNum is an ordinal.
- **Migration/limits:** Do not convert an absent count to zero. Queued-event endpoint obligations for Count>0 and actual queue reconciliation remain separate.

## N036: `AnchorRecord.Timestamp`

- **Context/group:** ANCHOR
- **Current definition:** Prose record; not part of the event schema. Repeated in Appendix E.3.
- **Current unit/range evidence:** Anchor time; int64 in body; unit not locally restated. Candidate explicitly uses epoch ns.
- **Presence:** Required in body AnchorRecord example.
- **Text evidence:** [body L1023–1043](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L1023-L1043)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** New signed-record mapping required; this is not Header.TimestampInt or an external service-authenticated time.

## N037: `AnchorRecord.EventCount`

- **Context/group:** ANCHOR
- **Current definition:** Prose field; not in event schema.
- **Current unit/range evidence:** Events in batch; int32 in body; signedness/lower bound not otherwise stated.
- **Presence:** Shown without explicit REQUIRED comment; candidate requires it for any nonempty signed batch.
- **Text evidence:** [body L1023–1043](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L1023-L1043)
- **Candidate:** `POS31` — Count of batch events or parties (specified by field).
- **Migration/limits:** Propose nonempty batches and authenticated count; legacy root-only signatures do not authenticate this field. Empty batches remain unsupported.

## N038: `AnchorRecord.AnchorTarget.Confirmations`

- **Context/group:** ANCHOR
- **Current definition:** Prose AnchorTarget extension; outside event schema.
- **Current unit/range evidence:** Number of confirmations at anchor time; int32.
- **Presence:** EnhancedMonitoring is REQUIRED for Class C/D; no inferred default time/count for other targets.
- **Text evidence:** [annex L475–495](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L475-L495)
- **Candidate:** `UINT31` — Count of events/confirmations (specified by field).
- **Migration/limits:** Proposed epoch ns for times; confirmation count is not elapsed time. Target-specific finality/receipt semantics and signatures remain a separate mapping gate.

## N039: `AnchorRecord.AnchorTarget.FinalityTimestamp`

- **Context/group:** ANCHOR
- **Current definition:** Prose AnchorTarget extension; outside event schema.
- **Current unit/range evidence:** Time finality achieved; int64; unit not locally restated.
- **Presence:** EnhancedMonitoring is REQUIRED for Class C/D; no inferred default time/count for other targets.
- **Text evidence:** [annex L475–495](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L475-L495)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** Proposed epoch ns for times; confirmation count is not elapsed time. Target-specific finality/receipt semantics and signatures remain a separate mapping gate.

## N040: `AnchorRecord.AnchorTarget.EnhancedMonitoring.LastHealthCheck`

- **Context/group:** ANCHOR
- **Current definition:** Prose AnchorTarget extension; outside event schema.
- **Current unit/range evidence:** Time of last health check; int64; unit not locally restated.
- **Presence:** EnhancedMonitoring is REQUIRED for Class C/D; no inferred default time/count for other targets.
- **Text evidence:** [annex L475–495](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L475-L495)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** Proposed epoch ns for times; confirmation count is not elapsed time. Target-specific finality/receipt semantics and signatures remain a separate mapping gate.

## N041: `Payload.VCP-XREF.SharedEventKey.Timestamp`

- **Context/group:** XREF
- **Current definition:** VCP-XREF object is open in schema; these fields are not typed there.
- **Current unit/range evidence:** int64 timestamp; body verification multiplies ToleranceMs by 1,000,000, indicating ns comparison.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [body L524–630](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L524-L630)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** Require explicit source encoding/unit before migration; exact arithmetic for difference and tolerance.

## N042: `Payload.VCP-XREF.SharedEventKey.ToleranceMs`

- **Context/group:** XREF
- **Current definition:** Prose only; schema object open.
- **Current unit/range evidence:** Milliseconds, int32; examples 100; nonnegative bound not stated.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [body L524–630](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VCP-Specification-v1_2_en.md#L524-L630)
- **Candidate:** `MILLISECONDS31` — Whole milliseconds (unchanged).
- **Migration/limits:** Keep milliseconds; multiply by 1,000,000 only in comparison arithmetic, using non-overflowing integers. Inclusive match at equal tolerance.

## N043: `Payload.VCP-XREF.PartyIndex`

- **Context/group:** XREF
- **Current definition:** Prose only; not constrained inside open VCP-XREF schema.
- **Current unit/range evidence:** Zero-based position, 0=initiator; int32.
- **Presence:** TotalParties is SHOULD in §9.6; multi-actor extension is optional. Missing total means unassessed index bound, not automatic success.
- **Text evidence:** [annex L1540–1573](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1540-L1573)
- **Candidate:** `INDEX31` — Zero-based position within the identified batch/party topology.
- **Migration/limits:** Candidate index < trusted/validated TotalParties; topology and role consistency need policy. Cross-party observed times do not prove causality without clock/trust evidence.

## N044: `Payload.VCP-XREF.UpstreamParty.ReceivedTimestamp`

- **Context/group:** XREF
- **Current definition:** Prose only; not constrained inside open VCP-XREF schema.
- **Current unit/range evidence:** int64; epoch ns for structured encoding, not locally restated.
- **Presence:** TotalParties is SHOULD in §9.6; multi-actor extension is optional. Missing total means unassessed index bound, not automatic success.
- **Text evidence:** [annex L1540–1573](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1540-L1573)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** Candidate index < trusted/validated TotalParties; topology and role consistency need policy. Cross-party observed times do not prove causality without clock/trust evidence.

## N045: `Payload.VCP-XREF.DownstreamParties[].ForwardedTimestamp`

- **Context/group:** XREF
- **Current definition:** Prose only; not constrained inside open VCP-XREF schema.
- **Current unit/range evidence:** int64; epoch ns for structured encoding, not locally restated.
- **Presence:** TotalParties is SHOULD in §9.6; multi-actor extension is optional. Missing total means unassessed index bound, not automatic success.
- **Text evidence:** [annex L1540–1573](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1540-L1573)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** Candidate index < trusted/validated TotalParties; topology and role consistency need policy. Cross-party observed times do not prove causality without clock/trust evidence.

## N046: `Payload.VCP-XREF.ChainMetadata.TotalParties`

- **Context/group:** XREF
- **Current definition:** Prose only; not constrained inside open VCP-XREF schema.
- **Current unit/range evidence:** Party count, int32; no lower bound stated.
- **Presence:** TotalParties is SHOULD in §9.6; multi-actor extension is optional. Missing total means unassessed index bound, not automatic success.
- **Text evidence:** [annex L1540–1573](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1540-L1573)
- **Candidate:** `POS31` — Count of batch events or parties (specified by field).
- **Migration/limits:** Candidate index < trusted/validated TotalParties; topology and role consistency need policy. Cross-party observed times do not prove causality without clock/trust evidence.

## N047: `Payload.VCP-RECOVERY.RecoveryConstraints.MaxSkipEvents`

- **Context/group:** RECOVERY
- **Current definition:** Prose only at these paths; BreakPoint/ChainValidation are open in CHECKPOINT, RecoveryConstraints is not explicitly defined in schema.
- **Current unit/range evidence:** Maximum skipped events; int32; tier caps 10/100/1000.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [annex L93–160](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L93-L160)
- **Candidate:** `UINT31` — Count of events/confirmations (specified by field).
- **Migration/limits:** General recovery prose is not a complete SYS_CHECKPOINT schema. Preserve SKIP limits and anchor-boundary rule; no new recovery operation authorized.

## N048: `Payload.VCP-RECOVERY.RecoveryConstraints.MaxSkipDuration`

- **Context/group:** RECOVERY
- **Current definition:** Prose only at these paths; BreakPoint/ChainValidation are open in CHECKPOINT, RecoveryConstraints is not explicitly defined in schema.
- **Current unit/range evidence:** int64 duration; no wire unit assigned here and not covered by *Sec exception.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [annex L93–160](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L93-L160)
- **Candidate:** `DURATION_NS63` — Nanoseconds of elapsed duration (new explicit choice).
- **Migration/limits:** General recovery prose is not a complete SYS_CHECKPOINT schema. Preserve SKIP limits and anchor-boundary rule; no new recovery operation authorized. Candidate chooses ns explicitly (1s/60s/3600s = 1000000000/60000000000/3600000000000); historical unit cannot be inferred from integer magnitude.

## N049: `Payload.VCP-RECOVERY.BreakPoint.BreakTimestamp`

- **Context/group:** RECOVERY
- **Current definition:** Prose only at these paths; BreakPoint/ChainValidation are open in CHECKPOINT, RecoveryConstraints is not explicitly defined in schema.
- **Current unit/range evidence:** int64; epoch ns in structured encoding.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [annex L93–160](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L93-L160)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** General recovery prose is not a complete SYS_CHECKPOINT schema. Preserve SKIP limits and anchor-boundary rule; no new recovery operation authorized.

## N050: `Payload.VCP-RECOVERY.RecoveryAction.RecoveredEvents`

- **Context/group:** RECOVERY
- **Current definition:** Prose only at these paths; BreakPoint/ChainValidation are open in CHECKPOINT, RecoveryConstraints is not explicitly defined in schema.
- **Current unit/range evidence:** Recovered event count; int32.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [annex L93–160](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L93-L160)
- **Candidate:** `UINT31` — Count of events/confirmations (specified by field).
- **Migration/limits:** General recovery prose is not a complete SYS_CHECKPOINT schema. Preserve SKIP limits and anchor-boundary rule; no new recovery operation authorized. SYS_CHECKPOINT RecoveryAction.additionalProperties=false currently rejects RecoveredEvents; keep general recovery versus CHECKPOINT contexts separate.

## N051: `Payload.VCP-RECOVERY.ChainValidation.AnchorVerificationTimestamp`

- **Context/group:** RECOVERY
- **Current definition:** Prose only at these paths; BreakPoint/ChainValidation are open in CHECKPOINT, RecoveryConstraints is not explicitly defined in schema.
- **Current unit/range evidence:** int64; epoch ns in structured encoding.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [annex L93–160](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L93-L160)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** General recovery prose is not a complete SYS_CHECKPOINT schema. Preserve SKIP limits and anchor-boundary rule; no new recovery operation authorized.

## N052: `Payload.VCP-GOV.Governance.ApprovalTimestamp`

- **Context/group:** GOV
- **Current definition:** Inherited prose inside open VCP-GOV; not schema-typed.
- **Current unit/range evidence:** int64; unit not locally stated; structured encoding rule provides ns.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L380–417](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L380-L417)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** Do not confuse governance approval with erasure/checkpoint approval; authorization/signature and presence mapping remain open.

## N053: `Payload.VCP-GOV.DecisionFactors.Features[].Value`

- **Context/group:** GOV
- **Current definition:** Inherited prose; DecisionFactors permits array|object with unconstrained contents; other added members are open.
- **Current unit/range evidence:** Feature value as string; may be numeric or categorical.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L380–417](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L380-L417)
- **Candidate:** `TYPED_FEATURE` — Per-feature declared type/unit/scale/bounds; categorical strings remain categorical.
- **Migration/limits:** Do not parse all feature strings as numbers. Policy must identify type, unit, scale and bounds per feature.

## N054: `Payload.VCP-GOV.DecisionFactors.Features[].Weight`

- **Context/group:** GOV
- **Current definition:** Inherited prose; DecisionFactors permits array|object with unconstrained contents; other added members are open.
- **Current unit/range evidence:** Weight string; normalization/unit/range not specified.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L380–417](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L380-L417)
- **Candidate:** `DEC_SIGNED` — Signed model weight in the unit declared for that model/feature; no normalization assumed.
- **Migration/limits:** Candidate signed decimal with policy-defined model units; no assumed [0,1] bound or sum=1.

## N055: `Payload.VCP-GOV.DecisionFactors.Features[].Contribution`

- **Context/group:** GOV
- **Current definition:** Inherited prose; DecisionFactors permits array|object with unconstrained contents; other added members are open.
- **Current unit/range evidence:** SHAP/LIME contribution string; output unit/range unspecified.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L380–417](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L380-L417)
- **Candidate:** `DEC_SIGNED` — Signed model-output units identified by explanation policy (including transform/base value).
- **Migration/limits:** Candidate signed decimal in the declared model-output units; never reinterpret as a probability.

## N056: `Payload.VCP-GOV.DecisionFactors.ConfidenceScore`

- **Context/group:** GOV
- **Current definition:** Inherited prose; DecisionFactors permits array|object with unconstrained contents; other added members are open.
- **Current unit/range evidence:** Unitless confidence 0.0–1.0 string.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L380–417](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L380-L417)
- **Candidate:** `RATIO01` — Unitless fraction in [0,1], not a percentage value in [0,100].
- **Migration/limits:** Distinct path from VCP-GOV.ConfidenceScore; reject conflicting dual representations in a future mapping, do not pick whichever passes.

## N057: `Payload.VCP-GOV.PerformanceMetadata.SamplingRate`

- **Context/group:** GOV
- **Current definition:** Inherited prose; DecisionFactors permits array|object with unconstrained contents; other added members are open.
- **Current unit/range evidence:** Unitless sample fraction; 1.0=100%, 0.1=10%.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L380–417](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L380-L417)
- **Candidate:** `RATIO01` — Unitless fraction in [0,1], not a percentage value in [0,100].
- **Migration/limits:** Candidate [0,1]; zero is explicit no sampling, absent is unknown. Sampled evidence is not full coverage.

## N058: `Payload.VCP-GOV.PerformanceMetadata.LatencyImpact`

- **Context/group:** GOV
- **Current definition:** Inherited prose; DecisionFactors permits array|object with unconstrained contents; other added members are open.
- **Current unit/range evidence:** Microseconds added, as string.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L380–417](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L380-L417)
- **Candidate:** `DEC_NONNEG` — Microseconds added, allowing fractional microseconds.
- **Migration/limits:** Preserve microseconds and fractional precision; do not confuse with integer ns timestamps or tier latency thresholds.

## N059: `Payload.VCP-RISK.RiskProfile.LastModified`

- **Context/group:** RISK
- **Current definition:** Inherited prose; VCP-RISK is an open object.
- **Current unit/range evidence:** int64; local unit unspecified, ns under structured rule.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L426–463](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L426-L463)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** New exact string changes event bytes; authenticated policy identity/version and no-default rule required.

## N060: `Payload.VCP-RISK.ParametersSnapshot.MaxOrderSize`

- **Context/group:** RISK
- **Current definition:** Inherited example string; not schema-typed, not an independently defined numeric range.
- **Current unit/range evidence:** Order quantity limit; unit missing.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L426–463](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L426-L463)
- **Candidate:** `DEC_NONNEG` — Instrument quantity units identified by risk policy.
- **Migration/limits:** Candidate nonnegative exact decimal. Unit, scale, instrument/currency and policy bounds must be identified; no requirement to stop/reject operations is created.

## N061: `Payload.VCP-RISK.ParametersSnapshot.MaxPositionSize`

- **Context/group:** RISK
- **Current definition:** Inherited example string; not schema-typed, not an independently defined numeric range.
- **Current unit/range evidence:** Position quantity limit; unit missing.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L426–463](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L426-L463)
- **Candidate:** `DEC_NONNEG` — Instrument quantity units identified by risk policy; limit magnitude, not signed net position.
- **Migration/limits:** Candidate nonnegative exact decimal. Unit, scale, instrument/currency and policy bounds must be identified; no requirement to stop/reject operations is created.

## N062: `Payload.VCP-RISK.ParametersSnapshot.DailyExposureLimit`

- **Context/group:** RISK
- **Current definition:** Inherited example string; not schema-typed, not an independently defined numeric range.
- **Current unit/range evidence:** Exposure limit; amount/currency basis missing.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L426–463](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L426-L463)
- **Candidate:** `DEC_NONNEG` — Risk-policy currency amount; net/gross exposure, valuation and daily window explicit.
- **Migration/limits:** Candidate nonnegative exact decimal. Unit, scale, instrument/currency and policy bounds must be identified; no requirement to stop/reject operations is created.

## N063: `Payload.VCP-RISK.ParametersSnapshot.ExposureUtilization`

- **Context/group:** RISK
- **Current definition:** Inherited example string; not schema-typed, not an independently defined numeric range.
- **Current unit/range evidence:** Utilization string, example 0.75; denominator/unit and upper bound not explicitly stated.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L426–463](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L426-L463)
- **Candidate:** `DEC_NONNEG` — Unitless exposure/limit ratio, allowed to exceed 1; zero denominator is undefined, never zero-filled.
- **Migration/limits:** Candidate nonnegative exact decimal. Unit, scale, instrument/currency and policy bounds must be identified; no requirement to stop/reject operations is created. Values >1 are retained to represent a breached limit, not clipped to 1.

## N064: `Payload.VCP-RISK.ParametersSnapshot.VaRLimit`

- **Context/group:** RISK
- **Current definition:** Inherited example string; not schema-typed, not an independently defined numeric range.
- **Current unit/range evidence:** Value-at-risk limit; currency, horizon and confidence level missing.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L426–463](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L426-L463)
- **Candidate:** `DEC_NONNEG` — Risk-policy currency amount, horizon/confidence/valuation basis explicitly identified.
- **Migration/limits:** Candidate nonnegative exact decimal. Unit, scale, instrument/currency and policy bounds must be identified; no requirement to stop/reject operations is created.

## N065: `Payload.VCP-RISK.ParametersSnapshot.CurrentVaR`

- **Context/group:** RISK
- **Current definition:** Inherited example string; not schema-typed, not an independently defined numeric range.
- **Current unit/range evidence:** Current value-at-risk; currency, horizon and confidence level missing.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L426–463](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L426-L463)
- **Candidate:** `DEC_NONNEG` — Same amount basis as VaRLimit; sign convention must be reviewed if a legacy model reports negative loss.
- **Migration/limits:** Candidate nonnegative exact decimal. Unit, scale, instrument/currency and policy bounds must be identified; no requirement to stop/reject operations is created.

## N066: `Payload.VCP-RISK.ParametersSnapshot.ThrottleRate`

- **Context/group:** RISK
- **Current definition:** Inherited example string; not schema-typed, not an independently defined numeric range.
- **Current unit/range evidence:** Orders per second (explicit comment).
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L426–463](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L426-L463)
- **Candidate:** `DEC_NONNEG` — Orders per second averaged over the policy window; fractional rate allowed; burst limit specified separately.
- **Migration/limits:** Candidate nonnegative exact decimal. Unit, scale, instrument/currency and policy bounds must be identified; no requirement to stop/reject operations is created. Fractional orders/s allowed as an average rate; burst/window semantics need policy, no integer rounding.

## N067: `Payload.VCP-RISK.TriggeredControls[].TriggerValue`

- **Context/group:** RISK
- **Current definition:** Inherited prose; open risk object.
- **Current unit/range evidence:** Example quantity string; unit/type depend on ControlName.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L451–463](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L451-L463)
- **Candidate:** `TYPED_CONTROL` — Per-control declared type/unit/scale/bounds; no implicit quantity conversion.
- **Migration/limits:** Require a typed control policy; reject unknown semantics for candidate conformance, preserve evidence as unassessed. Not all controls use quantity units.

## N068: `Payload.VCP-RISK.TriggeredControls[].Timestamp`

- **Context/group:** RISK
- **Current definition:** Inherited prose; not schema-typed.
- **Current unit/range evidence:** int64; ns under structured rule.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L451–463](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L451-L463)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** Explicitly retain operation time, distinct from the event capture timestamp; ordering/trust is separate.

## N069: `Payload.VCP-PRIVACY.Pseudonymization.RetentionPeriod`

- **Context/group:** OTHER
- **Current definition:** Inherited prose; not schema-typed.
- **Current unit/range evidence:** ISO 8601 calendar duration string, example P7Y; not a timestamp.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L470–491](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L470-L491)
- **Candidate:** `CALENDAR` — Calendar duration, preserved; range/subset unresolved.
- **Migration/limits:** Preserve calendar representation. A duration containing years/months cannot be mapped to seconds without a start/calendar/policy. Range and lexical subset remain open; no retention/legal requirement changed.

## N070: `SecondaryAnchorConfiguration.Secondary.LastHealthCheck`

- **Context/group:** CONFIG
- **Current definition:** Configuration example, not event/AnchorTarget field.
- **Current unit/range evidence:** Explicit RFC 3339 example string.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [annex L1401–1427](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1401-L1427)
- **Candidate:** `UTC_NS` — UTC date-time with exactly 9 fractional digits; maps exactly to TIME_NS.
- **Migration/limits:** Do not globally convert LastHealthCheck by name: the AnchorTarget field is int64, this configuration field is a date string.

## N071: `SCITTReceipt.payload.tree_size`

- **Context/group:** EXTERNAL
- **Current definition:** Conceptual external COSE receipt; not VCP event schema.
- **Current unit/range evidence:** Example 12345 in conceptual COSE receipt; exact encoding/profile unspecified.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [annex L1003–1018](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1003-L1018)
- **Candidate:** `EXTERNAL_INTEGER` — External service-tree count/index; selected receipt profile controls representation/range.
- **Migration/limits:** Do not change CBOR/service-signed values into VCP decimal strings. Candidate adapter checks exact nonnegative values and index<size under the chosen service profile; limits/mapping remain unresolved.

## N072: `SCITTReceipt.payload.leaf_index`

- **Context/group:** EXTERNAL
- **Current definition:** Conceptual external COSE receipt; not VCP event schema.
- **Current unit/range evidence:** Example 12344; index into service tree, not necessarily VCP batch.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [annex L1003–1018](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/spec/v1.2/VSO-SPEC-CHANGE-001.md#L1003-L1018)
- **Candidate:** `EXTERNAL_INTEGER` — External service-tree count/index; selected receipt profile controls representation/range.
- **Migration/limits:** Do not change CBOR/service-signed values into VCP decimal strings. Candidate adapter checks exact nonnegative values and index<size under the chosen service profile; limits/mapping remain unresolved.

## N073: `LegacyHeader.Timestamp`

- **Context/group:** LEGACY
- **Current definition:** Legacy flat Header example; structured v1.2 requires TimestampInt instead.
- **Current unit/range evidence:** Inherited Int64 epoch ns, but Appendix C illustrates ns/us/ms separately.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L296–324](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L296-L324)
- **Candidate:** `TIME_NS` — Nanoseconds since 1970-01-01T00:00:00Z on the explicitly selected Unix-time convention (no leap-second counting).
- **Migration/limits:** Old aliases/units are not accepted by guessing. Annotate identified legacy interpretation separately; do not rename signed keys.

## N074: `LegacyHeader.EventType`

- **Context/group:** LEGACY
- **Current definition:** Legacy numeric enum; structured schema requires a registered string EventType.
- **Current unit/range evidence:** Int8 event code, example 2; an identifier, not a measured quantity.
- **Presence:** Presence/optionality not fully specified at this path; a future mapping must decide it. No default/null coercion.
- **Text evidence:** [inherited L296–324](https://github.com/veritaschain/vcp-spec/blob/e984d85311f57338065570d7679ddff92718001b/VCP-Specification-v1_0_en.md#L296-L324)
- **Candidate:** `ENUM_CODE` — Registered code; excluded from quantity conversion.
- **Migration/limits:** Explicitly excluded from scalar decimal-string conversion; a separate enum mapping is required. No code/register changes here.
