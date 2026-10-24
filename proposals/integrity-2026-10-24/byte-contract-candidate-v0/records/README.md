# Internal execution record — 2026-10-24 JST

**Unadopted candidate. Independent third-party reproduction unestablished.**

The two Python JSON files are complete stdout from `check.py --node <node>` in
the candidate folder, using Python 3.12.14 and 3.14.3 respectively with Node
24.19.0 on the same VSO development environment. The run used no external
evaluator or receipt service. Actual platform, interpreter, crypto-library and
installed package versions are inside each record. There was no stderr on
these successful final runs; both exited 0. They are not two independent runs
by different operators and not a Linux deployment validation.

Both read the same committed `data/` files. SHA-256 values are recorded in each
run and in `source-data-sha256.json`; that manifest additionally fixes the
candidate code, documentation and dependencies used. The containing Git commit
identifies these records. The manifest excludes `records/` to avoid a recursive
self-hash. Hash/record consistency does not authenticate the machine or operator.

`negative-controls.json` records two separate runs against temporary copies:
one changed an event hash, the other removed a proof record. Each exited 1 at
the exact-regeneration comparison. Neither modified the committed vectors or
any fixed distribution. Source review also corrected a numeric lexical edge
case in the Node cross-check: whole-string matching now rejects trailing CR,
LF and Unicode line terminators. The saved numeric vectors include these cases.

The separate byte implementations agree for the covered inputs. Python's
candidate generator/checker share helpers; Node uses a separate restricted JCS
encoder, incremental tree and recursive proof fold. This is internal consistency
and cross-language evidence, not full independent acceptance, native VCP
verification, normative adoption or independent third-party reproduction.

Before publication, all 132 files already tracked at base
`9b88e318aeb9575de66047ed49c8ab86c2879487` were compared byte-for-byte and found
unchanged. Only the new candidate folder is in scope. Existing CI remains a
check of the old v1.2 contract; it is not a candidate acceptance suite.
