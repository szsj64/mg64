#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

OUTPUT="zbl"
OVERWRITE=""
BRUTE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -w|--overwrite)
            OVERWRITE="-w"
            shift
            ;;
        -b|--brute)
            BRUTE="-b"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

python3 "${SCRIPT_DIR}/get_pages.py" -o "${OUTPUT}" -v ${OVERWRITE} ${BRUTE}
