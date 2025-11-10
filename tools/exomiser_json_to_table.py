#!/usr/bin/env python3
import json, sys, csv
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: exomiser_json_to_table.py <exomiser.json> <out.tsv>", file=sys.stderr)
    sys.exit(1)

jpath = Path(sys.argv[1])
opath = Path(sys.argv[2])

with jpath.open() as fh:
    data = json.load(fh)

# Exomiser JSON shape depends on version; try to locate gene/variant rankings
genes = data.get("genes", []) or data.get("geneResults", [])
variants = data.get("variants", []) or data.get("variantResults", [])

# Write a compact gene table
gkeys = ["rank", "geneSymbol", "combinedScore", "phenotypeScore", "variantScore"]
with opath.open("w", newline="") as out:
    w = csv.writer(out, delimiter="\t")
    w.writerow(["type"] + gkeys)
    for g in genes:
        row = [
            "gene",
            g.get("rank") or g.get("geneRank"),
            g.get("geneSymbol") or g.get("gene", {}).get("geneSymbol"),
            g.get("combinedScore") or g.get("exomiserGeneCombinedScore"),
            g.get("phenotypeScore") or g.get("exomiserGenePhenoScore"),
            g.get("variantScore") or g.get("exomiserGeneVariantScore"),
        ]
        w.writerow(row)
    # Also dump top variants if present
    vkeys = ["rank", "geneSymbol", "contig", "start", "end", "ref", "alt", "functionalClass"]
    for v in variants:
        row = [
            "variant",
            v.get("rank"),
            v.get("geneSymbol"),
            v.get("contig"),
            v.get("start"),
            v.get("end"),
            v.get("ref"),
            v.get("alt"),
            v.get("functionalClass") or v.get("functionalAnnotation"),
        ]
        w.writerow(row)
