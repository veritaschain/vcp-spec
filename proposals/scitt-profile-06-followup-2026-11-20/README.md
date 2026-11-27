# SCITT-VCP -06 follow-up: source of the posted -07 and Receipt-context intake

**Status: posted.** [`draft-kamimura-scitt-vcp-07`](https://datatracker.ietf.org/doc/html/draft-kamimura-scitt-vcp-07)
was posted to the IETF Datatracker on 24 November 2026 (submission 173128;
document record dated 2026-11-24T02:34:46Z; document date 24 November 2026;
expires 28 May 2027; 38 pages). It is an individual Internet-Draft, not adopted
by any IETF Working Group. The XML and text in this directory are byte-identical
to the [archived XML](https://www.ietf.org/archive/id/draft-kamimura-scitt-vcp-07.xml)
and [archived text](https://www.ietf.org/archive/id/draft-kamimura-scitt-vcp-07.txt)
(SHA-256 `078e1ac6c3dcbd9c0d2930655443e4729dce373da68bbb05f6e76b1f117e2bd3` and
`9c96f008cfef43173947ade282277642fee974c8492e6a70e37cb600a7c600df`). A posted
revision cannot be withdrawn or edited; corrections go into a later revision.
Posting adopts no VCP requirement.

The package is reproducible from the actual official -06 XML. It began on
20 November 2026 as an editor candidate; the candidate notice was removed and the
date set on 24 November. It corrects the API description and illustrative
examples and settles the log position and size part of Open Issue 6. The entry
rule and the trusted service and keys remain open design questions tracked in
[issue #37](https://github.com/veritaschain/vcp-spec/issues/37), which the draft
now cites.

## Review artifacts

| Artifact | Purpose |
|---|---|
| [Posted XML](draft-kamimura-scitt-vcp-07.xml) | Full source as posted. The generator refuses to produce different bytes. |
| [Rendered text](draft-kamimura-scitt-vcp-07.txt) | Text rendered with xml2rfc 3.35.0. It matches the text the Datatracker rendered from the XML. |
| [Preserved -06 XML](source/draft-kamimura-scitt-vcp-06.xml) | Byte-for-byte official source used by the generator. |
| [Manifest](manifest.json) | SHA-256 of the baseline source, saved bibliography and generated XML/JSON. |
| [Render record](rendered-manifest.json) | Pinned renderer version and the exact XML/TXT digests for the reviewed rendering. |
| [Example JSON](examples/) | Header, ORD and ERASURE illustrations with consistent clocks. Hashes, signatures and certificates remain synthetic placeholders. |
| [Receipt context test plan](receipt-context-test-plan.md) | Questions, candidate cases and evidence required before selecting new rules, and inputs received from the SCITT list. No Receipt test result is asserted for this plan. |
| [Position check](receipt_position_check.py) | First-party RFC 9162 tree arithmetic behind the tree-size result reported on the SCITT list; regression in `tests/test_scitt_receipt_position.py`. Not a Receipt implementation. |
| [Receipt context candidate, 25 November](../scitt-receipt-context-2026-11-25/README.md) | Unadopted entry-byte, service/key and historical-applicability alternatives responding to the later 24 November reply; includes a 22-case matrix and a first-party replay of seven cases. |

Source baseline: `veritaschain/vcp-spec` commit
`ab5c851ce937763104204d8c4ab09197e16799f1`.
Official -06 XML:
`https://www.ietf.org/archive/id/draft-kamimura-scitt-vcp-06.xml`.
Its SHA-256 is
`58ccf43f176e55d758f49eb21038c4742fa830a4c8d53657c1573e710ac480fe`.
The source retains its original IETF Trust notice. Bibliographic snapshots in
`source/bibxml/` came from the URLs in that official source; their digests are in
the manifest. The XML embeds those snapshots so generation and rendering
do not silently advance the SCRAPI reference beyond **-11**. On 24 November 2026
the Datatracker still listed SCRAPI -11 (RFC Editor queue) and CCF profile -06
(IESG Evaluation) as the latest revisions.

## Changes from -06

| Location in -06 | Problem | Change in -07 |
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
| §9 and change history | References would become stale after the API/example correction. | Update section references and the displayed example integer. Add proposed changes from -06. |
| §8.5, §9 items 2 and 6 | -06 left open (item 6(c)) what a verifier checks when an argument depends on log position or size, although -06 rests no claim on either. On the SCITT list ([24 November 2026](https://mailarchive.ietf.org/arch/msg/scitt/nQPyS-vfZfywHe9_TcqcrgY5Tw4/)) it was shown that an RFC9162_SHA256 Receipt of inclusion establishes neither. | §8.5 states that the profile relies on Receipts for inclusion only. Item 6 keeps (a) the entry rule, with the CCF profile's rule recorded as a candidate, and (b) the trusted service and keys. Item 2 notes that §8.5 relies on the AnchorRecord fields its signature does not cover. No VCP requirement changes. Added 24 November 2026. |
| §9 item 6, references | The intake record for the remaining parts of item 6 ([issue #37](https://github.com/veritaschain/vcp-spec/issues/37)) was not cited, and its fourth question (what follows when the needed context is absent, unknown or contradictory) was not recorded in the draft. | Item 6 states that the profile does not yet say what a verifier reports in that case, and cites the issue as an intake record that adopts no change. §8.5 cites the list message for the tree-size observation. Added 24 November 2026. |
| Front note, §9, Appendix C | The candidate notice, the provisional -07 label and the "this candidate" wording described an unsubmitted file. | Removed the notice; the document date is 24 November 2026 and the text says "this revision". Added 24 November 2026. |
| Acknowledgements | The comments that led to the §8.5 and item 6 changes were cited but not acknowledged. | Acknowledge Bassem Kudsi's comments on the SCITT list, with a statement that this does not imply endorsement. The name is as signed in his [15 November 2026 message](https://mailarchive.ietf.org/arch/msg/scitt/sKNL7T_CRu1YX-_rLPRYnyRcixg/). Added 24 November 2026. |

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
The document date is the `DOC_DATE` constant in the generator. The generator
compares its XML with the digest of the posted revision and fails on any
difference.
It checks the official source digest, uses exact integer arithmetic and refuses a
SCRAPI bibliography snapshot other than -11. The tests cover the known mismatches,
float/boolean timestamps, wrong UUID version, erasure-time ordering, schema shape,
unchanged rejection of ROTATE and agreement between the XML and JSON artifacts.
Existing contract CI discovers these tests and checks generated-artifact drift.

To render the text using the separately pinned documentation tool:

```sh
python -m pip install -r proposals/scitt-profile-06-followup-2026-11-20/requirements-render.txt
xml2rfc proposals/scitt-profile-06-followup-2026-11-20/draft-kamimura-scitt-vcp-07.xml --text --no-network --out proposals/scitt-profile-06-followup-2026-11-20/draft-kamimura-scitt-vcp-07.txt
```

The render record binds the reviewed text to the exact XML. After an intentional
update, record both new digests after checking the render. The regression suite
rejects a stale XML or TXT digest in that record, and a candidate notice or a
document date that differs from `DOC_DATE`.

xml2rfc warns that the inherited source has no `submissionType` and uses its
rendering default, as it did for -06. No stream assertion is added to the XML.
That rendering warning is not evidence of IETF adoption.

Submission checks on the rendered text, 24 November 2026 (idnits 2.17.1 through
the IETF author-tools service): submission-check mode reported no nits; the full
check reported 0 errors, 0 flaws, 1 warning (three lines with FQDNs outside the
RFC 2606 example names) and 1 comment (the informative reference to RFC 6962,
which RFC 9162 obsoletes). The same warning and comment are reported for the
earlier candidate text on `main`.

## Review and publication boundary

This directory and the current-status README edits are informative. The frozen
VCP v1.2 specification, annex, canonical schema, tagged releases and historical
fixtures retain their bytes. No CP identifier, final change class, decision record
or review start is assigned by this package. The proposed procedure and precedence
reviews in [#26](https://github.com/veritaschain/vcp-spec/issues/26) and
[#27](https://github.com/veritaschain/vcp-spec/issues/27) keep their existing clocks.

The steps listed here before 24 November are done: the text was reviewed against
-06, -07 was confirmed as the next revision (the Datatracker listed 00 to 06), the
candidate notice was removed, the date was set, the text was rendered and
checked, the XML was uploaded, and the author confirmed the posting. The posting
was verified against the Datatracker document record and the archived files
before this page called -07 current.
Normative VCP changes arising from Receipt-context work require separate review,
classification, vectors and migration analysis under the applicable procedure.

## Sources

- [SCITT-VCP -06](https://www.ietf.org/archive/id/draft-kamimura-scitt-vcp-06.txt), §§4.1, 6.3, 7, 8.1, 8.3, 9 and Appendix A.
- [SCRAPI -11](https://datatracker.ietf.org/doc/html/draft-ietf-scitt-scrapi-11), §§2.3–2.4.
- [RFC 9562 §5.7](https://www.rfc-editor.org/rfc/rfc9562#section-5.7), UUIDv7 millisecond layout.
- [Current VCP known issues](../../spec/v1.2/README.md#known-issues-in-v12-informative) and [proposal register](../../decisions/REGISTER.md).
