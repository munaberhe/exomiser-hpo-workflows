# exomiser-hpo-workflows

Reproducible Exomiser + HPO workflows to prioritise variants from VEP-annotated VCFs.

This repo ships two demo analyses:
- Hypertrophic cardiomyopathy (HCM) — HP:0001639, HP:0001671 (expects GRCh38 or GRCh37 VCF; set accordingly)
- Epilepsy / neurodevelopment — HP:0001250, HP:0001263, HP:0000252 (expects GRCh37 VCF)

Outputs include a human-friendly HTML report plus TSV (genes & variants) and JSON for downstream use.

----------------------------------------------------------------

## Requirements

- Java 17+ (Java 21 tested)
- Exomiser CLI 14.x installed and data downloaded

  Example layout:
  - ~/tools/exomiser/exomiser-cli-14.0.1.jar
  - data directories like:
    - ~/tools/exomiser/data/2406_hg19
    - ~/tools/exomiser/data/2406_hg38

- VEP-annotated VCFs, bgzipped (.vcf.gz) and tabix indexed (.tbi)

- macOS tip: if Homebrew git clashes with conda (dyld: _iconv not found), use Apple Git:
  env -u DYLD_LIBRARY_PATH -u DYLD_FALLBACK_LIBRARY_PATH /usr/bin/git <args>

----------------------------------------------------------------

## Quickstart

# 1) clone and enter the repo
git clone git@github.com:munaberhe/exomiser-hpo-workflows.git
cd exomiser-hpo-workflows

# 2) set Exomiser path (adjust if needed)
export EXOMISER_HOME="$HOME/tools/exomiser"

# 3) run the HCM demo (expects a GRCh38/GRCh37 VCF path set inside cases/case01_hcm/exomiser.yml)
bash run_exomiser_hcm.sh

# 4) run the epilepsy demo (expects a GRCh37 VCF path set inside cases/case02_epilepsy/exomiser.yml)
bash run_exomiser_epilepsy.sh

# 5) open the HTML reports (macOS)
open outputs/case01_hcm/*-exomiser.html
open outputs/case02_epilepsy/*-exomiser.html

----------------------------------------------------------------

## What the jobs do

Each cases/*/exomiser.yml is an Exomiser job that defines:

- sample: genomeAssembly, input vcf, and HPO terms
- preset: EXOME
- analysis:
  - analysisMode: PASS_ONLY
  - inheritanceModes tuned for each case
  - frequency sources: gnomAD exome/genome (E_, G_)
  - pathogenicity sources: REVEL, MVP, ALPHA_MISSENSE, SPLICE_AI
  - filters: failed call, low-value variant effects removed, frequency and pathogenicity thresholds
  - phenotype prioritisers: OMIM and hiPhive
- outputOptions: write HTML, JSON, TSV_GENE, TSV_VARIANT into outputs/<case>/

----------------------------------------------------------------

##  Assembly matters

- HCM job = usually GRCh38 VCF (set to match your file)
- Epilepsy job = GRCh37 VCF

If your VCF uses another assembly, either liftover the VCF or change sample.genomeAssembly and ensure the corresponding Exomiser data (2406_hg19 or 2406_hg38) are present.

----------------------------------------------------------------

## Run manually (without the wrapper scripts)

# HCM
java -Xms1g -Xmx6g -jar "$EXOMISER_HOME/exomiser-cli-14.0.1.jar" \
  --job="$(pwd)/cases/case01_hcm/exomiser.yml"

# Epilepsy (GRCh37)
java -Xms1g -Xmx6g -jar "$EXOMISER_HOME/exomiser-cli-14.0.1.jar" \
  --job="$(pwd)/cases/case02_epilepsy/exomiser.yml"

----------------------------------------------------------------

## Outputs

Each run writes to outputs/<case>/:
- *-exomiser.html – interactive, easiest for review
- *-exomiser.genes.tsv – ranked genes with phenotype/variant scores
- *-exomiser.variants.tsv – top variants with annotations & ACMG hints
- *-exomiser.json – structured detail for downstream parsing

Example quick peeks:

