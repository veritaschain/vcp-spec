#!/usr/bin/env python3
"""Rebuild draft-kamimura-scitt-vcp-07 from the preserved official -06 XML.

The output is byte-identical to the XML posted to the IETF Datatracker on
24 November 2026 (submission 173128); the build fails if it is not. A posted
revision cannot be changed, so later corrections belong in a new revision, not
here. This generates documentation examples, not signed evidence or a
conformance implementation. All integer arithmetic is exact; no JCS choice is
made here.
"""

import argparse
import hashlib
import json
import re
import uuid
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
BASE_NAME = "draft-kamimura-scitt-vcp-06.xml"
CANDIDATE_NAME = "draft-kamimura-scitt-vcp-07.xml"
BASE_SHA256 = "58ccf43f176e55d758f49eb21038c4742fa830a4c8d53657c1573e710ac480fe"
# Document date of the posted revision.
DOC_DATE = (2026, "November", 24)
# SHA-256 of https://www.ietf.org/archive/id/draft-kamimura-scitt-vcp-07.xml,
# fetched after posting on 24 November 2026.
POSTED_XML_SHA256 = "078e1ac6c3dcbd9c0d2930655443e4729dce373da68bbb05f6e76b1f117e2bd3"
POSTED_URL = "https://www.ietf.org/archive/id/" + CANDIDATE_NAME
ORDER_NS = 1773567000123456789  # 2026-03-15T09:30:00.123456789Z
ERASURE_NS = 1791504000000000000  # 2026-10-09T00:00:00Z

SCRAPI = '''    <section anchor="scrapi-integration">
      <name>SCRAPI Integration</name>

      <t>VCP Transparency Services MUST implement SCRAPI
      <xref target="I-D.ietf-scitt-scrapi"/>. The descriptions below follow
      revision -11 of that API; they do not define alternative SCRAPI
      resources.</t>

      <section anchor="scrapi-registration">
        <name>Registration (POST /entries)</name>
        <t>A client submits a COSE_Sign1 Signed Statement carrying the VCP
        event to the registration resource defined in Section 2.3 of
        <xref target="I-D.ietf-scitt-scrapi"/>. The Transparency Service
        applies its Registration Policy before further processing.</t>
        <sourcecode type="http"><![CDATA[
POST /entries HTTP/1.1
Host: vcp-ts.example.com
Accept: application/cbor
Accept: application/cose
Content-Type: application/cose

<COSE_Sign1 containing VCP Event payload>
        ]]></sourcecode>
        <t>A successful synchronous registration returns the Receipt in
        a 201 response. An accepted asynchronous registration returns 202
        while the Receipt is pending. In both cases the Location header
        identifies the Receipt resource. A 202 response is not evidence
        that registration is complete or that a Receipt has been issued.</t>
      </section>

      <section anchor="scrapi-retrieval">
        <name>Receipt Resolution (GET the Location URL)</name>
        <t>The client follows the Location URL returned by registration,
        for example /entries/{EntryID}, as defined in Section 2.4 of
        <xref target="I-D.ietf-scitt-scrapi"/>. This resource returns a
        Receipt, not the original VCP event. A 200 response carries the
        COSE Receipt; 204 indicates that registration is still pending;
        404 indicates that no Receipt exists, including a failed
        registration. Polling and error handling follow SCRAPI.</t>
        <t>This profile defines no derivation of EntryID from
        Header.EventID. The client uses the service-provided Location
        instead of synthesizing a Receipt URL from an event identifier.</t>
      </section>

      <section anchor="scrapi-receipt">
        <name>Receipt Verification and Statement Availability</name>
        <t>The Receipt resource is the Location URL described above;
        this profile does not append a /receipt suffix. Obtaining a
        Receipt is separate from verifying it against the candidate
        Signed Statement and the trusted service context. The unresolved
        context questions are recorded in <xref target="open-issues"/>,
        item 6.</t>
        <t>The original Signed Statement and any detached payload are
        supplied to a verifier through the applicable evidence-distribution
        or artifact-repository mechanism. The SCRAPI Receipt resource
        does not provide an event-download API.</t>
      </section>

      <section anchor="scrapi-anchor">
        <name>External Anchor Information</name>
        <t>External anchor evidence, such as a blockchain reference or
        timestamp token, is made available through the deployment's
        documented evidence-distribution mechanism. This profile does
        not define GET /anchors/{anchor_id} as a SCRAPI resource.
        A deployment-specific anchor-status API is outside this profile;
        its response is not by itself verification of the anchor.</t>
      </section>
    </section>'''

