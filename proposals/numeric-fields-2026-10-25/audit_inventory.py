#!/usr/bin/env python3
"""Read-only source/coverage audit; not a protocol or numeric verifier."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSES = {
    "TIME_NS", "UTC_NS", "UINT63", "POS63", "UINT31", "POS31", "INDEX31",
    "SECONDS63", "MILLISECONDS31", "DURATION_NS63", "RATIO01", "DEC_SIGNED",
    "DEC_NONNEG", "TYPED_FEATURE", "TYPED_CONTROL", "CALENDAR",
    "EXTERNAL_INTEGER", "ENUM_CODE",
}
SCALAR_KEYS = {"type", "minimum", "maximum", "pattern", "format", "description", "$comment"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    """Keep ambiguous/non-JSON input out of the source comparison."""
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError(f"non-JSON numeric constant: {value}")

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def same_snapshot(left, right):
    """Compare parsed snapshots without Python's bool/int/float coercion.

    The inventory promises a source snapshot, not merely equivalent numeric
    constraints. Even an integer token changed to a floating-point token differs.
    This is an audit rule, not a new VCP scalar acceptance rule.
    """
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(same_snapshot(left[k], right[k]) for k in left)
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(same_snapshot(a, b) for a, b in zip(left, right))
    return left == right


def pointer(document, value):
    node = document
    for part in value.lstrip("#/").split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        node = node[int(key)] if isinstance(node, list) else node[key]
    return node


def escape(value):
    return value.replace("~", "~0").replace("/", "~1")


def walk(document, node, ptr="", path="", context="all structured events", refs=()):
    """Follow named properties, array items, positive branches and local refs.

    Not a general JSON Schema evaluator. Conditional contexts are event bindings;
    they do not establish presence or satisfy oneOf authorization predicates.
    `if`/`not` predicates are not counted as positive field declarations.
    """
    if "$ref" in node:
        ref = node["$ref"]
        require(ref.startswith("#/"), f"unsupported nonlocal ref: {ref}")
        require(ref not in refs, f"recursive ref requires explicit review: {ref}")
        target = pointer(document, ref)
        if ref == "#/$defs/DecimalString":
            yield path, ptr, context, {k: v for k, v in target.items() if k in SCALAR_KEYS}
        else:
            yield from walk(document, target, ref[1:], path, context, refs + (ref,))
        return
    types = node.get("type", [])
    if isinstance(types, str):
        types = [types]
    if set(types) & {"integer", "number"} or node.get("format") == "date-time":
        yield path, ptr, context, {k: v for k, v in node.items() if k in SCALAR_KEYS}
    for name, child in node.get("properties", {}).items():
        yield from walk(document, child, ptr + "/properties/" + escape(name),
                        path + "." + name if path else name, context, refs)
    if isinstance(node.get("items"), dict):
        yield from walk(document, node["items"], ptr + "/items", path + "[]", context, refs)
    for keyword in ("allOf", "oneOf", "anyOf"):
        for i, child in enumerate(node.get(keyword, [])):
            yield from walk(document, child, f"{ptr}/{keyword}/{i}", path, context, refs)
    if "then" in node:
        code = node.get("if", {}).get("properties", {}).get("Header", {}).get(
            "properties", {}).get("EventType", {}).get("const")
        yield from walk(document, node["then"], ptr + "/then", path, code or context, refs)


def scalar_sites(node, ptr=""):
    """Also check declaration coverage independently of ref reachability."""
    if isinstance(node, dict):
        types = node.get("type", [])
        if isinstance(types, str):
            types = [types]
        if (set(types) & {"integer", "number"} or node.get("format") == "date-time"
                or node.get("$ref") == "#/$defs/DecimalString"):
            yield ptr
        for key, value in node.items():
            yield from scalar_sites(value, ptr + "/" + escape(key))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from scalar_sites(value, ptr + "/" + str(i))


def render(rows, sources):
    text = ["# Numeric-field inventory", "",
            "**UNADOPTED discussion draft; independent reproduction not established.**",
            "", "Generated from [inventory.json](inventory.json). Read the [candidate rules and",
            "migration limitations](README.md) before using the proposed classes. Full source",
            "hashes are in [sources.json](sources.json). Required-at-leaf is not required-in-every-event.",
            "", "The `Payload.` prefix on inherited module blocks is an inventory projection,",
            "not a claim that the GA schema defines all these nested paths. LegacyHeader,",
            "AnchorRecord, configuration and SCITTReceipt are separate contexts.", ""]
    for row in rows:
        text += [f"## {row['id']}: `{row['path']}`", "",
                 f"- **Context/group:** {row['group']}",
                 f"- **Current definition:** {row['current']}",
                 f"- **Current unit/range evidence:** {row['current_unit']}",
                 f"- **Presence:** {row['presence']}"]
        schema = row["schema"]
        if schema:
            url = sources["schema"]["url"]
            text += [f"- **Schema site:** [`{schema['pointer']}`]({url}); context: {schema['context']}.",
                     "- **Exact scalar snapshot:** `" + json.dumps(schema["constraints"], ensure_ascii=False,
                                                                   separators=(",", ":")) + "`"]
        links = []
        for item in row["references"]:
            start, end = item["lines"]
            source = item["source"]
            links.append(f"[{source} L{start}–{end}]({sources[source]['url']}#L{start}-L{end})")
        if links:
            text += ["- **Text evidence:** " + "; ".join(links)]
        text += [f"- **Candidate:** `{row['candidate_class']}` — {row['candidate_unit']}",
                 f"- **Migration/limits:** {row['migration_notes']}", ""]
    return "\n".join(text).rstrip() + "\n"


def audit(render_output=False):
    manifest = read_json(HERE / "sources.json")
    data = read_json(HERE / "inventory.json")
    require(data["status"] == "UNADOPTED_DISCUSSION_DRAFT", "draft status changed")
    require(data["independent_reproduction"] == "not_established", "independence claim changed")
    require(data["base_commit"] == manifest["commit"], "baseline mismatch")
    sources = manifest["sources"]
    line_counts = {}
    for name, item in sources.items():
        content = (ROOT / item["path"]).read_bytes()
        require(hashlib.sha256(content).hexdigest() == item["sha256"], f"source drift: {name}")
        require(item["url"] == f"https://github.com/veritaschain/vcp-spec/blob/{manifest['commit']}/{item['path']}",
                f"source URL mismatch: {name}")
        line_counts[name] = len(content.decode("utf-8").splitlines())
    for name, mirror in (("body", "VCP-Specification-v1_2_en.md"),
                         ("annex", "VSO-SPEC-CHANGE-001.md")):
        require(hashlib.sha256((ROOT / mirror).read_bytes()).hexdigest() == sources[name]["sha256"],
                f"root mirror drift: {mirror}")
    schema = read_json(ROOT / sources["schema"]["path"])
    expanded = {}
    for path, ptr, context, constraints in walk(schema, schema):
        value = (ptr, context, constraints)
        require(path not in expanded or same_snapshot(expanded[path], value), f"ambiguous expansion: {path}")
        expanded[path] = value
    rows = data["fields"]
    require(len({r["id"] for r in rows}) == len(rows), "duplicate entry ID")
    require(len({r["path"] for r in rows}) == len(rows), "duplicate instance path")
    documented = {r["path"]: r["schema"] for r in rows if r["schema"] is not None}
    require(set(documented) == set(expanded), "missing/extra schema instance path")
    require({v[0] for v in expanded.values()} == set(scalar_sites(schema)), "uncovered schema declaration")
    for path, item in documented.items():
        ptr, context, constraints = expanded[path]
        require(same_snapshot((item["pointer"], item["context"], item["constraints"]), (ptr, context, constraints)),
                f"schema snapshot mismatch: {path}")
        parent, key = ptr.rsplit("/properties/", 1)
        required = key in pointer(schema, parent).get("required", [])
        require(type(item["required_in_containing_object"]) is bool and
                item["required_in_containing_object"] == required, f"requiredness mismatch: {path}")
    for row in rows:
        require(row["candidate_class"] in CLASSES, f"unknown candidate class: {row['id']}")
        for key in ("path", "current", "current_unit", "candidate_unit", "presence", "migration_notes"):
            require(isinstance(row[key], str) and bool(row[key].strip()), f"empty {key}: {row['id']}")
        require(row["references"] or row["schema"], f"unsourced entry: {row['id']}")
        for item in row["references"]:
            start, end = item["lines"]
            require(type(start) is int and type(end) is int and
                    1 <= start <= end <= line_counts[item["source"]], f"bad citation: {row['id']}")
    markdown = render(rows, sources)
    if render_output:
        (HERE / "inventory.md").write_text(markdown)
    else:
        require((HERE / "inventory.md").read_text() == markdown, "generated inventory.md drift")
    return {"status": "inventory_consistency_pass", "base_commit": manifest["commit"],
            "schema_definition_sites": len(set(scalar_sites(schema))),
            "schema_instance_paths": len(expanded), "review_entries": len(rows),
            "other_entries": len(rows) - len(expanded),
            "candidate_classes": dict(sorted(Counter(r["candidate_class"] for r in rows).items())),
            "inventory_sha256": hashlib.sha256((HERE / "inventory.json").read_bytes()).hexdigest(),
            "independent_reproduction": "not_established",
            "limitations": "No semantic/protocol/cryptographic verification or independent external run."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true", help="regenerate inventory.md only")
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.render), indent=2))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"inventory audit failed: {error}\n")
