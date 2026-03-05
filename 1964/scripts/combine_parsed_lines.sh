#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/config.sh"

OVERWRITE=false
INPUT_DIRECTORY=parsed
OUTPUT_PATH=mg1964.txt

while getopts "i:o:w" opt; do
  case $opt in
    i)
      INPUT_DIRECTORY="$OPTARG"
      ;;
    o)
      OUTPUT_PATH="$OPTARG"
      ;;
    w)
      OVERWRITE=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

echo "Combining parsed lines..."

printf "%s.txt\n" "${COMPONENTS[@]/#/$INPUT_DIRECTORY/}" | xargs -d '\n' cat > "${OUTPUT_PATH}"

echo "Combining parsed lines completed."
