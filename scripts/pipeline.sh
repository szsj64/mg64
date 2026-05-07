#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

JMS_INPUT_PATH="${SCRIPT_DIR}/../jms/data/jms.json"
JMS_LINKS_PATH="${SCRIPT_DIR}/../jms/data/45409.txt"
MG1964_INPUT_PATH="${SCRIPT_DIR}/../1964/data/parsed/mg1964.txt"
OUTPUT_PATH="${SCRIPT_DIR}/../matched.xlsx"

#python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -o "${OUTPUT_PATH}" -g -v -l -r report.txt
#python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report.txt -M 0 -F -Y -P -n -e -a -s

python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -o "${OUTPUT_PATH}" -g -v -l -r report.txt -M 0 -F -Y -P -n -e -a -s -d -O matched.txt

"${SCRIPT_DIR}/create_plot_inputs.sh"
"${SCRIPT_DIR}/create_plots.sh"

#python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report.txt -M 0 -F -Y -P -n -e -a -s -d -O matched.txt
#python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report.txt -M 0 -F -Y -P -n -e -a -s -d --ld -b 3 -O matched2.txt
#python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report.txt -M 0 -F -Y -P -n -e -a -s -d --ld -b 3 -t 1 -O matched_ld_1.txt
#python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report.txt -M 0 -F -Y -P -n -e -a -s -d --ld -b 3 -t 1 --ff -O matched_ld_1_ff.txt
#python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report.txt -M 0 -F -Y -P -n -e -a -s -d --ld -b 3 -t 2 -O matched_ld_2.txt
#python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report.txt -M 0 -F -Y -P -n -e -a -s -d --ld -b 3 -t 2 --ff -O matched_ld_2_ff.txt

#python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report.txt -M 0 -F -Y -P -n -s -d --ld -b 3 --ff --fs --score --fs-review review.tsv -O matched_fs.txt
