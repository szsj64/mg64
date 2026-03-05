#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/config.sh"

INDIVIDUAL=false
SEPARATED=false
ALL=false
SORT=false
USE_SOURCES=false

while getopts "isaSf" opt; do
  case $opt in
    i)
      INDIVIDUAL=true
      ;;
    s)
      SEPARATED=true
      ;;
    a)
      ALL=true
      ;;
    S)
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

EXTRA_ARGS=""
[ "$SORT" = true ] && EXTRA_ARGS="${EXTRA_ARGS} -s"
[ "$USE_SOURCES" = true ] && EXTRA_ARGS="${EXTRA_ARGS} -f"

OUTPUT_DIRECTORY="${SCRIPT_DIR}/../data/xlsx"
mkdir -p "${OUTPUT_DIRECTORY}"

if [ "$INDIVIDUAL" = true ]; then
  for COMPONENT in "${COMPONENTS[@]}"; do
    echo "${COMPONENT}:"
    "${SCRIPT_DIR}/export_xlsx_partial.sh" -i "${SCRIPT_DIR}/../data/parsed/${COMPONENT}.txt" -o "${OUTPUT_DIRECTORY}/${COMPONENT}.xlsx" ${EXTRA_ARGS}
  done
fi

if [ "$SEPARATED" = true ]; then
  "${SCRIPT_DIR}/export_xlsx_separated.sh" -o "${OUTPUT_DIRECTORY}/mg1964_separated.xlsx" ${EXTRA_ARGS}
fi

if [ "$ALL" = true ]; then
  "${SCRIPT_DIR}/export_xlsx_partial.sh" -i "${SCRIPT_DIR}/../data/parsed/mg1964.txt" -o "${OUTPUT_DIRECTORY}/mg1964.xlsx" ${EXTRA_ARGS}
fi

if [ "$INDIVIDUAL" = false ] && [ "$SEPARATED" = false ] && [ "$ALL" = false ]; then
  echo "Usage: $0 -i | -s | -a [ -S ] [ -f ]" >&2
  echo "  -i individual  -s separated  -a all  -S sort  -f sources" >&2
  exit 1
fi
