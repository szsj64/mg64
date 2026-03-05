#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

JMS_INPUT_PATH="${SCRIPT_DIR}/../jms/data/jms.json"
JMS_LINKS_PATH="${SCRIPT_DIR}/../jms/data/45409.txt"
MG1964_INPUT_PATH="${SCRIPT_DIR}/../1964/data/parsed/mg1964.txt"
OUTPUT_PATH="${SCRIPT_DIR}/../matched.xlsx"

python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -o "${OUTPUT_PATH}" -g -v -l
