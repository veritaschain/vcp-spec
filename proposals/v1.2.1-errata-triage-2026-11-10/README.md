# VCP-CP-2026-007 — v1.2.1 errata scope triage

**Status:** Draft, unadopted. Recorded 10 November 2026.
**Baseline:** [`5b042c73adc294e503f07451a18345165341372c`](https://github.com/veritaschain/vcp-spec/tree/5b042c73adc294e503f07451a18345165341372c).
**Proposed class:** P for eligible errata only; no final class or target release is decided.

This is an informative intake of the [v1.2 known issues](../../spec/v1.2/README.md#known-issues-in-v12-informative)
following a source review. The [register](../../decisions/REGISTER.md) assigns
this identifier provisionally. [VCP-PROC-001](../../CHANGE-CONTROL.md) remains a
proposal until [DR-2026-001](../../decisions/VCP-DR-2026-001.md) accepts it.
Merging this draft does not open public review, adopt an erratum or change a
requirement. CP-2026-002's pinned public-review text is not changed here.

## 1. Separation of work

The 10 November documentation follow-up corrects working-branch digest metadata,
records the missing 5 November status-line edit and supplies historical source
links. Those metadata/navigation changes do not repair the technical defects
below. The specifications, annex, schema, existing tags, fixed distributions
and signed records keep their bytes.

PATCH eligibility is conditional: a fix must leave producer hash/signature
bytes and the schema acceptance set unchanged under the proposed procedure.
Adding a required version binding, changing signed coverage, replacing a tree
construction or narrowing schema acceptance cannot be included as P without
checking those byte and acceptance invariants. Each needs its own class, review,
vectors and migration analysis.

## 2. Candidate inventory

The audit labels below are cross-references to the supplied 10 November review,
not adopted erratum or conformance-test identifiers. Repeated claims are grouped;
the source locations remain visible in the known-issue inventory.

| Audit item | Verified observation | Proposed route and remaining evidence |
|---|---|---|
| A-1 | PR #23 changed all three status lines and mirrors; the README's previous digests no longer matched. | Digest/history metadata corrected outside normative files. Specification-internal revision tables remain unchanged; no tagged bytes are replaced. |
| A-2 | §3.2.1's integer/ISO pair disagrees in EN/JA/ZH and the historical v1.1 snapshot. English §6.3.2 has a second mismatch; that section is absent from JA/ZH. | Candidate P example correction once units, schema-field choice and normative precedence are settled. Verify intended instants and portable integer handling; do not modify stored signed events. |
| A-3 | Blanket compatibility claims recur in the summary, §1.3, §10.1, §10.4, §10.5 and Annex §4.3–§4.4. Known field/enum and Merkle-construction divergences contradict blanket assurances. | Candidate P withdrawal of unsupported claims. A replacement compatibility matrix must separate historical verification, future producer migration, schema validity and certification. Depends on CP-002/003/004/006; no automatic conversion of historical evidence. |
| A-4 | §10.3 has elapsed dates; Annex D.2/E contain estimates, dated phases, named deliverables and adoption-population assumptions. | Candidate P clarification/withdrawal of unsupported claims. Require current, attributable evidence before asserting delivered tooling, certification eligibility, counts or regulatory compliance. Set no replacement deadline in this draft. |
| B-1 | Optional Header.SCITTAlignment.Version is hash-covered when present and identifies the VCP version governing alignment semantics; SCITTAlignment is required under VCP_SCITT, not on every base-profile event. Security.Version and PolicyIdentification.Version are free strings outside the Header/Payload hash input. A required, unambiguous version/byte-contract/tree-scheme binding for all events, including authenticated resolution through hashed Header.PolicyID, remains underspecified. | First clarify the roles and limits of existing hashed selectors. Route substantive binding changes to CP-004/006 with M/X assessment; specify trusted configuration or policy resolution, legacy modes, unknown-version behavior and adversarial tests. No downgrade exploit is established by this observation alone. |
| B-2 | Throughput, HSM signing and latency claims lack a reproducible complete pipeline. Annex §6.3 excludes asynchronous signing from the critical path; §6.6 and §8.3 describe different hardware. | Record an unresolved feasibility/measurement question, not impossibility. Require Ed25519-specific support and measurements, signature scope, device/concurrency count, sustained arrival/service rates, queue bounds and p99 methodology. A P-256 number is not Ed25519 evidence. Any move from per-event to root-only signing needs separate normative classification; CP-002 does not supply a benchmark. |
| B-3 | §9.1.2 lists v1.0/v1.1 tests without a v1.2 mapping for RECOVERY and anchor continuity. | Develop a traceable proposed test matrix with fixtures and independently specified expected outcomes. Classify new acceptance criteria separately; existing syntax CI is not a complete certification suite. |
| B-4 | v1.1 has no release tag; current copies include later notices. v1.0's version directory is a navigation page pointing to a root source. | The documentation follow-up adds a commit-pinned v1.1 historical snapshot with computed digests and corrects v1.0 navigation. It creates no tag and does not designate an unreviewed implementation as conforming. Historical data must identify its actual rules, not only a version label. |
| B-5 | §6.3.3 mixes RFC 3161 and qualified status, limits TSA tiers while allowing FreeTSA at Silver, and names a database/SOC 2 example without a cryptographic verification contract. Annex §8.8 mixes anchor frequencies under a Gold heading. | Candidate P terminology/cost clarification where no acceptance rule changes. Determine target classification, qualification evidence and concrete verification mechanisms before changing allowed targets; such changes may need M/X. Do not infer either qualification or cryptographic anchoring from a product name or SOC 2 alone. |
| B-6 | §7.1 attaches MerkleRoot/MerkleIndex/AnchorReference after closing the batch; they lie outside EventHash. | Define captured, signed, batched and externally anchored evidence states and authenticated attachment associations. Relate them to append-only storage without asserting that all event content is mutable until anchoring. Coverage/state changes belong in CP-004/006 with migration review; a README notice does not settle their class. |

## 3. Evidence boundaries

- The timestamp arithmetic is reproducible with integer quotient/remainder and
  the Unix epoch; no floating-point timestamp conversion is needed.
- [SDK interpretations I-1, I-5, I-6 and I-7](https://github.com/veritaschain/vcp-sdk/blob/8eadded87e4f4e46d011835b2ba9a874b91c916d/INTERPRETATIONS.md)
  describe a first-party implementation. Its legacy-tree `INDETERMINATE` result,
  signature coverage and timestamp checks are not adopted protocol decisions.
- [RFC 3161](https://www.rfc-editor.org/rfc/rfc3161.html) defines the protocol;
  [eIDAS Article 42](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02014R0910-20241018)
  has separate qualified-time-stamp requirements. No individual provider's
  legal status is determined here.
- The reviewed annex does not publish the implementation or measurements needed
  to reproduce its Platinum claims. This review runs no HSM benchmark and makes
  no external-vendor throughput claim.
- No full conformance suite, real deployment, new release or certification result
  is produced by this triage. No public-review clock is started or reset here.

## 4. Next decision record

After the procedure and precedence questions are settled, select only eligible
P items for an exact errata text. Record per-artifact before/after digests,
normative effect, implementation/vectors, review evidence and unresolved items.
Separate M/X work before review rather than treating the proposed v1.2.1 name
as an approved classification. Existing release tags and signed data remain
unchanged.
