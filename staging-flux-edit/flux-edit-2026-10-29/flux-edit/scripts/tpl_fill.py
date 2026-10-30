"""U11 tpl_fill: load templates/<name>/vN, verify index.json sha256, fill typed params, return an API graph.

Strings: ${KEY} placeholders in string inputs. Numbers: params.schema.json maps KEY -> node title + input.
Fails (TplError, zero POSTs) on: index sha256 mismatch, unknown/missing key, wrong type, out of range,
leftover ${. The filled graph always goes through flux_edit_guard.check_graph (GuardStop on a hit).
"""
import copy
import hashlib
import json
import os
import re

import flux_edit_guard

def _jl(path, encoding="utf-8"):
    with open(path, encoding=encoding) as f:
        return json.load(f)



def _wr(path, mode, data):
    with open(path, mode) as f:
        f.write(data)


PH = re.compile(r"\$\{([A-Z0-9_]+)\}")


class TplError(Exception):
    pass


def tdir(templates_root, name, version):
    return os.path.join(templates_root, name, version)


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def verify_index(templates_root, name, version):
    idx = _jl(os.path.join(templates_root, "index.json"))
    ent = [t for t in idx.get("templates", []) if t["name"] == name and t["version"] == version]
    if len(ent) != 1:
        raise TplError(f"{name}/{version} not in index.json")
    d = tdir(templates_root, name, version)
    on_disk = sorted(f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)))
    if on_disk != sorted(ent[0]["files"]):
        raise TplError(f"file set differs from index: {on_disk}")
    for fn, want in ent[0]["files"].items():
        if _sha(os.path.join(d, fn)) != want:
            raise TplError(f"sha256 mismatch {name}/{version}/{fn} (used versions are frozen; make v2)")
    return ent[0]


def _check_value(key, spec, v):
    t = spec["type"]
    if t == "string":
        if not isinstance(v, str) or not v:
            raise TplError(f"{key}: need non-empty string")
        if "${" in v:
            raise TplError(f"{key}: value contains ${{")
        if "pattern" in spec and not re.fullmatch(spec["pattern"], v):
            raise TplError(f"{key}: {v!r} does not match {spec['pattern']}")
        if len(v) > spec.get("max_len", 4096):
            raise TplError(f"{key}: too long")
    elif t in ("int", "float"):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or (t == "int" and not isinstance(v, int)):
            raise TplError(f"{key}: need {t}")
        if not (spec["min"] <= v <= spec["max"]):
            raise TplError(f"{key}: {v} outside [{spec['min']}, {spec['max']}]")
    elif t == "enum":
        if v not in spec["enum"]:
            raise TplError(f"{key}: {v!r} not in {spec['enum']}")
    else:
        raise TplError(f"{key}: unknown type {t}")


def _node_by_title(g, title):
    hits = [n for n in g.values() if n.get("_meta", {}).get("title") == title]
    if len(hits) != 1:
        raise TplError(f"node title {title!r} matches {len(hits)} nodes (must be unique)")
    return hits[0]


def fill_graph(graph, schema, params):
    unknown = set(params) - set(schema)
    missing = set(schema) - set(params)
    if unknown or missing:
        raise TplError(f"unknown keys {sorted(unknown)} missing keys {sorted(missing)}")
    g = copy.deepcopy(graph)
    for k, spec in schema.items():
        _check_value(k, spec, params[k])
    for k, spec in schema.items():
        node = _node_by_title(g, spec["node_title"])
        cur = node["inputs"].get(spec["input"])
        if spec["type"] == "string":
            if not isinstance(cur, str) or "${" + k + "}" not in cur:
                raise TplError(f"{k}: placeholder not found at {spec['node_title']}.{spec['input']}")
            node["inputs"][spec["input"]] = cur.replace("${" + k + "}", params[k])
        else:
            node["inputs"][spec["input"]] = params[k]
    left = PH.findall(json.dumps(g)) or ("${" in json.dumps(g))
    if left:
        raise TplError(f"leftover placeholder {left}")
    flux_edit_guard.check_graph(g)
    return g


def fill(templates_root, name, version, params):
    verify_index(templates_root, name, version)
    d = tdir(templates_root, name, version)
    graph = _jl(os.path.join(d, "workflow_api.json"))
    schema = _jl(os.path.join(d, "params.schema.json"))
    return fill_graph(graph, schema, params)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("templates_root"); ap.add_argument("name"); ap.add_argument("version"); ap.add_argument("params_json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    g = fill(a.templates_root, a.name, a.version, _jl(a.params_json, encoding="utf-8"))
    _wr(a.out, "w", json.dumps(g, indent=1))
