#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

##"${SCRIPT_DIR}/get_table.sh"
#"${SCRIPT_DIR}/match.sh"

"${SCRIPT_DIR}/match.sh" --ld -b 2 -t 0 -o matches_ld_0.txt
"${SCRIPT_DIR}/match.sh" --ld -b 2 -t 1 -o matches_ld_1.txt
"${SCRIPT_DIR}/match.sh" --ld -b 2 -t 2 -o matches_ld_2.txt
"${SCRIPT_DIR}/match.sh" --ld -b 2 -t 3 -o matches_ld_3.txt
"${SCRIPT_DIR}/match.sh" --ld -b 2 -t 4 -o matches_ld_4.txt
"${SCRIPT_DIR}/match.sh" --ld -b 2 -t 5 -o matches_ld_5.txt
