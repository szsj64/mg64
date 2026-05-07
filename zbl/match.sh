#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

JMS_INPUT_PATH="${SCRIPT_DIR}/../jms/data/jms.json"
ZBL_PAGES_DIR="${SCRIPT_DIR}/pages"
OUTPUT_PATH="${SCRIPT_DIR}/../zbl_matched.xlsx"

python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -z "${ZBL_PAGES_DIR}" -o "${OUTPUT_PATH}" -v "$@"
