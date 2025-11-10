import sys, os
import pandas as pd
import matplotlib.pyplot as plt

if len(sys.argv) < 3:
    print("Usage: python tools/report_scn1a.py <variants.tsv> <outdir>")
    sys.exit(1)

tsv = sys.argv[1]
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)

df = pd.read_csv(tsv, sep="\t", dtype=str)

# Normalize numeric field (EXOMISER_VARIANT_SCORE) if present
for col in ["EXOMISER_VARIANT_SCORE"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Filter for SCN1A
mask = df["GENE_SYMBOL"].str.upper() == "SCN1A"
scn1a = df[mask].copy()
if scn1a.empty:
    print("No SCN1A variants found in:", tsv)
    sys.exit(0)

# Sort by Exomiser variant score desc, fallback to keep as-is
if "EXOMISER_VARIANT_SCORE" in scn1a.columns:
    scn1a = scn1a.sort_values("EXOMISER_VARIANT_SCORE", ascending=False)

keep_cols = [c for c in [
    "RANK","GENE_SYMBOL","CONTIG","START","REF","ALT","HGVS",
    "EXOMISER_VARIANT_SCORE","EXOMISER_ACMG_CLASSIFICATION",
    "MAX_PATH","MAX_PATH_SOURCE"
] if c in scn1a.columns]

scn1a_out_csv = os.path.join(outdir, "scn1a_top.csv")
scn1a[keep_cols].to_csv(scn1a_out_csv, index=False)

# Bar chart of top 10 by Exomiser variant score
if "EXOMISER_VARIANT_SCORE" in scn1a.columns:
    plot_df = scn1a.head(10)
    labels = plot_df["HGVS"].fillna(plot_df["RANK"]).astype(str).str.slice(0, 30)
    plt.figure(figsize=(10,5))
    plt.bar(range(len(plot_df)), plot_df["EXOMISER_VARIANT_SCORE"])
    plt.xticks(range(len(plot_df)), labels, rotation=45, ha="right")
    plt.ylabel("Exomiser Variant Score")
    plt.title("Top SCN1A variants")
    plt.tight_layout()
    png = os.path.join(outdir, "scn1a_top.png")
    plt.savefig(png, dpi=150)
    print("Wrote:", png)

# Markdown table (top 10)
md_path = os.path.join(outdir, "scn1a.md")
top_md = scn1a[keep_cols].head(10).to_markdown(index=False)
with open(md_path, "w") as f:
    f.write("# SCN1A top variants\n\n")
    f.write(top_md)
print("Wrote:", scn1a_out_csv, "and", md_path)
