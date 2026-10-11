"""Archive a bounded OpenNeuro search for independent T2 lesion cohorts."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


OUT = Path(__file__).resolve().parent / "source_cache/openneuro_glioma_candidates_2026-10-01"
URL = "https://openneuro.org/crn/graphql"
TERMS = ("glioma", "brain tumor", "brain tumour", "T2w lesion", "glioblastoma")
TYPE_QUERY = "query { edge: __type(name: \"DatasetEdge\") { fields { name type { kind name ofType { kind name } } } } dataset: __type(name: \"Dataset\") { fields { name type { kind name ofType { kind name } } } } }"
ADVANCED_TYPE_QUERY = "query { __type(name: \"DatasetSearchInput\") { name inputFields { name type { kind name ofType { kind name } } } } }"


def fetch(opener: urllib.request.OpenerDirector, query: str) -> bytes:
    req = urllib.request.Request(
        URL, data=json.dumps({"query": query}).encode(),
        headers={"User-Agent": "MRI-source-audit/1.0", "Content-Type": "application/json"},
    )
    with opener.open(req, timeout=25) as response:
        raw = response.read(200_001)
        if response.status != 200 or len(raw) > 200_000:
            raise ValueError("Unexpected GraphQL response")
        return raw


def save(name: str, query: str, raw: bytes) -> dict:
    (OUT / name).write_bytes(raw)
    return {"file": name, "query": query, "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records = [save("types.json", TYPE_QUERY, fetch(opener, TYPE_QUERY)),
               save("advanced_input.json", ADVANCED_TYPE_QUERY,
                    fetch(opener, ADVANCED_TYPE_QUERY))]
    types = json.loads((OUT / "types.json").read_bytes())["data"]
    edge_fields = [x["name"] for x in types["edge"]["fields"]]
    dataset_fields = [x["name"] for x in types["dataset"]["fields"]]
    scalar_fields = [x["name"] for x in types["dataset"]["fields"]
                     if x["type"]["kind"] in ("SCALAR", "ENUM")]
    selected = [x for x in ("id", "name", "description", "summary", "doi", "created", "modified")
                if x in scalar_fields]
    if "node" not in edge_fields or not selected:
        raise ValueError({"edge_fields": edge_fields, "dataset_fields": dataset_fields})
    matches = {}
    for index, term in enumerate(TERMS):
        query = ("query { search(q: " + json.dumps(term) + ", first: 15) { "
                 "edges { node { " + " ".join(selected) + " } } "
                 "pageInfo { hasNextPage } } }")
        raw = fetch(opener, query)
        name = f"search_{index:02d}.json"
        records.append(save(name, query, raw))
        data = json.loads(raw)
        if data.get("errors"):
            matches[term] = {"errors": data["errors"]}
        elif data.get("data", {}).get("search") is None:
            matches[term] = {"search": None}
        else:
            edges = data["data"]["search"]["edges"]
            matches[term] = {"nodes": [e["node"] for e in edges],
                             "hasNextPage": data["data"]["search"]["pageInfo"]["hasNextPage"]}
    for index, candidate in enumerate(("glioma", "glioblastoma")):
        query = ("query { advancedSearch(query: { diagnosis: " + json.dumps(candidate) +
                 ", publicOnly: true }, first: 15) { edges { node { " +
                 " ".join(selected) + " } } pageInfo { hasNextPage } } }")
        raw = fetch(opener, query)
        name = f"advanced_{index:02d}.json"
        records.append(save(name, query, raw))
        data = json.loads(raw)
        result = data.get("data", {}).get("advancedSearch")
        matches["advanced:" + candidate] = (
            {"errors": data["errors"]} if data.get("errors") else
            {"advancedSearch": None} if result is None else
            {"nodes": [e["node"] for e in result["edges"]],
             "hasNextPage": result["pageInfo"]["hasNextPage"]})
    (OUT / "index.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(matches, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: {"status": "null" if ("search" in v or "advancedSearch" in v)
                                    else "errors" if "errors" in v else "results",
                          "ids": [x.get("id") for x in v.get("nodes", [])]}
                      for k, v in matches.items()}, indent=2))


if __name__ == "__main__":
    main()
