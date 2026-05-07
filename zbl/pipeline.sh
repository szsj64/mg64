#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"${SCRIPT_DIR}/get_pages.sh" -o pages
"${SCRIPT_DIR}/match.sh"
#"${SCRIPT_DIR}/match.sh" --ld -t 2 -b 2