CHANGES = '''    <section anchor="appendix-changes-06">
      <name>Changes from draft-kamimura-scitt-vcp-06</name>
      <ul>
        <li>Corrected the SCRAPI description to match the cited revision
        -11: service-provided Receipt Location, synchronous and asynchronous
        registration, and Receipt resolution without a /receipt suffix.</li>
        <li>Removed the unsupported EventID-to-EntryID derivation and the
        description of an anchor-status endpoint as part of SCRAPI.</li>
        <li>Made the Header and ERASURE example timestamps and UUIDv7
        millisecond timestamps consistent. Marked the Appendix A hashes as
        illustrative placeholders; the integer/JCS issue remains open.</li>
        <li>Removed the reference to an undefined ROTATE event. No event
        type or key-rotation protocol is introduced.</li>
        <li>Removed the acknowledgement of a VeritasChain Standards
        Organization Technical Committee. No membership or decision
        record of such a committee has been published.</li>
        <li>Named the regulation that replaced MiFID II RTS 25 in the
        Silver tier note. Commission Delegated Regulation (EU) 2017/574
        (RTS 25) was repealed with effect from 2 March 2026; business-clock
        synchronisation is set by Commission Delegated Regulation (EU)
        2025/1155, Articles 11 to 16. No tier requirement changes.</li>
        <li>Stated in the Completeness Considerations that this profile
        relies on Receipts for inclusion only and draws no conclusion from
        the tree size or leaf index a Receipt carries. This settles the
        part of Open Issue 6 on log position and size. No VCP requirement
        changes; -06 already rested no claim on them.</li>
        <li>Narrowed Open Issue 6 to the entry rule and the trusted service
        and keys, and recorded the CCF profile's entry rule as a candidate
        under discussion on the SCITT list.</li>
        <li>Noted in Open Issue 2 that the Completeness Considerations rely
        on the AnchorRecord fields its signature does not cover.</li>
        <li>Recorded in Open Issue 6 that the profile does not yet state
        what a verifier reports when the entry rule or the trusted service
        and keys are missing, unknown or contradictory, and added a
        reference to the intake record that tracks the remaining parts of
        item 6.</li>
        <li>Acknowledged the SCITT list comments that led to the changes to
        the Completeness Considerations and Open Issue 6.</li>
        <li>Items 1 to 5 and the remaining parts of item 6 stay open.
        This revision does not adopt any VSO change proposal or change
        the VCP v1.2 specification, schema or existing signed records.</li>
      </ul>
    </section>

'''

COMPLETENESS_RECEIPTS = '''        frequency should be disclosed when records are presented.</t>
        <t>This profile relies on COSE Receipts <xref target="RFC9942"/>
        for inclusion only. It draws no conclusion about a Signed
        Statement's position in a Transparency Service's log, or about the
        log's size, from the tree size or leaf index that a Receipt
        carries, and none of the mechanisms above depends on them. For
        RFC9162_SHA256 a Receipt of inclusion establishes neither: the tree
        size and leaf index are outside the signed protected header, and
        the same inclusion path can recompute the signed root under more
        than one tree size <xref target="SCITT-LIST-OI6"/>. VCP takes the
        order of events from their sequence numbers; Relying Parties
        cannot assume that log order matches issuance order unless the
        Registration Policy advertises it (Section 9.1 of
        <xref target="RFC9943"/>). The AnchorRecord
        fields listed above are not yet covered by the AnchorRecord
        signature; see item 2 of <xref target="open-issues"/>.</t>
      </section>'''

