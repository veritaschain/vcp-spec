#!/usr/bin/env python3
"""Rebuild an unsubmitted I-D candidate from the preserved official -06 XML.

This generates documentation examples, not signed evidence or a conformance
implementation. All integer arithmetic is exact; no JCS choice is made here.
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
        <li>All six integrity and Receipt-context issues remain open.
        This candidate does not adopt any VSO change proposal or change
        the VCP v1.2 specification, schema or existing signed records.</li>
      </ul>
    </section>

'''


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
                             '  Unsubmitted editor candidate: draft-kamimura-scitt-vcp-07')
    candidate = replace_once(candidate,
        '  Changes from -05: see Appendix "Changes from draft-kamimura-scitt-vcp-05".',
        '  Changes from -06: see Appendix "Changes from draft-kamimura-scitt-vcp-06".')
    candidate = replace_once(candidate, '      <name>About This Document</name>',
        '''      <name>About This Document</name>
      <t>This is an unsubmitted editor's candidate for discussion. The -07
      identifier is provisional. The published revision is -06; this file
      is not evidence of a new IETF submission, VSO adoption or an
      implementation-conformance result.</t>''')
    start = candidate.index('      <t>Changes from -05 are listed in')
    end = candidate.index('</t>', start) + 4
    candidate = candidate[:start] + '''      <t>Proposed changes from -06 are listed in
      <xref target="appendix-changes-06"/>. The SCRAPI description and
      examples are corrected; the six Open Issues remain unresolved.
      Earlier changes are recorded in the subsequent appendices.</t>''' + candidate[end:]
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
        '      Item 6 was added in revision -06. None of them is resolved by\n      this candidate.')
    candidate = replace_once(candidate,
        '        <li>Receipt verification context.  <xref target="scrapi-receipt"/>\n        describes a Receipt as containing the Merkle inclusion proof, and\n        <xref target="security-completeness"/> builds on inclusion.  For the',
        '        <li>Receipt verification context. Receipt resolution in\n        <xref target="scrapi-retrieval"/> is separate from verification;\n        <xref target="security-completeness"/> builds on inclusion. For the')
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
    outputs = {CANDIDATE_NAME: candidate}
    outputs.update({"examples/" + name + ".json": json_text(value)
                    for name, value in examples.items()})
    manifest = {
        "status": "unsubmitted and unadopted editor candidate",
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
    print(("Checked" if args.check else "Generated") + f" {len(outputs)} candidate artifacts; no protocol validation performed.")


if __name__ == "__main__":
    main()
