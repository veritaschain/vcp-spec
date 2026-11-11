# Prepared correction for the archived SDK specification repository

**Status, 11 November 2026:** prepared patch only; not applied to the remote
`veritaschain/vcp-sdk-spec` repository. That repository is archived. This record
does not authorize changing its archival state or claim that its published guide
has been corrected.

## Exact target and scope

- Repository: <https://github.com/veritaschain/vcp-sdk-spec>
- Archived base: `d06ceea1388c916851083b92fdb0950aff0c0bd1`
- Patch: [archived-vcp-sdk-spec.patch](archived-vcp-sdk-spec.patch)
- Changed file: `VCP_IMPLEMENTATION_GUIDE_v1_1.md`, §11.2 only.

The guide shows installation and invocation commands for `vcp-conformance-test`
and `vcp-test`, but the repository does not provide those tools or establish their
published availability. The patch withdraws those commands as runnable guidance,
retains the existing local Merkle-example regression command, and links the
separate legacy v1.0 conformance guide with explicit version and scope limits.
No algorithms, fixtures, version requirements or certification status change.

## Validation performed on the local candidate

The patch was checked against a clean copy of the exact archived base with
`git apply --check`. Applying it locally produced byte-identical guide content to
the candidate tested with:

```bash
python -m unittest discover -s tests -v
```

All nine existing documentation/Merkle tests passed with Python 3.12.14 and
Node.js 24.22.1. They execute the published Python and TypeScript examples,
including unbalanced trees and negative controls. This is first-party local
validation; it does not establish complete VCP conformance or an external review.

## Applying the correction after an owner decision

Read-only review and a local application of the patch do not require unarchiving
the remote repository. If the owner explicitly authorizes a change to its archival
state and permits a correction PR, start a branch from the exact base above,
copy this patch outside that checkout, and run:

```bash
git checkout d06ceea1388c916851083b92fdb0950aff0c0bd1
git switch -c fix/conformance-tooling-guidance
git apply --check /path/to/archived-vcp-sdk-spec.patch
git apply /path/to/archived-vcp-sdk-spec.patch
python -m unittest discover -s tests -v
git diff --check
```

Review and commit the resulting diff before publishing a PR through the owner's
authorized workflow. If the repository has moved from this base, re-review the
current content and reconcile the patch; do not force a historical branch over
new work. Keep this status as prepared until the actual remote disposition is
recorded.
