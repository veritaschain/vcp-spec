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
