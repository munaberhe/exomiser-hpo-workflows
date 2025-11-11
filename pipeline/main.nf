nextflow.enable.dsl=2

params.hpo      = params.hpo      ?: "HP:0001639,HP:0001671"
params.assembly = params.assembly ?: "GRCh37"
params.vcf      = params.vcf      ?: "data/case01_hcm.vep.vcf.gz"
params.exomiserJar = params.exomiserJar ?: "${HOME}/tools/exomiser/exomiser-cli-14.0.1.jar"
params.outdir   = params.outdir   ?: "outputs/nextflow"

Channel
  .value( file(params.vcf) )
  .set { vcf_ch }

// Build the Exomiser job YAML as a single string (val)
def hpo_list = params.hpo.split(',').collect{ "'${it.trim()}'" }.join(', ')
def job_text = """
sample:
  genomeAssembly: ${params.assembly}
  vcf: ${file(params.vcf).toRealPath()}
  hpoIds: [${hpo_list}]

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
  outputDirectory: ${params.outdir}
  outputFilename: pipeline
  outputFormats: [HTML, JSON, TSV_GENE, TSV_VARIANT]
"""

process exomiser {
  tag "${vcf.simpleName}"
  publishDir params.outdir, mode: 'copy'

  input:
    path vcf
    val job

  shell:
  '''
  set -euo pipefail
  cat > job.yml <<'YML'
  !{job}
  YML
  java -Xms1g -Xmx6g -jar "!{params.exomiserJar}" --job=job.yml
  '''
}

workflow {
  exomiser( vcf_ch, job_text )
}
