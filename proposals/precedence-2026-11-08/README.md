# Normative precedence among VCP artifacts

**Status:** Draft change proposal; **unadopted**. Register entry VCP-CP-2026-002 in [decisions/REGISTER.md](../../decisions/REGISTER.md). Not in effect.
**Date:** 2026-11-08 JST
**Baseline:** vcp-spec [`2dd82e2`](https://github.com/veritaschain/vcp-spec/tree/2dd82e2a70b7f3245ba00e851c991c035649beee); release `v1.2.0` = [`b23acb2`](https://github.com/veritaschain/vcp-spec/tree/b23acb266f88df81d960d36d58fb64ceaa0dd5ed)
**Proposed class:** P (clarification). Reviewers may argue for M; see §5.

## 1. Problem

The published rules settle only two kinds of conflict:

- the normative annex prevails over the specification text (`spec/v1.2/README.md`, Documents table);
- English prevails over the Japanese and Chinese translations (`README.md`; `spec/v1.2/README.md`).

No rule settles conflicts between the specification's normative statements, the JSON Schema and the code examples. Such conflicts exist. For example:

- §6.2.1 states that Merkle construction "MUST follow RFC 6962", while the example builder under it duplicates odd nodes. Its docstring reads "REQUIRED for all VCP implementations".
- §3.1, §3.2 and §8.1.3 use event types (`REJ`, `PRT`, `SNC`, and the inherited v1.0 types `ALG`, `AUD`, `REC`) that the closed v1.2 schema rejects.
- §6.4.1 marks `MerkleRoot`, `MerkleIndex` and `AnchorReference` REQUIRED, while the schema does not.

Without a precedence rule, it cannot be decided whether these are errors in the example, in the schema or in the text. That decides whether each correction is a PATCH or a breaking change.

## 2. Proposed rule

Add to §1 of the specification (and to the Documents table of `spec/vX.Y/README.md`):

> **Precedence.** Where VCP artifacts of the same version conflict, the following order applies, from highest to lowest:
> 1. the normative annex(es) of that version;
> 2. normative statements in the English specification text, meaning statements using the key words of RFC 2119 and RFC 8174 in capitals, together with the definitions they depend on;
> 3. the JSON Schema(s) published in `spec/vX.Y/`;
> 4. code examples, diagrams, tables of examples and other illustrative material, including docstrings such as "REQUIRED for all VCP implementations", which are informative;
> 5. translations.
>
> A conflict is an erratum against the lower-ranked artifact. Schema validity is necessary for conformance only where the text requires it, and it is never sufficient.

## 3. Effect on open items

| Known issue | Effect if adopted |
|---|---|
| §6.2.1 / §6.2.3 Merkle builder and audit-path examples | The examples are informative and conflict with "MUST follow RFC 6962". Correcting them is a PATCH erratum. Data produced by following the old examples must be verified with an explicitly labelled legacy procedure; signed data is never rewritten |
| Quickstart verifier | Already non-normative; corrected together with the above |
| §3.1 / §3.2 event types missing from the schema | The text prevails. Adding the six types to the schema widens what it accepts, so it is class M under the procedure, not a PATCH |
| §6.4.1 REQUIRED fields absent from the schema | The text prevails unless a separate decision moves these requirements to the certification scheme. Either outcome needs its own proposal |
| §3.2.1 `ErrorDetails` example | The example is wrong. The text requirement stands, and the schema needs a location for it (class M) |

## 4. Alternatives considered

- **Schema prevails over the text.** This gives a machine-checkable rule. But it would turn the event types, field requirements and the RFC 6962 requirement into errors in the text, and would require removing requirements the specification states. It is rejected because it reverses the existing statement "Schema validity is not conformance" in the Known issues.
- **No general rule, decided case by case.** This leaves every conflict open to the same question and keeps the classification of each repair arbitrary.

## 5. Compatibility

The rule changes no hash, signature, schema or wire format. Its consequence is that some existing examples become errata, and implementations that copied them diverge from the normative text.

The repository README reports zero external implementations as of 25 October 2026. First-party v1.1 reference implementations and their archived evidence are affected. They keep their original bytes and need a labelled legacy verification path.

Reviewers who consider that the rule itself changes the effective requirements may argue for class M, which brings a 30-day review.

## 6. Not decided here

This proposal does not adopt the Merkle repair, the AnchorRecord statement signature, the numeric representation or any field relocation. Those remain separate proposals.
