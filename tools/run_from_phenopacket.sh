#!/usr/bin/env bash
set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq is required (brew install jq / apt-get install jq)" >&2
  exit 1
fi

if [ $# -lt 3 ]; then
  echo "Usage: $0 <phenopacket.json> <vcf(.vcf.gz)> <assembly: GRCh37|GRCh38> [outdir]"
  exit 1
fi

PP=$1
VCF=$2
ASM=$3
OUTDIR=${4:-"outputs/pipeline"}

if [ ! -f "$PP" ]; then echo "Phenopacket not found: $PP" >&2; exit 1; fi
if [ ! -f "$VCF" ]; then echo "VCF not found: $VCF" >&2; exit 1; fi

# Extract comma-separated HPO IDs
HPO=$(jq -r '[.phenotypicFeatures[].type.id]|join(",")' "$PP")
if [ -z "$HPO" ] || [ "$HPO" = "null" ]; then
  echo "No HPO terms found in $PP" >&2; exit 1;
fi

case_id=$(basename "$PP" .json)
mkdir -p "$OUTDIR/$case_id"

echo "Running pipeline:"
echo "  HPO      : $HPO"
echo "  VCF      : $VCF"
echo "  Assembly : $ASM"
echo "  Outdir   : $OUTDIR/$case_id"
echo

nextflow run pipeline \
  --vcf "$VCF" \
  --hpo "$HPO" \
  --assembly "$ASM" \
  --outdir "$OUTDIR/$case_id"
