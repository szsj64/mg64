#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"${SCRIPT_DIR}/download_pages.sh" -i "${SCRIPT_DIR}/../data/45409.txt" -o "${SCRIPT_DIR}/../data/45409"
"${SCRIPT_DIR}/extract_json.sh" -i "${SCRIPT_DIR}/../data/45409" -o "${SCRIPT_DIR}/../data/jms.json"
"${SCRIPT_DIR}/export_xlsx.sh" -i "${SCRIPT_DIR}/../data/jms.json" -o "${SCRIPT_DIR}/../data/jms.xlsx"