OPEN_ISSUE_6_REST = '''This
        profile does not yet state (a) which bytes form the entry for a
        registered VCP Signed Statement and how a verifier learns that rule
        for a given Transparency Service, or (b) which Transparency Service
        a verifier is expected to trust and how it obtains the Receipt
        verification keys that service used, including those for earlier
        Receipts. Section 4 of <xref target="RFC9943"/> allows the key to
        change between Receipts, and key discovery (Section 2.1 of
        <xref target="I-D.ietf-scitt-scrapi"/>) does not by itself decide
        which service is trusted. For (a), the entry rule of the CCF
        profile <xref target="CCF-PROFILE"/> (Sections 2.2 and 3.2: the
        Signed Statement as registered, with tag 18 retained and an empty
        unprotected header, its digest computed by the verifier) is a
        candidate under discussion <xref target="SCITT-LIST-OI6"/>. Under
        RFC9162_SHA256 the vds value in the protected header does not
        identify an entry rule, so a rule stated by this profile would be
        fixed together with the service identity in (b) rather than
        selected by the Receipt. Revision -06 also left open (c), what a
        verifier checks when an argument depends on a statement's position
        in the log or on the log's size. This revision settles (c) by
        stating in <xref target="security-completeness"/> that the profile
        relies on Receipts for inclusion only. A future claim resting on
        position or size would need further evidence under the trusted
        service key, such as a signed checkpoint whose root equals the one
        recomputed from the Receipt, together with every entry in the range
        and consistency between the tree heads compared. This profile
        also does not yet state what a verifier reports when the context
        in (a) or (b) is missing, unknown or contradictory. Parts (a) and
        (b) are tracked in an intake record <xref target="VCP-ISSUE-37"/>;
        it adopts no change. The hackathon
        report presented to the SCITT Working Group at IETF 127 names the
        same points as rules that verifying Receipts across operators
        currently needs out of band <xref target="SCITT-IETF127"/>.</li>'''

NEW_REFERENCES = '''        <reference anchor="CCF-PROFILE" target="https://datatracker.ietf.org/doc/html/draft-ietf-scitt-receipts-ccf-profile-06">
          <front>
            <title>CCF Profile for COSE Receipts</title>
            <author initials="H." surname="Birkholz" fullname="Henk Birkholz"/>
            <author initials="A." surname="Delignat-Lavaud" fullname="Antoine Delignat-Lavaud"/>
            <author initials="C." surname="Fournet" fullname="Cedric Fournet"/>
            <author initials="A." surname="Chamayou" fullname="Amaury Chamayou"/>
            <date day="22" month="October" year="2026"/>
          </front>
          <seriesInfo name="Internet-Draft" value="draft-ietf-scitt-receipts-ccf-profile-06"/>
        </reference>

        <reference anchor="SCITT-LIST-OI6" target="https://mailarchive.ietf.org/arch/msg/scitt/nQPyS-vfZfywHe9_TcqcrgY5Tw4/">
          <front>
            <title>Re: draft-kamimura-scitt-vcp-06: open issue on what a verifier needs besides the Receipt</title>
            <author initials="B." surname="Kudsi" fullname="Bassem Kudsi">
              <organization>AugmentEV</organization>
            </author>
            <date day="24" month="November" year="2026"/>
          </front>
          <annotation>Message to the SCITT Working Group mailing list.</annotation>
        </reference>

        <reference anchor="VCP-ISSUE-37" target="https://github.com/veritaschain/vcp-spec/issues/37">
          <front>
            <title>SCITT -06 Receipt verification context and interoperability plan</title>
            <author>
              <organization>VeritasChain Standards Organization</organization>
            </author>
            <date month="November" year="2026"/>
          </front>
          <annotation>Issue 37 in the vcp-spec repository. Intake record; no change is adopted.</annotation>
        </reference>

        <reference anchor="SCITT-IETF127"'''


def replace_between(text, start_marker, end_marker, new):
    if text.count(start_marker) != 1 or text.count(end_marker) != 1:
        raise ValueError("baseline text changed: " + start_marker[:60])
    start = text.index(start_marker)
    end = text.index(end_marker, start) + len(end_marker)
    return text[:start] + new + text[end:]


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("baseline text changed: " + old[:80])
    return text.replace(old, new, 1)


