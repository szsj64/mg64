#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

AUSCHWITZ_PATH="${SCRIPT_DIR}/Auschwitz_Death_Certificates_1942-1943.xlsx"
MG1964_PATH="${SCRIPT_DIR}/../1964/data/parsed/mg1964.txt"

python3 "${SCRIPT_DIR}/match_mg64.py" -a "${AUSCHWITZ_PATH}" -m "${MG1964_PATH}" -v "$@"
