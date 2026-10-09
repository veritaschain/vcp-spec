# VCP v1.2 contract fixtures

Run `python -m unittest discover -s tests -v` from the repository root.
`manifest.json` is the expected result oracle. Each file is independently checked
against the indicated `ga` or explicit historical `legacy` contract. Some invalid
cases exercise the documented local checks in `tools/validate_v1_2.py` beyond JSON
Schema; `error_contains` identifies the expected semantic failure.

All keys, hashes, signatures and attestations are illustrative placeholders.
These fixtures are not cryptographic known-answer tests or production Evidence
Packs. A locally valid fixture has not passed external operational verification.