def section_span(text, anchor):
    match = re.search(r'(?m)^([ ]*)<section anchor="' + re.escape(anchor) + r'"[^>]*>', text)
    if match is None:
        raise ValueError("missing section: " + anchor)
    depth = 0
    for token in re.finditer(r'</?section\b[^>]*>', text[match.start():]):
        depth += -1 if token.group().startswith("</") else 1
        if depth == 0:
            return match.start(), match.start() + token.end()
    raise ValueError("unclosed section: " + anchor)


def section(text, anchor):
    start, end = section_span(text, anchor)
    return text[start:end]


def replace_section(text, anchor, replacement):
    start, end = section_span(text, anchor)
    return text[:start] + replacement + text[end:]


def uuid7_at(ns, suffix):
    # Deterministic documentation ID, not a production UUID generator.
    return str(uuid.UUID(int=((ns // 1_000_000) << 80) | (7 << 76) | (2 << 62) | suffix))


def json_example(tree, anchor):
    node = tree.find(".//section[@anchor='" + anchor + "']/sourcecode[@type='json']")
    return json.loads(node.text)


def json_text(value):
    # Keep JSON valid while fitting string literals within RFC text width.
    lines = []
    for line in json.dumps(value, indent=2).splitlines():
        match = re.fullmatch(r'(\s*"[^"\\]+":) ("[^"\\]*"[,]?)', line)
        if len(line) > 70 and match:
            lines.extend((match[1], "  " + match[2]))
        else:
            lines.append(line)
    return "\n".join(lines) + "\n"


def insert_json(text, anchor, value):
    original = section(text, anchor)
    start = original.index('<sourcecode type="json"><![CDATA[') + len('<sourcecode type="json"><![CDATA[')
    end = original.index(']]></sourcecode>', start)
    updated = original[:start] + "\n" + json_text(value) + original[end:]
    return replace_section(text, anchor, updated)


def build():
    raw = (ROOT / "source" / BASE_NAME).read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASE_SHA256:
        raise ValueError("official -06 XML hash does not match the reviewed baseline")
    original = raw.decode("utf-8")
    tree = ET.fromstring(original)
    examples = {name: json_example(tree, anchor) for name, anchor in (
        ("header", "schema-header"), ("order", "appendix-example"), ("erasure", "erasure-event"))}
    for name in ("header", "order"):
        examples[name]["Header"]["TimestampInt"] = ORDER_NS
        examples[name]["Header"]["EventID"] = uuid7_at(ORDER_NS, 0x123456789ABC)
    examples["erasure"]["Header"]["EventID"] = uuid7_at(ERASURE_NS, 1)
    # Expand only length-constrained placeholders for schema-shape checks.
    # They remain synthetic, not computed hashes or destruction evidence.
    details = examples["erasure"]["Payload"]["VCP-PRIVACY"]["ErasureDetails"]
    details["TargetIdentifier"]["Hash"] = "b" * 64
    details["Reason"]["RequestReferenceHash"] = "c" * 64
    details["CryptoShredding"]["KeyIDHash"] = "d" * 64

    candidate = original
    candidate = replace_once(candidate, 'docName="draft-kamimura-scitt-vcp-06"',
                             'docName="draft-kamimura-scitt-vcp-07"')
    candidate = replace_once(candidate, 'value="draft-kamimura-scitt-vcp-06"',
                             'value="draft-kamimura-scitt-vcp-07"')
    candidate = replace_once(candidate, '  Internet-Draft: draft-kamimura-scitt-vcp-06',
                             '  Internet-Draft: draft-kamimura-scitt-vcp-07')
    candidate = replace_once(candidate, '<date year="2026" month="November" day="20"/>',
                             '<date year="%d" month="%s" day="%d"/>' % DOC_DATE)
    candidate = replace_once(candidate,
        '  Changes from -05: see Appendix "Changes from draft-kamimura-scitt-vcp-05".',
        '  Changes from -06: see Appendix "Changes from draft-kamimura-scitt-vcp-06".')
    start = candidate.index('      <t>Changes from -05 are listed in')
    end = candidate.index('</t>', start) + 4
    candidate = candidate[:start] + '''      <t>Changes from -06 are listed in
      <xref target="appendix-changes-06"/>. The SCRAPI description and
      examples are corrected, and the part of Open Issue 6 on log position
      and size is settled by relying on Receipts for inclusion only. Items
      1 to 5 and the rest of item 6 remain unresolved. Earlier changes are
      recorded in the subsequent appendices.</t>''' + candidate[end:]
    candidate = replace_section(candidate, "scrapi-integration", SCRAPI)
    candidate = replace_once(candidate,
        '<li>Key rotation with explicit ROTATE events</li>',
        '''<li>Key lifecycle management under the deployment's documented
          policy. This profile does not define a ROTATE event or a
          key-rotation protocol.</li>''')
    candidate = replace_once(candidate,
        '<li>UUID v7 provides embedded timestamp that must match TimestampInt</li>',
        '''<li>Compare the UUID v7 millisecond timestamp with TimestampInt
          at millisecond precision. Neither producer-supplied value is an
          independent attestation of the event time.</li>''')
    candidate = replace_once(candidate,
        '      Item 6 is added in this revision.  None of them is resolved by this\n      revision.',
        '      Item 6 was added in revision -06. This revision settles its part\n      on log position and size and leaves its other parts open; items 1\n      to 5 are not resolved by this revision.')
    candidate = replace_once(candidate,
        '        <li>Receipt verification context.  <xref target="scrapi-receipt"/>\n        describes a Receipt as containing the Merkle inclusion proof, and\n        <xref target="security-completeness"/> builds on inclusion.  For the',
        '        <li>Receipt verification context. Receipt resolution in\n        <xref target="scrapi-retrieval"/> is separate from verification;\n        <xref target="security-completeness"/> builds on inclusion. For the')
    # Open Issue 6 after the SCITT list reply of 24 November 2026: part (c)
    # is settled by relying on Receipts for inclusion only (Section 8.5);
    # (a) and (b) stay open, with the CCF entry rule recorded as a candidate.
    candidate = replace_between(candidate,
        'This\n        profile does not yet state (a) which bytes form the entry for a',
        'currently needs out of band <xref target="SCITT-IETF127"/>.</li>',
        OPEN_ISSUE_6_REST)
    candidate = replace_once(candidate,
        '        signature.  The signed bytes of the AnchorRecord remain to be\n        defined.</li>',
        '''        signature.  The signed bytes of the AnchorRecord remain to be
        defined. <xref target="security-completeness"/> relies on these
        fields for omission detection after anchoring. One direction under
        consideration is to register the AnchorRecord itself as a Signed
        Statement whose payload carries them, so that the Issuer's
        signature covers them; it is not adopted.</li>''')
    candidate = replace_once(candidate,
        '        frequency should be disclosed when records are presented.</t>\n      </section>',
        COMPLETENESS_RECEIPTS)
    candidate = replace_once(candidate, '        <reference anchor="SCITT-IETF127"', NEW_REFERENCES)
    candidate = replace_once(candidate, '        1742034600123456789 in <xref target="appendix-example"/>, cannot be',
        '        1773567000123456789 in <xref target="appendix-example"/>, cannot be')
    candidate = replace_once(candidate, '<name>Complete VCP Event Example</name>',
        '<name>Illustrative VCP Event Example</name>')
    candidate = replace_once(candidate,
        '      <t>The following is a complete VCP v1.2 Event encoded as JSON, ready\n      to be wrapped in a COSE_Sign1 Signed Statement:</t>',
        '''      <t>The following JSON illustrates the VCP v1.2 event structure
      before COSE_Sign1 wrapping. Hashes are placeholders: this is not a
      signature, Receipt or conformance test vector. The integer
      canonicalization issue in <xref target="open-issues"/> remains
      unresolved.</t>''')
    for name, anchor in (("header", "schema-header"), ("order", "appendix-example"), ("erasure", "erasure-event")):
        candidate = insert_json(candidate, anchor, examples[name])
    # No Technical Committee membership or decision record has been published
    # (spec/v1.2/README.md known issues; decisions/VCP-DR-2026-001.md).
    candidate = replace_once(candidate,
        '''      <t>The authors thank the members of the VeritasChain Standards
      Organization Technical Committee for their contributions to
      this specification. This work builds upon the SCITT architecture''',
        '''      <t>This work builds upon the SCITT architecture''')
    # Comments on the SCITT list, 24 November 2026 (issue #37).
    candidate = replace_once(candidate,
        '''      on draft-kamimura-scitt-vcp-01, which informed the improvements in
      this version.</t>''',
        '''      on draft-kamimura-scitt-vcp-01, which informed the improvements in
      this version.</t>
      <t>The changes to the Completeness Considerations and to Open
      Issue 6 in revision -07 follow comments by Bassem Kudsi on the SCITT
      mailing list <xref target="SCITT-LIST-OI6"/>. This acknowledgement
      does not imply endorsement of this profile.</t>''')
    # RTS 25 (Delegated Regulation (EU) 2017/574) was repealed from 2 March
    # 2026 by Delegated Regulation (EU) 2025/1155, Article 25. The published
    # -06 cannot be changed (spec/v1.2/README.md known issues).
    candidate = replace_once(candidate,
        '''        trading systems subject to MiFID II RTS 25, SEC Rule 17a-4, or
        equivalent clock synchronization requirements. Silver tier is''',
        '''        trading systems subject to the EU business-clock synchronisation
        rules (Commission Delegated Regulation (EU) 2025/1155, Articles 11
        to 16, which replaced MiFID II RTS 25 on 2 March 2026), SEC Rule
        17a-4, or equivalent clock synchronization requirements. Silver
        tier is''')
    candidate = replace_once(candidate, '    <section anchor="appendix-changes-05">',
        CHANGES + '    <section anchor="appendix-changes-05">')

    # Resolve the exact saved bibliographic snapshots, without network access.
    source_digests = {"source/" + BASE_NAME: BASE_SHA256}
    for match in list(re.finditer(r'<xi:include href="([^"]+)"/>', candidate)):
        name = match.group(1).rsplit("/", 1)[1]
        path = ROOT / "source" / "bibxml" / name
        data = path.read_bytes()
        element = ET.fromstring(data)
        if name == "reference.I-D.ietf-scitt-scrapi.xml":
            values = [s.get("value") for s in element.findall("seriesInfo")]
            if "draft-ietf-scitt-scrapi-11" not in values:
                raise ValueError("SCRAPI snapshot is not revision -11")
        candidate = candidate.replace(match.group(0), ET.tostring(element, encoding="unicode"), 1)
        source_digests[path.relative_to(ROOT).as_posix()] = hashlib.sha256(data).hexdigest()
    ET.fromstring(candidate)
    if hashlib.sha256(candidate.encode()).hexdigest() != POSTED_XML_SHA256:
        raise ValueError("generated XML differs from the posted -07 revision")
    outputs = {CANDIDATE_NAME: candidate}
    outputs.update({"examples/" + name + ".json": json_text(value)
                    for name, value in examples.items()})
    manifest = {
        "status": "posted as draft-kamimura-scitt-vcp-07 on 24 November 2026 (Datatracker submission 173128); the generated XML is byte-identical to the archived revision; no VCP change adopted",
        "posted_url": POSTED_URL,
        "baseline_repository_commit": "ab5c851ce937763104204d8c4ab09197e16799f1",
        "baseline_url": "https://www.ietf.org/archive/id/" + BASE_NAME,
        "source_sha256": source_digests,
        "generated_sha256": {name: hashlib.sha256(value.encode()).hexdigest() for name, value in outputs.items()},
        "scope": "Documentation, HTTP mapping and example clock consistency only; no cryptographic conformance claim",
    }
    outputs["manifest.json"] = json.dumps(manifest, indent=2) + "\n"
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated files differ")
    args = parser.parse_args()
    outputs = build()
    for name, text in outputs.items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_bytes() != text.encode():
                raise SystemExit("generated artifact mismatch: " + name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode())
    print(("Checked" if args.check else "Generated") + f" {len(outputs)} artifacts; no protocol validation performed.")


if __name__ == "__main__":
    main()
