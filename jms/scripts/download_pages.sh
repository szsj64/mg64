#!/bin/bash
set -e

USE_ARCHIVED_VERSIONS=false

INPUT_PATH=45409.txt

OUTPUT_DIRECTORY=45409

DOWNLOADERS_COUNT=1

QUIET=""

WRITE=""

while getopts "ai:o:n:qw" opt; do
  case $opt in
    a)
      USE_ARCHIVED_VERSIONS=true
      ;;
    i)
      INPUT_PATH="$OPTARG"
      ;;
    o)
      OUTPUT_DIRECTORY="$OPTARG"
      ;;
    n)
      DOWNLOADERS_COUNT="$OPTARG"
      ;;
    q)
      QUIET=true
      ;;
    w)
      WRITE=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

PREFIX=""
if [ "$USE_ARCHIVED_VERSIONS" = true ]; then
    PREFIX="https://web.archive.org/web/1/"
fi

mkdir -p "${OUTPUT_DIRECTORY}"

echo "Downloading pages..."

tr -d '\r' < "${INPUT_PATH}" | nl -w1 -s' ' | xargs -P "${DOWNLOADERS_COUNT}" -n2 sh -c '[ -z "$3" ] && [ -f "$1/$4" ] && { echo "Skipping $4 (already exists)"; exit 0; }; echo "Downloading $4..."; wget ${0:+-q} -O "$1/$4" "$2$5"' "${QUIET}" "${OUTPUT_DIRECTORY}" "${PREFIX}" "${WRITE}"


echo "Downloading completed."