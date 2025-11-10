# exomiser-hpo-workflows

Reproducible Exomiser + HPO workflows to prioritise variants from VEP-annotated VCFs.

This repo ships two demo analyses:
- Hypertrophic cardiomyopathy (HCM) — HP:0001639, HP:0001671 (expects GRCh38 VCF)
- Epilepsy / neurodevelopment — HP:0001250, HP:0001263, HP:0000252 (expects GRCh37 VCF)

Outputs include a human-friendly HTML report plus TSV (genes & variants) and JSON for downstream use.

----------------------------------------------------------------

## Requirements

- Java 17+ (Java 21 tested)
- Exomiser CLI 14.x installed and data downloaded

  Example layout:
  - ~/tools/exomiser/exomiser-cli-14.0.1.jar
  - data directories like ~/tools/exomiser/data/2406_hg19 and/or ~/tools/exomiser/data/2406_hg38

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

# 3) run the HCM demo (expects a GRCh38 VCF path inside cases/case01_hcm/exomiser.yml)
bash run_exomiser_hcm.sh

# 4) run the epilepsy demo (expects a GRCh37 VCF path inside cases/case02_epilepsy/exomiser.yml)
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

- HCM job = GRCh38 VCF
- Epilepsy job = GRCh37 VCF

If your VCF uses another assembly, either liftover the VCF or change genomeAssembly and ensure the corresponding Exomiser data (2406_hg19 or 2406_hg38) are present.

----------------------------------------------------------------

## Run manually (without the wrapper scripts)

# HCM (GRCh38)
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

## Customising

- Change HPO terms in sample.hpoIds to match your phenotype.
- Tighten/relax frequency via frequencyFilter.maxFrequency.
- Switch inheritance models by editing analysis.inheritanceModes.
- Assembly: ensure sample.genomeAssembly matches the VCF and that Exomiser data for that assembly exist.

----------------------------------------------------------------

## Troubleshooting

### VCF / assembly mismatch
Symptom: Error like “CoordinatesOutOfBoundsException” or “coordinates out of contig bounds”.
Fix: Your VCF assembly doesn’t match the job’s genomeAssembly. Fix VCF (liftover) or change the job and ensure Exomiser has the corresponding 2406_hg19/2406_hg38 data.

### YAML format errors
- Stick to the provided examples. Keys like inheritanceModes must be maps (e.g., AUTOSOMAL_DOMINANT: 1.0), not lists.

### Conda vs Homebrew git on macOS
If you see dyld: Symbol not found: _iconv, call Apple Git explicitly:
env -u DYLD_LIBRARY_PATH -u DYLD_FALLBACK_LIBRARY_PATH /usr/bin/git <args>

----------------------------------------------------------------

```## Repository layout

exomiser-hpo-workflows/
├── cases/
│   ├── case01_hcm/
│   │   └── exomiser.yml                  # HCM job (expects GRCh38 VCF)
│   └── case02_epilepsy/
│       └── exomiser.yml                  # Epilepsy job (expects GRCh37 VCF)
├── outputs/
│   ├── case01_hcm/                       # created after running HCM job
│   │   ├── case01_hcm.vep-exomiser.html
│   │   ├── case01_hcm.vep-exomiser.genes.tsv
│   │   ├── case01_hcm.vep-exomiser.variants.tsv
│   │   └── case01_hcm.vep-exomiser.json
│   └── case02_epilepsy/                  # created after running epilepsy job
├── reports/
│   └── case02_epilepsy/
│       ├── phenotype_HP0001250_variants.tsv
│       ├── scn1a_genes.tsv
│       └── scn1a_variants.tsv
├── run_exomiser_hcm.sh                   # wrapper for HCM job
├── run_exomiser_epilepsy.sh              # wrapper for epilepsy job
├── .gitignore
└── README.md
```
----------------------------------------------------------------

## Minimal example job snippets

### HCM (GRCh38)

sample:
  genomeAssembly: GRCh38
  vcf: /absolute/path/to/case01_hcm.vep.vcf.gz
  hpoIds: ['HP:0001639', 'HP:0001671']   # HCM, LVOT obstruction

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

## Citation

If you use this in a project or publication, please cite Exomiser and HPO:

- Smedley D, et al. A Whole-Genome Analysis Framework for Effective Discovery of Pathogenic Variants in Rare Disease. (Exomiser)
- Köhler S, et al. The Human Phenotype Ontology in 2021. (HPO)


