#!/bin/bash
set -e

INPUT_PATH="mg1964.txt"

OUTPUT_PATH="mg1964.xlsx"
SORT=false
USE_SOURCES=false

while getopts "i:o:sf" opt; do
  case $opt in
    i)
      INPUT_PATH="$OPTARG"
      ;;
    o)
      OUTPUT_PATH="$OPTARG"
      ;;
    s)
      SORT=true
      ;;
    f)
      USE_SOURCES=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

echo "Exporting data..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

EXTRA_ARGS=""
[ "$SORT" = true ] && EXTRA_ARGS="${EXTRA_ARGS} -s"
[ "$USE_SOURCES" = true ] && EXTRA_ARGS="${EXTRA_ARGS} -f"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${SCRIPT_DIR}/export_xlsx_partial.py" -i "${INPUT_PATH}" -o "${OUTPUT_PATH}" -v ${EXTRA_ARGS}

echo "Exporting completed."