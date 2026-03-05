#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/config.sh"

OUTPUT_PATH="mg1964_separated.xlsx"
SORT=false
USE_SOURCES=false

while getopts "o:sf" opt; do
  case $opt in
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

COMPONENT_NAMES=(Slovenia "Croatia" "Bosnia and Herzegovina" Montenegro Macedonia Serbia Kosovo Vojvodina)
COMPONENTS_PATHS=()
for c in "${COMPONENTS[@]}"; do
  COMPONENTS_PATHS+=("${SCRIPT_DIR}/../data/parsed/${c}.txt")
done

EXTRA_ARGS=""
[ "$SORT" = true ] && EXTRA_ARGS="${EXTRA_ARGS} -s"
[ "$USE_SOURCES" = true ] && EXTRA_ARGS="${EXTRA_ARGS} -f"

python3 "${SCRIPT_DIR}/export_xlsx_combined.py" -v -o "${OUTPUT_PATH}" ${EXTRA_ARGS} "${COMPONENTS_PATHS[@]}" "${COMPONENT_NAMES[@]}"
