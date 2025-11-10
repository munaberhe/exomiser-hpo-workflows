#!/usr/bin/env bash
set -euo pipefail
JAR=/Users/munaberhe/tools/exomiser/exomiser-cli-14.0.1.jar
CONF=file:/Users/munaberhe/tools/exomiser/application.properties
ANAL=/Users/munaberhe/projects/genomics-portfolio/cases/case01_hcm/exomiser.yml
OUTD=/Users/munaberhe/projects/genomics-portfolio/outputs/case01_hcm
mkdir -p "$OUTD"
java -Xms1g -Xmx6g -jar "$JAR" \
  $'--spring.config.location='"$CONF" \
  $'--analysis' "$ANAL" \
  $'--assembly' GRCh38 \
  $'--output-directory' "$OUTD" \
  $'--output-filename' exomiser_output
