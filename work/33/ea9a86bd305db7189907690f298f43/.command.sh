#!/bin/bash -ue
set -euo pipefail
  cat > job.yml <<'YML'
  
sample:
  genomeAssembly: GRCh37
  vcf: /Users/munaberhe/projects/genomics-portfolio/data/case01_hcm.vep.vcf.gz
  hpoIds: ['HP:0001639', 'HP:0001671']

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
    - frequencyFilter: {maxFrequency: 1.0}
    - pathogenicityFilter: {keepNonPathogenic: true}
    - inheritanceFilter: {}
    - omimPrioritiser: {}
    - hiPhivePrioritiser: {}
outputOptions:
  outputDirectory: outputs/pipeline/case_hcm
  outputFilename: pipeline
  outputFormats: [HTML, JSON, TSV_GENE, TSV_VARIANT]

  YML
  java -Xms1g -Xmx6g -jar "/Users/munaberhe/tools/exomiser/exomiser-cli-14.0.1.jar" --job=job.yml
