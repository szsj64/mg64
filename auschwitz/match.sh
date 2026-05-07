#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

JMS_INPUT_PATH="${SCRIPT_DIR}/../jms/data/jms.json"
AUSCHWITZ_PATH="${SCRIPT_DIR}/Auschwitz_Death_Certificates_1942-1943.xlsx"
OUTPUT_PATH="${SCRIPT_DIR}/../auschwitz_matched.xlsx"

python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -a "${AUSCHWITZ_PATH}" -o "${OUTPUT_PATH}" -v "$@"
