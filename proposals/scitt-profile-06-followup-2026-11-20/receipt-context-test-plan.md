# Receipt verification context: proposed test and decision plan

**Draft intake, unadopted.** Refs [#37](https://github.com/veritaschain/vcp-spec/issues/37).
This plan implements no verifier, opens no formal review, and reports no completed
Receipt interoperability test. Its subject is SCITT-VCP -06 §9 item 6.

## Decisions to compare

The experiment first needs explicit candidate rules for (1) the entry bytes and
their construction/version identifier, (2) service identity and the trusted key
context, including historical keys, and (3) any additional authenticated context
needed for position, tree size and omission reasoning. Each alternative must say
where that information originates, what authenticates it and which assumptions the
verifier makes. Successful key discovery does not establish that a service/key is
the intended trust anchor.

An experiment's outcome labels are local to its report: `verified under declared
context`, `rejected`, or `context insufficient`. They are proposed reporting
categories, not additions to VCP or SDK verdict vocabularies. No expectation may
be derived solely from the implementation being tested. The selected candidate
contract and applicable RFC clause provide the oracle before execution.

## Proposed cases

| ID | Input/control | Required evidence in the experiment report |
|---|---|---|
| RC-01 | Exact statement, known entry rule, intended service/key, valid Receipt | Recomputed entry/root, signature result and the explicitly bounded claim. |
| RC-02 | Missing or unknown entry rule | Record insufficient context; do not silently substitute the local VCP batch EventHash rule. |
| RC-03 | Valid signature from an untrusted key or another service | Demonstrate failure of the declared service/key trust check even when the mathematics verifies. |
| RC-04 | Statement bytes substituted after registration | Show the candidate-entry/root check that detects substitution; preserve both byte strings. |
| RC-05 | A Receipt added to a statement's unprotected metadata | Compare each candidate entry rule. Record whether it intentionally treats the statement as the same entry; do not assume whole-envelope identity. |
| RC-06 | CBOR re-encoding with equivalent decoded values | Compare exact bytes and the selected entry construction; explain equivalence or rejection from the contract, not parser behavior alone. |
| RC-07 | Leaf index changed, with otherwise unchanged proof/signature | Record root recomputation and whether the changed index can support the claimed position. Include boundary positions and non-power-of-two trees. |
| RC-08 | Tree size changed, with otherwise unchanged proof/signature | Record root recomputation and whether tree-size claims are authenticated sufficiently. Do not assume that every unprotected-field mutation necessarily changes the reconstructed root. |
| RC-09 | Index, size and proof changed together | Search synthetic boundary cases; record counterexamples as bounded findings, not generalized exploits. |
| RC-10 | Missing/stale/conflicting signed tree head or consistency evidence | State whether the candidate requires this evidence for the claim at issue, and report insufficient context or rejection accordingly. |
| RC-11 | Receipt signed by a retired key; archived key and later policy available | Evaluate the historical receipt under its declared historical trust context. Record key retention, compromise/rotation information and assessment time separately. |
| RC-12 | Inclusion passes but a claimed source event is absent | Report inclusion separately from completeness; show what independently fixed boundary, count, manifest or counterpart evidence supports any omission claim. |

RC-07 through RC-10 investigate the open question; this plan does not decide that
a signed tree head or consistency proof is universally required. Nor does it treat
tree size/leaf index as unauthenticated merely because they are outside the signed
protected header: their role in recomputing the signed root must be assessed.

## Package and execution requirements for the experiment

- Keep exact synthetic statement/Receipt bytes and separate decoded inspection
  views. Include the construction identifier, service identity, public keys, trust
  configuration, timestamps and any signed tree heads or consistency evidence.
- Publish SHA-256 per input/output artifact and pin both implementations, commands,
  dependency versions, exit codes and raw results. Never overwrite original bytes
  when producing an alternate encoding or adding a Receipt.
- Define expected outcomes and their source before running the implementation.
  Preserve unexpected disagreements and all contextual assumptions.
- Use at least two implementations and identify whether their maintainers are
  independent. Two first-party implementations do not establish independent
  reproduction.
- Record signature validity, inclusion, local batch integrity, history consistency
  and source completeness separately. The completed experiment cannot claim
  unobserved actions were captured or that a service is certified.

## Inputs received (24 November 2026)

Reply on the SCITT list from Bassem Kudsi (AugmentEV), [24 November 2026](https://mailarchive.ietf.org/arch/msg/scitt/nQPyS-vfZfywHe9_TcqcrgY5Tw4/),
answering the editor's two questions of [20 November](https://mailarchive.ietf.org/arch/msg/scitt/NEkecA1SxFvwENEoeFpaAdyLwYA/).
Recorded as input, not as adopted rules. The editor replied on the list the same day.

| Point | Input | Status here |
|---|---|---|
| Entry rule (a) | The rule belongs to the verifiable-data-structure profile. The [CCF profile -06](https://datatracker.ietf.org/doc/html/draft-ietf-scitt-receipts-ccf-profile-06) §§2.2, 3.2 hashes the Signed Statement as registered (tag 18 retained, empty unprotected header); the verifier computes the digest and MUST NOT take it from the Receipt. RFC 9942 §5.2.1 and the [MMR profile -00](https://datatracker.ietf.org/doc/html/draft-ietf-scitt-receipts-mmr-profile-00) §§5.1, 11.2 leave it open, so VCP would have to state it. | Candidate for (a). Open question raised by the editor: under RFC9162_SHA256 the vds value does not identify an entry rule, so the rule would be pinned with the service identity and committed to in the Registration Policy rather than selected by the Receipt. Would settle RC-05 and RC-06 if adopted. |
| Key (b) | RFC 9943 §§3, 7.1 require a trusted service key; SCRAPI §2.1 discovers keys. RFC 9943 §4 lets the key change between Receipts, so fix the service identity, not one key. | Consistent with this plan (discovery is not the trust decision; RC-03, RC-11). Open. |
| Position and size (c) | A Receipt of inclusion for RFC9162_SHA256 establishes neither ([reproduction](https://github.com/AugmentEV/rfc9942-receipt-position); RFC 9942 errata reports 9316 and 9317). A claim on them needs a signed checkpoint under the trusted key whose root equals the recomputed one, or a tree-size claim in the protected header; an omission argument also needs every entry in the range and consistency between heads. -06 rests no claim on them. | Settled in the -07 candidate by relying on Receipts for inclusion only (§8.5). Answers RC-07 and RC-08 for the reported cases. RC-09 and RC-10 apply only if a later claim rests on position or size. |
| Same shape in VCP | Open Issue 2: the AnchorRecord's event count is outside its signature. | Recorded in the -07 candidate (item 2). The direction "register the AnchorRecord as a Signed Statement" is a proposal, not adopted; it belongs with the VCP-CP-2026-003/004 work. |

**First-party check of the tree arithmetic.** [`receipt_position_check.py`](receipt_position_check.py),
written from RFC 9162 §2.1 without running the reporter's code: the honest path for
leaf 5 of 7 recomputes the same root when read with tree size 8, and with the size
fixed no other leaf index does; for tree sizes 1 to 64, 1,984 of 2,080 (size, index)
pairs also recompute their root under another size (sizes searched up to 255).
This matches the reported figures. It is the same maintainer side as the editor,
so it is not independent reproduction under this plan, and it tests tree
arithmetic, not a Receipt or COSE implementation. The reporter's check with
`scitt-cose` 0.5.0 is a second implementation; its maintainer's relation to the
reporter is not recorded here.

## Intake exit criteria

The tracking issue remains open until the candidate alternatives, fixed vectors,
reproduction evidence and unresolved choices are recorded, and an editor assigns
the next review/adoption route. A merge of this plan or its example checks does
not close it. Changing entry bytes, trusted-context requirements or schema
acceptance requires its own compatibility and migration analysis; all existing
VCP-CP proposals retain their published status.

Sources: [SCITT-VCP -06 §9](https://www.ietf.org/archive/id/draft-kamimura-scitt-vcp-06.txt),
[RFC 9942 §§4, 5.2.1](https://www.rfc-editor.org/rfc/rfc9942),
[RFC 9943 §5.1.3](https://www.rfc-editor.org/rfc/rfc9943), and
[SCRAPI -11 §§2.1–2.4](https://datatracker.ietf.org/doc/html/draft-ietf-scitt-scrapi-11).
