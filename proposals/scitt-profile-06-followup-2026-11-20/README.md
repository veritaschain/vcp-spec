# SCITT-VCP -06 follow-up: editor candidate and Receipt-context intake

**Status: unsubmitted, unadopted editor candidate.** Prepared 20 November 2026.
The `-07` filename and document identifier are provisional. The published IETF
revision is **-06**, whose document date is 20 November 2026 and whose Datatracker
metadata was updated on 19 November. Merging this directory does not submit an
Internet-Draft or adopt a VCP requirement.

This package gives the editor a complete, reproducible candidate based on the
actual official -06 XML. It corrects the API description and illustrative examples;
Receipt verification context remains an open design question tracked in
[issue #37](https://github.com/veritaschain/vcp-spec/issues/37).

## Review artifacts

| Artifact | Purpose |
|---|---|
| [Candidate XML](draft-kamimura-scitt-vcp-07.xml) | Full proposed source, with an explicit unsubmitted-candidate notice. |
| [Rendered candidate](draft-kamimura-scitt-vcp-07.txt) | Text rendered with xml2rfc 3.35.0 for review. |
| [Preserved -06 XML](source/draft-kamimura-scitt-vcp-06.xml) | Byte-for-byte official source used by the generator. |
| [Manifest](manifest.json) | SHA-256 of the baseline source, saved bibliography and generated XML/JSON. |
| [Render record](rendered-manifest.json) | Pinned renderer version and the exact XML/TXT digests for the reviewed rendering. |
| [Example JSON](examples/) | Header, ORD and ERASURE illustrations with consistent clocks. Hashes, signatures and certificates remain synthetic placeholders. |
| [Receipt context test plan](receipt-context-test-plan.md) | Questions, candidate cases and evidence required before selecting new rules. No test result is asserted for this plan. |

Source baseline: `veritaschain/vcp-spec` commit
`ab5c851ce937763104204d8c4ab09197e16799f1`.
Official -06 XML:
`https://www.ietf.org/archive/id/draft-kamimura-scitt-vcp-06.xml`.
Its SHA-256 is
`58ccf43f176e55d758f49eb21038c4742fa830a4c8d53657c1573e710ac480fe`.
The source retains its original IETF Trust notice. Bibliographic snapshots in
`source/bibxml/` came from the URLs in that official source; their digests are in
the manifest. The candidate embeds those snapshots so generation and rendering
do not silently advance the SCRAPI reference beyond **-11**.

## Proposed changes

| Location in -06 | Problem | Candidate change |
|---|---|---|
| §7.1 | Successful registration was described only as immediately returning a Receipt. | Describe SCRAPI -11's 201/202 paths and the service-provided Receipt `Location`; pending is not completion. |
| §7.2–7.3 | `/entries/{entry_id}` was described as returning the VCP event and `/entries/{entry_id}/receipt` as returning its Receipt; EntryID was said to derive from EventID. | Follow the Receipt `Location` from registration. Explain SCRAPI's 200/204/404 resolution states. Remove both the invented derivation and `/receipt` suffix. Original statement/payload distribution is separate. |
| §7.4 | `GET /anchors/{anchor_id}` was presented inside SCRAPI although §1.2 says no new interactions are defined. | Treat deployment-specific anchor distribution as outside this profile's SCRAPI mapping. |
| §4.1, §6.3, Appendix A | ISO, integer and UUIDv7 times disagree. | Generate exact nanosecond integers and matching UUIDv7 millisecond components. Three length-constrained ERASURE hash placeholders are expanded for structural checking. |
| §8.1 | The text refers to a `ROTATE` event absent from the canonical enum. | Refer to documented deployment key lifecycle management and state that no ROTATE event/protocol is defined. No enum is added. |
| §8.3 | The timestamp comparison did not explain differing units. | Compare UUID time and integer time at millisecond precision; neither is an independent time attestation. |
| Appendix A | A placeholder example was described as complete and ready to wrap. | Label it illustrative, explicitly identifying placeholders and the still-open integer/JCS issue. |
| Acknowledgements | -06 thanks "the members of the VeritasChain Standards Organization Technical Committee". No membership or decision record of such a committee has been published ([known issues](../../spec/v1.2/README.md#known-issues-in-v12-informative), [VCP-DR-2026-001](../../decisions/VCP-DR-2026-001.md)). The published -06 cannot be changed. | Remove that sentence; the acknowledgement of the SCITT Working Group and Certificate Transparency work is kept. Added 21 November 2026. |
| §5.3, note under Table 5 | The note names MiFID II RTS 25 as a clock-synchronisation rule. Delegated Regulation (EU) 2017/574 (RTS 25) was repealed with effect from 2 March 2026 by [Delegated Regulation (EU) 2025/1155](https://eur-lex.europa.eu/eli/reg_del/2025/1155/oj), Article 25 ([known issues](../../spec/v1.2/README.md#known-issues-in-v12-informative)). The published -06 cannot be changed. | Name Delegated Regulation (EU) 2025/1155, Articles 11 to 16, and say that it replaced RTS 25. No tier requirement changes. |
| §9 and change history | References would become stale after the API/example correction. | Update section references and the displayed example integer, preserving all six open questions. Add proposed changes from -06. |

For the ORD example the fixed ISO value is
`2026-03-15T09:30:00.123456789Z`, and the correct integer is
`1773567000123456789`. The previous integer `1742034600123456789` represents
`2025-03-15T10:30:00.123456789Z`; its old UUID represents
`2025-04-10T06:24:48.141Z`. The ERASURE example's old UUID represents
`2026-06-10T01:05:21.920Z`, while its event time is 9 October.
The regression tests exercise those published counterexamples.

These examples preserve integer nanoseconds as used by the released schema.
They **do not settle RFC 8785 representation**, select an EventHash preimage,
define Receipt entry bytes or supply valid cryptographic evidence. The synthetic
target IDs in the ERASURE scope are not a claim about real earlier events.

## Reproduce and inspect

From the repository root:

```sh
python proposals/scitt-profile-06-followup-2026-11-20/generate_candidate.py --check
python proposals/scitt-profile-06-followup-2026-11-20/check_examples.py
python -m unittest discover -s tests -p test_scitt_profile_examples.py -v
python -m unittest discover -s tests -v
```

Run the generator without `--check` to rebuild the XML, example JSON and manifest.
It checks the official source digest, uses exact integer arithmetic and refuses a
SCRAPI bibliography snapshot other than -11. The tests cover the known mismatches,
float/boolean timestamps, wrong UUID version, erasure-time ordering, schema shape,
unchanged rejection of ROTATE and agreement between the XML and JSON artifacts.
Existing contract CI discovers these tests and checks generated-artifact drift.

To render the candidate using the separately pinned documentation tool:

```sh
python -m pip install -r proposals/scitt-profile-06-followup-2026-11-20/requirements-render.txt
xml2rfc proposals/scitt-profile-06-followup-2026-11-20/draft-kamimura-scitt-vcp-07.xml --text --no-network --out proposals/scitt-profile-06-followup-2026-11-20/draft-kamimura-scitt-vcp-07.txt
```

The render record binds the reviewed text to the exact candidate XML. After an
intentional candidate/render update, record both new digests after checking the
render. The regression suite rejects a stale XML or TXT digest in that record.

xml2rfc warns that the inherited source has no `submissionType` and uses its
rendering default. No stream assertion is added to this candidate's XML. That
rendering warning is not evidence of IETF adoption. The document's cover notice
identifies it as unsubmitted.

## Review and publication boundary

This directory and the current-status README edits are informative. The frozen
VCP v1.2 specification, annex, canonical schema, tagged releases and historical
fixtures retain their bytes. No CP identifier, final change class, decision record
or review start is assigned by this package. The proposed procedure and precedence
reviews in [#26](https://github.com/veritaschain/vcp-spec/issues/26) and
[#27](https://github.com/veritaschain/vcp-spec/issues/27) keep their existing clocks.

Before an IETF submission, the editor needs to review the candidate against -06,
confirm the next available revision/date, replace its unsubmitted-candidate notice
with the intended submission note, render it and perform the submission checks.
An actual Datatracker posting must be verified before any page calls -07 current.
Normative VCP changes arising from Receipt-context work require separate review,
classification, vectors and migration analysis under the applicable procedure.

## Sources

- [SCITT-VCP -06](https://www.ietf.org/archive/id/draft-kamimura-scitt-vcp-06.txt), §§4.1, 6.3, 7, 8.1, 8.3, 9 and Appendix A.
- [SCRAPI -11](https://datatracker.ietf.org/doc/html/draft-ietf-scitt-scrapi-11), §§2.3–2.4.
- [RFC 9562 §5.7](https://www.rfc-editor.org/rfc/rfc9562#section-5.7), UUIDv7 millisecond layout.
- [Current VCP known issues](../../spec/v1.2/README.md#known-issues-in-v12-informative) and [proposal register](../../decisions/REGISTER.md).
