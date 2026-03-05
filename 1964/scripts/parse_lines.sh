#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/config.sh"

OVERWRITE=false
INPUT_DIRECTORY=extracted
OUTPUT_DIRECTORY=parsed

while getopts "i:o:w" opt; do
  case $opt in
    i)
      INPUT_DIRECTORY="$OPTARG"
      ;;
    o)
      OUTPUT_DIRECTORY="$OPTARG"
      ;;
    w)
      OVERWRITE=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

mkdir -p "${OUTPUT_DIRECTORY}"

echo "Parsing from lines..."

for COMPONENT in "${COMPONENTS[@]}"; do
    OUTPUT_PATH="${OUTPUT_DIRECTORY}/${COMPONENT}.txt"
    LOCATIONS_INPUT_PATH="${INPUT_DIRECTORY}/${COMPONENT}_locations.txt"
    if [ ! -e "${OUTPUT_PATH}" ] || [ "$OVERWRITE" = true ]; then
        INPUT_PATH="${INPUT_DIRECTORY}/${COMPONENT}.txt"
        echo "${COMPONENT}:"
        python3 "${SCRIPT_DIR}/parse_lines.py" -i "${INPUT_PATH}" -l "${LOCATIONS_INPUT_PATH}" -o "${OUTPUT_PATH}" -v
    else
        echo "Skipping ${COMPONENT}."
    fi
done

echo "Parsing completed."
