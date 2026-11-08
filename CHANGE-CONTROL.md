# VCP Change Control — Interim Procedure

**Document:** VCP-PROC-001 (interim)
**Status:** Proposed. Not in effect until decision record [VCP-DR-2026-001](decisions/VCP-DR-2026-001.md) records acceptance after its public review.
**Applies to:** normative VeritasChain Protocol (VCP) artifacts in this repository.
**Maintained by:** VeritasChain Standards Organization (VSO), operated by VeritasChain Co., Ltd.

---

## 1. Why this exists

VCP proposals currently have no defined route from "draft" to "adopted". For example, the integrity errata draft and the normative-change draft were merged as discussion documents on 2026-10-24. They are still unadopted because no VCP procedure says who decides, after what review, or how the decision is recorded.

[VAP v1.2 §10.3](https://github.com/veritaschain/vap-spec/blob/main/spec/v1.2/VAP_Framework_Specification.md) describes a 30-day public review, deliberation by the Technical Committee and a two-thirds vote. No Technical Committee membership or decision record for VCP has been published.

This document sets an interim VCP procedure that can be followed and checked now. It switches to the committee process once that committee is constituted (§10).

## 2. Scope

**In scope (normative artifacts):**

- the English specification text under `spec/vX.Y/`
- normative annexes (for example, `VSO-SPEC-CHANGE-001.md`)
- the JSON Schemas under `spec/vX.Y/`
- version tags and errata

**Out of scope:** translations (convenience only), `examples/`, `proposals/`, `experiments/`, research records, the website, SDKs and reference implementations. Changes to these follow normal pull-request review. They cannot change a normative requirement.

This procedure does not amend VAP §10.3. It does not re-evaluate past releases or annexes, and their published records stand as they are.

## 3. Roles

| Role | Who | Responsibility |
|---|---|---|
| **Editor** | Tokachi Kamimura (VeritasChain Co., Ltd.) | Assigns IDs and change classes, opens and closes reviews, answers comments, records decisions, creates tags |
| **Contributor** | Anyone | Submits change proposals, errata reports and review comments |
| **Independent reviewer** | Anyone not affiliated with VeritasChain Co., Ltd. who chooses to be recorded | A review recorded with its affiliation. Optional; never required for a decision, always disclosed when present |

**Disclosure.** The Editor is affiliated with VeritasChain Co., Ltd. That company operates VSO, and it is the only conformity assessment body listed in the VC-Certified CAB registry (VAP v1.2 §10.1, confirmed 2026-10-21). Under this interim procedure, a decision is the decision of a single editor after public review. It is not a consensus determination by an independent standards body. The absence of objections is recorded as such and is not reported as endorsement.

The [VSO conflict-of-interest policy](https://veritaschain.org/vso/policies/) excludes conflicted persons from deliberations and votes on the cases they are conflicted on. Under this interim procedure there is no alternate decision-maker, so the Editor cannot step aside. Instead, the conflict is disclosed in every decision record. This is a known limitation, and §10 is the route out of it.

## 4. Change classes

The class decides the review period and the release gates. The Editor proposes a class when opening review, and reviewers may challenge it.

| Class | Version effect | Criteria |
|---|---|---|
| **E — Editorial** | none, or batched into the next PATCH | Typography, links, references, wording that changes no requirement, translations |
| **P — Errata / PATCH** | `x.y.Z+1` | Fixes that leave unchanged both the bytes a conforming producer hashes or signs and the set of documents the schema accepts. Includes resolving contradictions where a precedence rule already exists, correcting an example to match existing normative text, and withdrawing incorrect compatibility or capability claims |
| **M — MINOR** | `x.Y+1.0` | Backward-compatible additions: new scheme identifiers or objects, schema additions that widen what is accepted, deprecations, newly specified verification rules with vectors |
| **X — MAJOR** | `X+1.0.0` | Changes to hash or signature preimages, wire types or required fields; removal of deprecated mechanisms; anything that narrows what is accepted |
| **S — Security** | per the fix (P, M or X) | A defect that lets a verifier accept tampered, omitted or misattributed evidence. Expedited notice (§6.3); the fix still meets the gates of its own class |

Classes follow §1.3 of the specification (Semantic Versioning 2.0.0). Adding values to a closed schema enum is classed **M**, because existing strict validators reject the new values.

## 5. Identifiers and records

| Identifier | Meaning | Where it lives |
|---|---|---|
| `VCP-CP-YYYY-NNN` | Change proposal | GitHub issue, plus `proposals/` when longer text is needed |
| `VCP-DR-YYYY-NNN` | Decision record | `decisions/VCP-DR-YYYY-NNN.md` |
| `VCP-ERR-X.Y-NNN` | Erratum to version X.Y | Errata section of `spec/vX.Y/README.md` |
| `VSO-SPEC-CHANGE-NNN` | Normative annex for an adopted M or X change | `spec/vX.Y/` (existing convention) |

[`decisions/REGISTER.md`](decisions/REGISTER.md) lists every proposal with its class and current status. Identifiers are never reused.

## 6. Lifecycle

```
Draft → Public review → Decision → Released
                          ├─ Accepted
                          ├─ Accepted with changes
                          ├─ Rejected
                          ├─ Deferred
                          └─ Withdrawn (by the proposer, at any stage)
```

### 6.1 Submission

Anyone can open a proposal with the **Change proposal** or **Errata report** issue form. The Editor aims to assign a `VCP-CP` identifier and a proposed class within 7 days.

### 6.2 Public review

The Editor opens review with a comment on the proposal issue that states:

- the proposal identifier and class
- the exact text under review, pinned to a commit SHA
- the affected artifacts and sections
- the review end date and time in UTC

The issue gets the `public-review` label and the register is updated.

| Class | Minimum review period |
|---|---|
| E | none (the decision is recorded in the next PATCH decision record) |
| P | 14 days |
| M | 30 days |
| X | 60 days |

Comments are made on the issue. A contributor who cannot comment publicly may write to `standards@veritaschain.org`. Such comments are summarized publicly and attributed only with permission.

A substantive change to the text under review restarts the review period.

### 6.3 Security class

Report suspected security defects to `security@veritaschain.org`, not in a public issue. Once a defect is confirmed, the Editor publishes a notice as soon as practicable. The notice gives the affected versions, what a verifier may wrongly accept, and interim verifier guidance.

The review period for the fix may be shortened to 7 days. The fix still meets the release gates of its class. A defect that is already public, such as the Merkle construction and AnchorRecord coverage findings of 2026-10-24, is handled in public.

### 6.4 Decision

After review closes, the Editor writes a decision record using [`decisions/TEMPLATE.md`](decisions/TEMPLATE.md). The record contains:

- the decision and the class it was finally given
- the SHA-256 of every affected artifact, before and after
- the review window and the number of comments received, with links
- a response to every substantive comment
- disclosures: the Editor's affiliation, any independent reviewers and their affiliations
- the implementation and test-vector status at the time of the decision

**A change is adopted only when its decision record, with decision Accepted or Accepted with changes, is merged into `decisions/`.** Merging a proposal document, a passing CI run or the absence of objections is not adoption.

### 6.5 Release

| Gate | P | M | X |
|---|---|---|---|
| Adopted decision record(s) | required | required | required |
| CI passes on the exact commit to be tagged | required | required | required |
| Repository-root mirrors byte-identical to `spec/` copies | required | required | required |
| SHA-256 of the schema and specification recorded in the release notes | required | required | required |
| Known issues updated | required | required | required |
| Normative test vectors for every new or changed mechanism | — | required | required |
| At least two implementations reproduce the vectors | — | required | required |
| Migration guide; legacy verification described; signed data never rewritten | — | if deprecating | required |

**Implementation independence.** Release notes state whether each implementation that reproduced the vectors is maintained inside or outside VeritasChain Co., Ltd. If all of them are inside, the release is labelled "first-party implementations only". Independence is reported under the existing [counting criteria](https://github.com/veritaschain/vap-spec/blob/main/disclosures/2026-10-24-counting-criteria.md).

Tags are never moved or replaced. A deployed copy of a schema, such as the one on veritaschain.org, is checked byte-for-byte against the tagged file. "Source merged", "tag created" and "website published" are reported as separate facts.

## 7. Status vocabulary

These terms are used with exactly these meanings in this repository:

| Term | Meaning |
|---|---|
| **Merged** | The text is on `main`. Says nothing about adoption |
| **Adopted** | An accepted decision record is merged (§6.4) |
| **Released** | A tag exists for an adopted change |
| **Implemented (first-party)** | Implemented by VeritasChain Co., Ltd. or VSO |
| **Independently reproduced** | Reproduced by an evaluator outside VeritasChain Co., Ltd., recorded under the counting criteria |

## 8. Reconsideration

Anyone may request reconsideration within 30 days after a decision record is merged by opening an issue that references it. The Editor answers with a new decision record.

No body independent of the Editor exists to hear appeals at present, and this is disclosed in every decision record.

## 9. Changes to this procedure

Changes to this document are class **M** and follow this procedure, including a 30-day review.

## 10. Transition to the Technical Committee

This interim procedure ends when a Technical Committee for VCP is constituted and has published:

- its membership and each member's affiliation, with at least three voting members, at least one of whom is not affiliated with VeritasChain Co., Ltd.;
- its decision rule (VAP §10.3 specifies a two-thirds vote);
- its first decision record under that rule.

Decisions taken under this interim procedure remain valid after the transition, and their records state which procedure applied.

## 11. GitHub practice (informative)

- **Avoid closing keywords.** Pull requests should use `Refs #N`, not `Fixes`, `Closes` or `Resolves #N`, for issues that track multi-step work. A closing keyword closes the issue automatically on merge.
- **Use labels:** `change-proposal`, `errata`, `public-review`, `decision-pending`, `security`.
- **Approvals.** The repository is currently maintained under a single GitHub account, so a GitHub approval by a second person cannot be recorded. The decision record, not a GitHub approval, is the authoritative evidence of adoption.

---

## 日本語要約

VCP の提案を「採択」まで進める手続きがこれまで存在しなかったため、暫定手続きを定めます。

- **決定者:** Editor（上村十勝、VeritasChain株式会社）。VSO の運営会社であり、唯一の登録 CAB でもあることを開示します。決定は単独編集者による公開レビュー後の決定であり、独立した標準化団体の合意ではありません。
- **区分:** E（編集）、P（正誤表）、M（後方互換の追加）、X（破壊的変更）、S（セキュリティ）。
- **公開レビュー期間:** P は14日、M は30日、X は60日。
- **採択の条件:** 採択された決定記録（`decisions/VCP-DR-YYYY-NNN.md`）が merge されたときに限り、その変更は採択されたものとします。提案文書の merge、CI の成功、反対意見がないことは、いずれも採択ではありません。
- **リリースの条件:** M と X では、テストベクタと2つ以上の実装による再現が必要です。実装がすべて第一者であれば、その旨を明記します。
- **移行:** VeritasChain株式会社に属さない者を含む3名以上の TC が構成と決定規則を公開した時点で、この暫定手続きは終了し、VAP §10.3 の手続きに移ります。
