#! /usr/bin/env python3

"""
EUREMAP knowledge-graph validation and query runner.

Loads the EUREMAP ontology and catalogue into a single rdflib Graph,
validates the merged graph against the project's SHACL shapes
(euremap-shapes.ttl), then executes every SPARQL query in queries/*.rq
against the merged graph. Results are consolidated into
queries/RESULTS.md:

  - SELECT query results are rendered as markdown tables
    (abbreviated to 25 rows), with namespace prefixes shortened
    (resource -> res:, OBO -> obo:).
  - CONSTRUCT query results are serialised to
    data/derived-feedsInto.ttl (eur:feedsInto triples).

Finally, the full merged graph is exported as a combined bundle in
both Turtle (euremap-kg-full.ttl) and JSON-LD (euremap-kg-full.jsonld).

Inputs:
    ontology/euremap-ontology.ttl   - ontology definition
    data/euremap-catalogue.ttl      - instance/catalogue data
    shapes/euremap-shapes.ttl       - SHACL shape constraints
    queries/*.rq                     - SPARQL queries to run

Outputs:
    queries/RESULTS.md              - consolidated query results
    data/derived-feedsInto.ttl      - derived feedsInto triples
    euremap-kg-full.ttl             - merged graph, Turtle
    euremap-kg-full.jsonld          - merged graph, JSON-LD

Run from the repository root (paths are relative).
"""

import os
import glob
from rdflib import Graph
from pyshacl import validate

g = Graph()
g.parse("ontology/euremap-ontology.ttl")
g.parse("data/euremap-catalogue.ttl")
print("merged triples:", len(g))
sh = Graph().parse("shapes/euremap-shapes.ttl")
conforms, rg, rt = validate(g, shacl_graph=sh, inference="none", allow_warnings=True)
print("SHACL conforms:", conforms)
print(rt[:1500])
out = [
    "# EUREMAP SPARQL query results\n",
    f"Run with rdflib against ontology + catalogue graph ({len(g)} triples). Generated 2026-11-19.\n",
]
for f in sorted(glob.glob("queries/*.rq")):
    q = open(f).read()
    name = os.path.basename(f)
    res = g.query(q)
    out.append(f"\n## {name}\n")
    out.append(
        "```sparql\n"
        + "\n".join(tok for tok in q.splitlines() if not tok.startswith("PREFIX")).strip()
        + "\n```\n"
    )
    if res.type == "CONSTRUCT":
        cg = Graph()
        [cg.add(t) for t in res]
        cg.bind("eur", "https://w3id.org/euremap/ontology/")
        cg.bind("res", "https://w3id.org/euremap/resource/")
        cg.serialize("data/derived-feedsInto.ttl", format="turtle")
        out.append(
            f"Result: {len(cg)} `eur:feedsInto` triples (saved to `data/derived-feedsInto.ttl`).\n"
        )
        print(name, len(cg))
        continue
    vars_ = [str(v) for v in res.vars]
    rows = list(res)

    def fmt(x):
        if x is None:
            return ""
        s = (
            str(x)
            .replace("https://w3id.org/euremap/resource/", "res:")
            .replace("http://purl.obolibrary.org/obo/", "obo:")
        )
        return s.replace("|", "\\|")

    out.append(
        f"Rows: {len(rows)}\n\n| "
        + " | ".join(vars_)
        + " |\n|"
        + "---|" * len(vars_)
        + "\n"
    )
    for r in rows[:25]:
        out.append("| " + " | ".join(fmt(x) for x in r) + " |\n")
    if len(rows) > 25:
        out.append(f"\n…{len(rows) - 25} more rows\n")
    print(name, len(rows))
open("queries/RESULTS.md", "w").write("".join(out))
# combined bundle + JSON-LD
g.serialize("euremap-kg-full.ttl", format="turtle")
g.serialize("euremap-kg-full.jsonld", format="json-ld", indent=1)
