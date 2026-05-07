#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"${SCRIPT_DIR}/download_pdfs.sh" -o "${SCRIPT_DIR}/../data/pdfs"
"${SCRIPT_DIR}/extract_lines_from_pdfs.sh" -i "${SCRIPT_DIR}/../data/pdfs" -o "${SCRIPT_DIR}/../data/extracted"
"${SCRIPT_DIR}/parse_lines.sh" -i "${SCRIPT_DIR}/../data/extracted" -o "${SCRIPT_DIR}/../data/parsed"
"${SCRIPT_DIR}/combine_parsed_lines.sh" -i "${SCRIPT_DIR}/../data/parsed" -o "${SCRIPT_DIR}/../data/parsed/mg1964.txt"
"${SCRIPT_DIR}/export_xlsx.sh" -i -s -a -S -f
python3 "${SCRIPT_DIR}/plot_birth_year_histogram.py" -i "${SCRIPT_DIR}/../data/parsed/mg1964.txt" -o "${SCRIPT_DIR}/birth_year_histogram.png" -c
