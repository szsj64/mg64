#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Some plot scripts read matched_M_*.txt via relative paths, so we must cd here.
cd "${SCRIPT_DIR}"

python3 "${SCRIPT_DIR}/plot_alternative_birth_years_histogram.py" -i "${SCRIPT_DIR}/../jms/data/jms.json" -o "${SCRIPT_DIR}/alternative_birth_years_histogram.png"
python3 "${SCRIPT_DIR}/plot_matched_alternative_birth_years_histogram.py" -i "${SCRIPT_DIR}/report.txt" -o "${SCRIPT_DIR}/matched_alternative_birth_years_histogram.png"
python3 "${SCRIPT_DIR}/plot_number_of_matches.py" -o "${SCRIPT_DIR}/number_of_matches.png"
python3 "${SCRIPT_DIR}/plot_fs_scores.py" -i "${SCRIPT_DIR}/matched_fs.txt" -o "${SCRIPT_DIR}/fs_scores_histogram.png"
