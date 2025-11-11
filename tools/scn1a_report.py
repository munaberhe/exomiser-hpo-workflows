#!/usr/bin/env python3
"""
Make a concise SCN1A (or any gene) report from Exomiser outputs.

Inputs:
  - Exomiser variants TSV  (e.g. outputs/.../*-exomiser.variants.tsv)
  - Exomiser genes TSV     (e.g. outputs/.../*-exomiser.genes.tsv)
Args:
  --gene SCN1A (default)
  --outdir docs/ (default so it’s auto-published by GitHub Pages)
Outputs:
  - <outdir>/scn1a_report.md
  - <outdir>/scn1a_variants.tsv
"""
import argparse, csv, pathlib, sys
from collections import OrderedDict

def read_tsv(path):
    with open(path, newline='') as fh:
        for row in csv.DictReader(fh, delimiter='\t'):
            yield row

def best_path_score(row):
    vals = []
    for k in ("EXOMISER_VARIANT_SCORE","MAX_PATH","EXOMISER_GENE_VARIANT_SCORE"):
        if k in row and row[k]:
            try:
                vals.append(float(row[k]))
            except:
                pass
    return max(vals) if vals else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gene", default="SCN1A")
    ap.add_argument("--variants", required=True, help="*-exomiser.variants.tsv")
    ap.add_argument("--genes", required=True, help="*-exomiser.genes.tsv")
    ap.add_argument("--outdir", default="docs")
    args = ap.parse_args()

    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    gene_sym = args.gene.upper()

    gene_info = None
    for r in read_tsv(args.genes):
        if r.get("GENE_SYMBOL","").upper() == gene_sym:
            gene_info = r
            break

    keep = []
    for r in read_tsv(args.variants):
        if r.get("GENE_SYMBOL","").upper() != gene_sym:
            continue
        row = OrderedDict()
        row["RANK"]       = r.get("RANK","")
        row["CONTIG"]     = r.get("CONTIG","")
        row["POS"]        = r.get("START","")
        row["REF"]        = r.get("REF","")
        row["ALT"]        = r.get("ALT","")
        row["GENOTYPE"]   = r.get("GENOTYPE","")
        row["FUNC"]       = r.get("FUNCTIONAL_CLASS","")
        row["HGVS"]       = r.get("HGVS","")
        row["AF_MAX_SRC"] = r.get("MAX_FREQ_SOURCE","")
        row["AF_MAX"]     = r.get("MAX_FREQ","")
        row["ACMG_CLASS"] = r.get("EXOMISER_ACMG_CLASSIFICATION","")
        row["ACMG_EVID"]  = r.get("EXOMISER_ACMG_EVIDENCE","")
        ps = best_path_score(r)
        row["PATH_SCORE"] = f"{ps:.3f}" if ps is not None else ""
        keep.append((ps if ps is not None else -1.0, row))

    keep.sort(key=lambda x: (-x[0], int(x[1]["RANK"]) if x[1]["RANK"].isdigit() else 999999))

    tsv_out = outdir / f"{gene_sym.lower()}_variants.tsv"
    if keep:
        with open(tsv_out, "w", newline='') as fh:
            writer = csv.DictWriter(fh, fieldnames=list(keep[0][1].keys()), delimiter='\t')
            writer.writeheader()
            for _, row in keep:
                writer.writerow(row)

    md_out = outdir / f"{gene_sym.lower()}_report.md"
    with open(md_out, "w") as md:
        md.write(f"# {gene_sym} gene-centric report\n\n")
        if gene_info:
            md.write("## Gene summary\n")
            md.write(f"- Exomiser combined gene score: **{gene_info.get('EXOMISER_GENE_COMBINED_SCORE','')}**\n")
            md.write(f"- Phenotype score: **{gene_info.get('EXOMISER_GENE_PHENO_SCORE','')}**\n")
            md.write(f"- Variant score: **{gene_info.get('EXOMISER_GENE_VARIANT_SCORE','')}**\n")
            md.write(f"- OMIM linked: **{gene_info.get('OMIM_SCORE','')}**\n\n")
        else:
            md.write("_Gene not present in gene ranking table._\n\n")

        md.write("## Top variants (tab-separated table also saved)\n\n")
        if not keep:
            md.write("_No variants for this gene in the Exomiser variants TSV._\n")
        else:
            head = list(keep[0][1].keys())
            md.write("| " + " | ".join(head) + " |\n")
            md.write("|" + "|".join(["---"]*len(head)) + "|\n")
            for _, row in keep[:10]:
                md.write("| " + " | ".join(str(row[k]) for k in head) + " |\n")
            md.write(f"\nFull table: `{tsv_out.name}`\n")

    print(f"Wrote: {md_out} and {tsv_out if keep else '(no TSV, no variants)'}")

if __name__ == "__main__":
    sys.exit(main())
