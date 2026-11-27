# Candidate experiment cases

**Proposed 25 November 2026; partial first-party replay 27 November 2026.**
The 22 expectations below follow the [Receipt context candidate](README.md)
and extend [RC-01 through RC-12](../scitt-profile-06-followup-2026-11-20/receipt-context-test-plan.md).
Each row identifies the basis for its expected outcome.

The [replay package](replay/README.md) exercised **CX-01, CX-09, CX-10, CX-17,
CX-19, CX-21 and CX-22**. The [Python report](replay/results/python.json) and
[Go report](replay/results/go.json) each record eight Receipt assessments.
CX-19 covers both K1 and K2. All seven cases reuse the two issued Receipts
and supply the applicable archive records and keys through the selected trust
view. **The remaining 15 cases are unexecuted.**

CX-17 checks that the report leaves source completeness and history consistency
unassessed after verifying inclusion. CX-22 checks the unresolved choice between
two authenticated epochs before verifying either candidate rule; it does not
exercise a comparison of their cryptographic outcomes. Both implementations
were run by VSO under the fixture's restricted encoding and trust assumptions.
Independent external reproduction remains outstanding and [#37](https://github.com/veritaschain/vcp-spec/issues/37)
stays open.

| ID | Controlled case | Expected result under the candidate | Basis / prior case |
|---|---|---|---|
| CX-01 | Valid A1 statement and Receipt, preconfigured service, authorized key, authenticated applicable context | Inclusion verified under declared context; no other property implied | §§1, 2, 4 / RC-01 |
| CX-02 | Policy Signed Statement and its Receipt supplied, but initial rule context absent | Context insufficient; the policy's own Receipt cannot bootstrap the missing rule | §§1, 3 / RC-02 |
| CX-03 | Unknown protected rule value on a Receipt signed by an otherwise authorized service | Context insufficient; retain the unknown value without treating it as trusted until its signature is verified; no fallback to A1 | §§3, 4 / RC-02 |
| CX-04 | Trusted configuration authorizes A1; an independently authenticated applicable record requires A2 for the same context | Rejected for context conflict, not silently resolved by whichever proof succeeds | §§2–4 / RC-03 |
| CX-05 | Add or re-encode only a well-formed unprotected map, keeping all retained bytes identical | Same E; original valid inclusion result preserved | §2 / RC-05, RC-06 |
| CX-06 | Change a retained byte-string length encoding while preserving its decoded bytes; retain original Receipt | E differs. With complete A1 context the original Receipt fails, assuming ordinary collision resistance; issuer-signature behavior is assessed separately | §2 / RC-04, RC-06 |
| CX-07 | Same E, compare A1 entry with A2 entry against a Receipt built for A1 | Different leaf commitments; no automatic interchange or downgrade | §2 / RC-01, RC-04 |
| CX-08 | Nonminimal outer tag, indefinite outer array/byte string, detached payload, or duplicate map label | Outside/rejected by the restricted corpus; do not claim these are all forbidden by base COSE or SCITT | §2 / RC-06 |
| CX-09 | Service rotates K1 to K2; K1 authorization, historical context and applicability evidence are retained with no applicable revocation | Old K1 Receipt can verify under the historical context; today's discovery need not return K1 | §§1, 3, 4 / RC-11 |
| CX-10 | Same old Receipt, but only current K2 is available | Context insufficient; do not report invalid signature merely because K1 is unavailable | §§1, 4 / RC-11 |
| CX-11 | Rule A1 valid before a boundary and A2 after it; unsigned event time is the only epoch selector | Context insufficient, even if one attempted rule recomputes a signed root | §3 / RC-11 |
| CX-12 | Separately authorized archive record binds the exact Receipt digest to the A1 epoch | Evaluate A1, reporting archive-authority reliance; mutating the Receipt invalidates that binding | §§1, 3 / RC-11 |
| CX-13 | Bounded authorized candidate list; more than one applicable rule matches | Context insufficient / ambiguous; preserve all matches | §3 / RC-02 |
| CX-14 | Authorized key is marked compromised; only a self-asserted pre-compromise time supports historical acceptance | No verified historical claim; context insufficient, or rejected if the declared policy explicitly excludes that key | §§1, 4 / RC-11 |
| CX-15 | Known wrong service supplies a mathematically valid Receipt | Rejected by the service allowlist; record math separately | §4 / RC-03 |
| CX-16 | Known applicable context, mutated statement/proof/signature | Rejected for the specific failed verification check; no claim of global non-inclusion | §§2, 4 / RC-04 |
| CX-17 | Inclusion passes while no independent completeness evidence exists | Report inclusion only; source completeness and global history consistency unestablished | §4 / RC-12 |
| CX-18 | RFC9162_SHA256 tree-size mutation still reconstructs the same signed root | Inclusion may still pass; never infer size or position from that result | §4 / RC-07, RC-08 |
| CX-19 | An authorized archive binds service S and SHA256(E) to A1. S issues two Receipts for the same E, under K1 and K2 respectively. The record applies to both and independent context authorizes each key for its use. | Evaluate each proof and signature separately. Both can verify under A1 using the same entry-specific record; their Receipt digests differ. Record the archive authority and key evidence used for each. | §§1, 3, 4 / CX-09, CX-12 |
| CX-20 | Present the CX-19 record for a different service, or for a different E at S. No other applicable binding is supplied. | The record does not select an epoch for that pair. Report insufficient historical context; an explicitly disallowed service is separately rejected under CX-15. | §§1, 3, 4 / CX-11, CX-15 |
| CX-21 | The CX-19 record selects A1 for S and E, but the reissued Receipt has no independent evidence needed to establish the signing key's historical authorization under the declared policy. | Report insufficient key context; the entry binding supplies neither an issuance time nor proof of the key's applicability. | §§1, 3, 4 / CX-10, CX-14 |
| CX-22 | The same service and E appear in two authenticated rule epochs; the entry-specific records and policy give no way to choose between them for this Receipt. | Report ambiguous context even if only one attempted rule produces a matching root. | §§1, 3, 4 / CX-11, CX-13 |

Record exact input hashes, trusted-context hashes, rule/epoch selection evidence,
derived entry and root, signature result, final report, and reason for every row.
A later implementation that disagrees with an expectation requires review of both
the code and this candidate; do not silently regenerate expectations from it.
