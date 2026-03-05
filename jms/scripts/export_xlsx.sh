#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT_PATH="jms.json"

OUTPUT_PATH="jms.xlsx"

while getopts "i:o:" opt; do
  case $opt in
    i)
      INPUT_PATH="$OPTARG"
      ;;
    o)
      OUTPUT_PATH="$OPTARG"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

echo "Exporting data..."

python3 "${SCRIPT_DIR}/export_xlsx.py" -i "${INPUT_PATH}" -o "${OUTPUT_PATH}" -v

echo "Exporting completed."
