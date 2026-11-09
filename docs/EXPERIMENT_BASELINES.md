# Reproducing the pinned experiments

Updated 10 November 2026. These unadopted experiments use historical source
snapshots. Their source manifests identify exact inputs; later edits on `main`
are not replacements for those inputs.

Each CI job checks out the candidate commit and its declared source commit
separately, then copies only that candidate's own experiment directory into the
source checkout. The existing source and experiment integrity checks still run.
Changes to the experiment are tested; a successful run does not assess the current
specification as a new baseline or establish independent reproduction.

| Experiment | Fixed source commit | Source inventory |
|---|---|---|
| [Numeric representation](../experiments/numeric-representation-candidate-v0/README.md) | `16018dd405cad45bd8b11a7dc2278f6d95111ea6` | Eight files in its `manifest.json` |
| [Numeric byte binding](../experiments/numeric-byte-binding-v0/README.md) | `1131901d0b83f87c1c60674697574a60cc88fee1` | Eight files in its `sources.json`, including historical numeric-candidate inputs |
| [Native layout and migration](../experiments/native-layout-migration-v0/README.md) | `943d513fec3c0eaa7eb683120e2d82d5eb748285` | 204 files in its `sources.json`, including historical numeric and byte-binding experiments |

Copy only the experiment being executed. Other experiment directories in the
selected snapshot can be pinned inputs and must keep their historical bytes.
Do not update expected digests merely to make a newer checkout pass. A different
source baseline requires a separately reviewed experiment and evidence update.

## Numeric byte binding from a newer checkout

The byte-binding README is itself part of its closed, hash-checked asset inventory.
This guide supplies the preparation step without changing that README, the code,
source/asset manifests, fixtures or saved reports.

From the repository root, with a Python 3.12 or 3.14 virtual environment activated
and Node.js 24 available:

```sh
source_commit=1131901d0b83f87c1c60674697574a60cc88fee1
git cat-file -e "${source_commit}^{commit}" 2>/dev/null || \
  git fetch --no-tags origin "$source_commit"
binding_snapshot_dir="$(mktemp -d)"
git archive "$source_commit" | tar -x -C "$binding_snapshot_dir"
mkdir -p "$binding_snapshot_dir/experiments"
cp -R experiments/numeric-byte-binding-v0 "$binding_snapshot_dir/experiments/"
cd "$binding_snapshot_dir"

python -m pip install -r experiments/numeric-byte-binding-v0/requirements.txt
python experiments/numeric-byte-binding-v0/run.py --output "$binding_snapshot_dir/binding-run.json"
node experiments/numeric-byte-binding-v0/crosscheck.cjs "$binding_snapshot_dir/binding-run.json"
node experiments/numeric-byte-binding-v0/test_crosscheck.cjs "$binding_snapshot_dir/binding-run.json"
```

Retrieving a missing Git snapshot and installing dependencies require network
access. The subsequent checks run locally. The fresh directory supplies an unused
report path; the runner still refuses to overwrite a report. The other two
experiments' READMEs describe their corresponding snapshot preparation.

All original case expectations, regression controls and fingerprint checks remain
in force. Saved historical reports retain their original runtime and input
fingerprints; they are not relabeled as newly executed results.