# first 10 rows (with header) of top genes
awk -F'\t' 'NR==1 || NR<=11' outputs/case01_hcm/*-exomiser.genes.tsv | column -t -s $'\t'

# first 10 rows (with header) of top variants
awk -F'\t' 'NR==1 || NR<=11' outputs/case01_hcm/*-exomiser.variants.tsv | column -t -s $'\t'

----------------------------------------------------------------

## Phenopackets demo → run pipeline from a phenopacket

This script reads HPO terms from a Phenopacket JSON (using `jq`), then runs the pipeline.

# example packets (already included)
phenopackets/case_hcm.json
phenopackets/case_epilepsy.json

# runner (already included)
tools/run_from_phenopacket.sh

# usage
export EXOMISER_HOME="$HOME/tools/exomiser"
tools/run_from_phenopacket.sh phenopackets/case_hcm.json data/case01_hcm.vep.vcf.gz GRCh37

# notes
# - requires jq
# - writes results under outputs/pipeline/<case_id>

----------------------------------------------------------------

## SCN1A gene-centric mini-report

Create a quick SCN1A summary (table + PNG) from an Exomiser variants TSV.

# script (already included)
python tools/report_scn1a.py outputs/case02_epilepsy/*-exomiser.variants.tsv docs/img

# generates
# - docs/img/scn1a_top.png   (bar chart of top 10 by Exomiser variant score)
# - docs/img/scn1a.md        (markdown table of top 10)
# Optional: commit and view via GitHub Pages:
#   https://munaberhe.github.io/exomiser-hpo-workflows/img/scn1a_top.png

----------------------------------------------------------------

## GitHub Pages (reports)

Static copies of reports can be placed under docs/ and will publish at:
https://munaberhe.github.io/exomiser-hpo-workflows/

Current landing page links:
- HCM report: /hcm-report.html
- Epilepsy report: /epilepsy-report.html
- SCN1A image (if generated): /img/scn1a_top.png

----------------------------------------------------------------

## Repository layout

```exomiser-hpo-workflows/
├─ cases/
│  ├─ case01_hcm/
│  │  └─ exomiser.yml                 # HCM job (assembly must match VCF)
│  └─ case02_epilepsy/
│     └─ exomiser.yml                 # Epilepsy job (GRCh37 VCF expected)
├─ outputs/
│  ├─ case01_hcm/                     # Exomiser outputs (HTML/JSON/TSV)
│  └─ case02_epilepsy/                # Exomiser outputs (when run)
├─ docs/
│  ├─ hcm-report.html                 # static copy for GitHub Pages (optional)
│  ├─ epilepsy-report.html            # static copy for GitHub Pages (optional)
│  ├─ index.html / index.md           # Pages landing
│  └─ img/
│     └─ scn1a_top.png                # generated by tools/report_scn1a.py
├─ phenopackets/
│  ├─ case_hcm.json
│  └─ case_epilepsy.json
├─ tools/
│  ├─ run_from_phenopacket.sh         # phenopacket → HPO → pipeline
│  └─ report_scn1a.py                 # SCN1A mini-report
├─ pipeline/                          # (optional) Nextflow wrapper
│  ├─ main.nf
│  └─ nextflow.config
├─ reports/                           # any extra summaries (optional)
├─ run_exomiser_hcm.sh                # wrapper for HCM job
├─ run_exomiser_epilepsy.sh           # wrapper for epilepsy job
├─ .gitignore
├─ LICENSE
├─ CITATION.cff
└─ README.md
```

----------------------------------------------------------------

## Minimal example job snippets

### HCM (set genomeAssembly to match your file)

sample:
  genomeAssembly: GRCh38
  vcf: /absolute/path/to/case01_hcm.vep.vcf.gz
  hpoIds: ['HP:0001639', 'HP:0001671']   # HCM, septal abnormality

preset: EXOME

analysis:
  analysisMode: PASS_ONLY
  inheritanceModes:
    AUTOSOMAL_DOMINANT: 1.0
  frequencySources: [GNOMAD_E_AFR, GNOMAD_E_AMR, GNOMAD_E_EAS, GNOMAD_E_NFE, GNOMAD_E_SAS,
                     GNOMAD_G_AFR, GNOMAD_G_AMR, GNOMAD_G_EAS, GNOMAD_G_NFE, GNOMAD_G_SAS]
  pathogenicitySources: [REVEL, MVP, ALPHA_MISSENSE, SPLICE_AI]
  steps:
    - failedVariantFilter: {}
    - variantEffectFilter:
        remove: [INTERGENIC_VARIANT, UPSTREAM_GENE_VARIANT, DOWNSTREAM_GENE_VARIANT,
                 NON_CODING_TRANSCRIPT_INTRON_VARIANT, CODING_TRANSCRIPT_INTRON_VARIANT,
                 THREE_PRIME_UTR_EXON_VARIANT, FIVE_PRIME_UTR_EXON_VARIANT]
    - frequencyFilter: {maxFrequency: 2.0}
    - pathogenicityFilter: {keepNonPathogenic: true}
    - inheritanceFilter: {}
    - omimPrioritiser: {}
    - hiPhivePrioritiser: {}
outputOptions:
  outputDirectory: /absolute/path/to/outputs/case01_hcm
  outputFilename: case01_hcm.vep-exomiser
  outputFormats: [HTML, JSON, TSV_GENE, TSV_VARIANT]

### Epilepsy (GRCh37)

sample:
  genomeAssembly: GRCh37
  vcf: /absolute/path/to/case02_epilepsy.vep.vcf.gz
  hpoIds: ['HP:0001250', 'HP:0001263', 'HP:0000252']   # seizure, GDD, microcephaly

preset: EXOME

analysis:
  analysisMode: PASS_ONLY
  inheritanceModes:
    AUTOSOMAL_DOMINANT: 1.0
    AUTOSOMAL_RECESSIVE_COMP_HET: 1.0
    AUTOSOMAL_RECESSIVE_HOM_ALT: 1.0
  frequencySources: [GNOMAD_E_AFR, GNOMAD_E_AMR, GNOMAD_E_EAS, GNOMAD_E_NFE, GNOMAD_E_SAS,
                     GNOMAD_G_AFR, GNOMAD_G_AMR, GNOMAD_G_EAS, GNOMAD_G_NFE, GNOMAD_G_SAS]
  pathogenicitySources: [REVEL, MVP, ALPHA_MISSENSE, SPLICE_AI]
  steps:
    - failedVariantFilter: {}
    - variantEffectFilter:
        remove: [INTERGENIC_VARIANT, UPSTREAM_GENE_VARIANT, DOWNSTREAM_GENE_VARIANT,
                 NON_CODING_TRANSCRIPT_INTRON_VARIANT, CODING_TRANSCRIPT_INTRON_VARIANT,
                 THREE_PRIME_UTR_EXON_VARIANT, FIVE_PRIME_UTR_EXON_VARIANT]
    - frequencyFilter: {maxFrequency: 1.0}
    - pathogenicityFilter: {keepNonPathogenic: true}
    - inheritanceFilter: {}
    - omimPrioritiser: {}
    - hiPhivePrioritiser: {}
outputOptions:
  outputDirectory: /absolute/path/to/outputs/case02_epilepsy
  outputFilename: case02_epilepsy.vep-exomiser
  outputFormats: [HTML, JSON, TSV_GENE, TSV_VARIANT]

----------------------------------------------------------------

## Troubleshooting

### VCF / assembly mismatch
Symptom: “CoordinatesOutOfBoundsException” or “coordinates out of contig bounds”.
Fix: Your VCF assembly doesn’t match the job’s genomeAssembly. Liftover the VCF or change the job’s assembly and ensure Exomiser has the corresponding 2406_hg19/2406_hg38 data.

### YAML format errors
Stick to the provided examples. Keys like inheritanceModes must be maps (e.g., AUTOSOMAL_DOMINANT: 1.0), not lists.

### Conda vs Homebrew git on macOS
If you see: dyld: Symbol not found: _iconv  
Use Apple Git explicitly:
env -u DYLD_LIBRARY_PATH -u DYLD_FALLBACK_LIBRARY_PATH /usr/bin/git <args>

----------------------------------------------------------------

## Citation

If you use this in a project or publication, please cite Exomiser and HPO:

- Smedley D, et al. A Whole-Genome Analysis Framework for Effective Discovery of Pathogenic Variants in Rare Disease. (Exomiser)
- Köhler S, et al. The Human Phenotype Ontology in 2021. (HPO)

