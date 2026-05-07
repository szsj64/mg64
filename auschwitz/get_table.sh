#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

OUTPUT="${SCRIPT_DIR}/Auschwitz_Death_Certificates_1942-1943.xlsx"

python3 "${SCRIPT_DIR}/get_table.py" -o "${OUTPUT}" -v
