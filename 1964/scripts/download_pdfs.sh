#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${SCRIPT_DIR}/config.sh"

USE_ARCHIVED_PDFS=false
OVERWRITE=false
OUTPUT_DIRECTORY=pdfs

while getopts "ao:w" opt; do
  case $opt in
    a)
      USE_ARCHIVED_PDFS=true
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

PREFIX=""
if [ "$USE_ARCHIVED_PDFS" = true ]; then
    PREFIX="https://web.archive.org/web/1/"
fi

mkdir -p "${OUTPUT_DIRECTORY}"

echo "Downloading PDFs..."

for COMPONENT in "${COMPONENTS[@]}"; do
    OUTPUT_PATH="${OUTPUT_DIRECTORY}/${COMPONENT}.pdf"
    if [ ! -e "${OUTPUT_PATH}" ] || [ "$OVERWRITE" = true ]; then
        URL="${PREFIX}https://www.muzejgenocida.rs/images/ZrtvePub/${COMPONENT}.pdf"
        wget -P "${OUTPUT_DIRECTORY}" "$URL"
    else
        echo "Skipping ${COMPONENT}."
    fi
done

echo "Downloading completed."
