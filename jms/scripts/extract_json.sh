#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT_DIRECTORY=45409

OUTPUT_PATH="jms.json"

while getopts "i:o:" opt; do
  case $opt in
    i)
      INPUT_DIRECTORY="$OPTARG"
      ;;
    o)
      OUTPUT_PATH="$OPTARG"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

echo "Extracting data..."

python3 "${SCRIPT_DIR}/extract_json.py" -i "${INPUT_DIRECTORY}" -o "${OUTPUT_PATH}" -v

echo "Extraction completed."