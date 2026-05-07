#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

${SCRIPT_DIR}/jms/scripts/pipeline.sh
${SCRIPT_DIR}/1964/scripts/pipeline.sh
${SCRIPT_DIR}/scripts/pipeline.sh
${SCRIPT_DIR}/zbl/pipeline.sh
${SCRIPT_DIR}/hbl/pipeline.sh
