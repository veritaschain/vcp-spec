# Numeric representation → hash and signature binding experiment v0

**UNADOPTED research composition. Independent third-party reproduction has not
been established.** This is a separate synthetic experiment, not an adopted VCP
revision, native VCP validator, production implementation, migration utility or
certification. A matching expected failure is a successful **test**, not accepted
evidence. Merging this directory does not adopt its policy or change any current
normative requirement.

## Fixed inputs and purpose

The experiment connects the numeric candidate from [PR #12](https://github.com/veritaschain/vcp-spec/pull/12)
with the [byte-contract candidate](../../proposals/integrity-2026-10-24/byte-contract-candidate-v0/README.md)
from PR #10, at base commit
`1131901d0b83f87c1c60674697574a60cc88fee1`. [sources.json](sources.json) pins the
eight imported/referenced files by SHA-256. Both existing implementations are
loaded read-only after their fingerprints are checked. The source inventory and
the new experiment inventory are closed sets: omitting an entry is an error.

This checks the consequences of type, decoded numeric-string spelling, units,
ISO spelling and instant changes for actual JCS bytes, EventHash, leaf/root,
event/anchor signature inputs, **Ed25519 verification**, and external commitment
bytes. It does not accept `signature_valid` flags. The old 535 numeric cases and
all previous candidate vectors remain unchanged; this is 45 additional
composition cases, not a claim to retest every numeric field or every Merkle size.

## Explicit synthetic mapping

The old byte contract has a closed Header and rejects an added Header.TimestampISO.
Its ContractID, domains, event/statement shapes and signature algorithms are
unchanged. This adapter uses its opaque, fully committed Payload:

| Value | Position in this synthetic object | Numeric candidate check |
| --- | --- | --- |
| Nanoseconds | `Header.TimestampInt` | `iso_pair`, Unix ns, 0…2^63−1 |
| ISO / basis / unit | `Payload.NumericEvidence.TimestampISO`, `TimeBasis`, `TimestampUnit` | Selected nine-digit UTC spelling and `unix_no_leap`; unit `unix_ns` |
| Duration | `Payload.NumericEvidence.Duration.{Value,Unit}` | N028, seconds |
| Tolerance | `Payload.NumericEvidence.Tolerance.{Value,Unit}` | N042, milliseconds |
| Confidence | `Payload.NumericEvidence.Confidence.{Value,Unit}` | N012, ratio 0…1 |
| Anchor count | `AnchorStatement.EventCount` | N037, `batch_events`, plus actual supplied-list binding |
| Claimed anchor time | `AnchorStatement.RecordedAtNs` | N036's TIME_NS capacity, **synthetic mapping only** |
| Policy commitment | `Payload.PolicyDigest` and `AnchorStatement.PolicyDigest` | SHA-256 of the exact supplied policy bytes |

The Payload also commits `ExperimentID`. The selected policy records source
commit, candidate identifiers, units and time basis. A signature over a different
policy cannot authorize a unit conversion: policy interpretation becomes
UNASSESSED and violations of the selected numeric rules remain FAIL. Payload
placement, policy schema and the N036 mapping are experiment choices, **not
proposed native field allocations adopted by this PR**.

Each case supplies one event: `leaf = SHA-256(0x00 || decoded EventHash)` and root
equals that leaf. EventHash follows the existing domain-prefixed JCS contract.
Ordinary Ed25519 signs the **full domain-prefixed statement bytes**, not the
diagnostic SHA-256 of those bytes. Event signatures are outside EventHash and
the anchor root; the external commitment includes the anchor statement and
anchor signature. There is no external anchor service or trusted receipt.

Policy digests bind **exact bytes**, not reparsed/recanonicalized JSON. Adding a
newline to policy bytes changes its digest even though policy interpretation is
unchanged. Event JSON layout and escape spelling, in contrast, are normalized
by JCS after strict parsing. No Unicode or numeric-string normalization is added.

## Cases and separate outcomes

Every case includes raw event JSON, policy bytes, signed statements, signatures,
explicit reference case and manually declared per-check/byte-relation
expectations. [fixtures.py](fixtures.py) generates public synthetic evidence
using the old byte producer, without importing/calling the new checker. Expected
statuses are declared separately from observed outcomes. The actual checker
still shares the pinned byte implementation with the producer; this limitation
is why the byte/crypto crosscheck below is useful, but neither is an independent
third-party reproduction.

| Change | Result illustrated |
| --- | --- |
| Reorder JSON / change whitespace / escape `1` as `\u0031` | Same canonical bytes, hashes and signatures |
| `1` → `1.0` → `01.00`, or `0` → `-0.000` as strings | Numerically equivalent under selected rules; different signed bytes/hashes |
| String → boolean/null | Can be committed by the opaque Payload contract; numeric validation fails despite fresh valid signatures |
| String → JSON number, overflow, extra Header member | Rejected candidate shape; **no candidate EventHash** assigned |
| Change ns and ISO consistently by 1 ns | Fresh evidence has new hashes/signatures; old statements still verify cryptographically but fail event/list binding |
| Rehash changed event without resigning | Event signature fails actual Ed25519 verification |
| Wrong ISO year, broader offset/fraction spelling | Fresh signatures can pass while numeric checks fail |
| Leap second / smear | Cryptography can pass; numeric mapping stays UNASSESSED |
| 1 s → 1000 ms, or changed unit alone | No implicit unit conversion; wrong selected unit fails |
| Missing signed unit plus unsigned hint | Hint does not repair or override signed evidence |
| Policy newline / new policy / signed wrong count | Digest binding, policy interpretation and list/count checks are distinct |
| Changed anchor time/count / bad signature / wrong role/domain | Signed metadata tampering and actual signature failures are exposed |
| Valid signature with unconfigured KeyID | Raw crypto PASS, caller-owned test trust UNASSESSED |

The 16 checks are retained independently. `covered_checks_result` aggregates
**FAIL before UNASSESSED before PASS**, retaining all unknown entries. It refers
only to these checks, not overall truth or conformance. The 10 byte relations
are SAME / CHANGED / UNAVAILABLE. Generic JCS diagnostics for rejected inputs
are explicitly separate from candidate EventHash: a JSON number may have
diagnostic bytes without being a valid candidate event.

All keys/seeds in fixtures are **PUBLIC SYNTHETIC TEST MATERIAL**. The caller-owned
role/producer/stream/KeyID trust map is fixed in common.py, not supplied by the
evidence. No real-world identity, delegation, authorization, external time,
observation completeness, truth of the event or independent reproduction is
established, even for baseline PASS.

## Run and inspect

Python 3.12 or 3.14; dependencies pinned in [requirements.txt](requirements.txt).
From the repository root, with a virtual environment already activated:

```sh
python -m pip install -r experiments/numeric-byte-binding-v0/requirements.txt
python experiments/numeric-byte-binding-v0/run.py --output /tmp/numeric-binding-run.json
node experiments/numeric-byte-binding-v0/crosscheck.cjs /tmp/numeric-binding-run.json
```

Use a new output filename per run; the Python runner refuses overwrite. After
dependencies are installed, the checks need no network, Docker, service account,
real key or external data. The single Python command verifies source and new
file hashes, regenerates fixtures for byte equality, executes all 45 cases and
20 regression tests, and writes complete actual preimages, digests, signatures,
numeric detail and per-check differences. It exits nonzero for any mismatch,
missing test, skipped/expected-failure test or integrity check failure. The
manifest does not authenticate the author or host; changing both code and its
manifest is outside this local consistency check.

The optional Node 24 command uses built-in crypto and a separate restricted
canonical encoder for the ASCII-key fixture subset. It recomputes accepted
event/preimage/leaf/root and external-commitment bytes and checks all 88
available Ed25519 verifications (including expected failures). It does **not**
implement the full candidate schema, semantic/unit rules, arbitrary JCS input,
or a second complete verifier. It reads the local Python report; a passing
crosscheck is not a fresh independent reproduction or host authentication.

[manifest.json](manifest.json) pins new code, data, documentation and source
fingerprints. Its own bytes and each runtime/dependency version are recorded in
each run. Generated records are excluded from the manifest to avoid a circular
hash; [records](records/) contains separate Python 3.12/3.14 internal runs and
Node crosschecks. The repository commit pins their bytes and provenance.
Expected tally: **45 cases (12 PASS, 30 FAIL, 3 UNASSESSED), all matching their
expectations; 20 regressions without skips or expected failures**. These are
internal synthetic results only.

## Unresolved decisions and migration implications

1. Native placement/presence rules for numeric value, ISO representation, units,
   time basis and policy digest need a separately reviewed versioned schema.
   This experiment's opaque Payload adapter does not settle that mapping.
2. Whether equivalent decimal strings should be preserved or normalized, and
   exactly where normalization would occur, remains a normative decision. Under
   this candidate they are preserved; normalizing before hashing changes signed
   bytes. No floating-point coercion is permitted as a migration shortcut.
3. Unit registry, per-field conversion/rounding rules, capacity changes,
   timestamp range, leap/smear mapping and policy authority/version negotiation
   remain open. N036 does not thereby become an adopted AnchorRecord field.
4. Replacing types/units/ISO spellings or policy bytes requires new hashes and
   signatures wherever committed bytes change. A new signature does not validate
   the original signature against changed bytes or prove an old signer approved
   a new representation. Preserve originals and identify derived versions and
   any translation evidence; migration format/provenance is not specified here.
5. Synthetic keys and claimed RecordedAtNs do not establish signer authority,
   trusted timestamp or external receipt. The event-signature exclusion from
   the event/Merkle commitments is retained, not silently strengthened.
6. Real profile compatibility, all-field coverage, multi-event migration,
   performance/resource security and independent external execution require
   separate work. UNASSESSED cases are not evidence of adequacy.

## Scope boundary

Only this new directory and its isolated read-only CI workflow are added.
Current normative text, schemas, implementations, signed records, previous
experimental vectors, fixed distributions, release tags and K3 are unchanged.
The proposal remains **UNADOPTED** and independent third-party reproduction
remains **not established** before and after any document/code merge.
