# Local VCP v1.2 event checks

`validate_v1_2.py` checks JSON input, the selected event schema and the current
selected intra-event rules. It does not verify signatures, hash chains, external
anchors, completeness, authorization identities or protocol conformance.

```bash
python -m pip install -r requirements-test.txt
python tools/validate_v1_2.py event.json another-event.json
```

The JSON reader uses UTF-8, rejects duplicate object keys and non-JSON numeric
constants (`NaN`, `Infinity`, `-Infinity`), and preserves integer and decimal
values while checking them. A fractional value cannot pass an integer field by
rounding to a binary floating-point integer. This is local schema validation;
it does not choose a VCP numeric encoding or define cryptographic signed bytes.
Missing dependencies for a schema's format checks produce an operational error,
instead of silently skipping date-time or URI validation.

`--schema` selects a custom schema without disabling the selected intra-event
rules. Those rules still require a string `Header.EventType` and, for the event
types they inspect, the fields and types needed to evaluate the rule. Missing or
incompatible rule inputs are reported as a per-file validation failure; later
files are still checked. This prerequisite check does not impose the entire
default schema on custom input or establish protocol conformance.

Historical compact input requires `--legacy` and the unchanged historical schema:

```bash
python tools/validate_v1_2.py --legacy \
  --schema spec/v1.2/vcp-event-v1.2-rc-legacy.json legacy-event.json
```

A copy with the same parsed schema content is accepted. Passing the current or a
modified schema with `--legacy` is a configuration error; the flag cannot disable
the current intra-event checks by changing the schema path's spelling.

| Exit code | Meaning |
| --- | --- |
| `0` | Every supplied file passed the selected local checks. |
| `1` | At least one file had invalid input or failed a selected local check. |
| `2` | Usage, schema configuration, required format support or file access failed. |

The CLI reports each readable event file even after an earlier event is invalid
or inaccessible. An operational error takes precedence over exit `1`. A schema
configuration error stops the invocation before event results are emitted.
`LOCAL CHECKS PASS` always retains the explicit cryptographic/external-check
limitation; it is not a certification result.

Regression tests create their malformed input in temporary directories. Existing
specifications, schemas, fixed fixtures and recorded evidence are unchanged.
