#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

JMS_INPUT_PATH="${SCRIPT_DIR}/../jms/data/jms.json"
JMS_LINKS_PATH="${SCRIPT_DIR}/../jms/data/45409.txt"
MG1964_INPUT_PATH="${SCRIPT_DIR}/../1964/data/parsed/mg1964.txt"
OUTPUT_PATH="${SCRIPT_DIR}/../matched.xlsx"

python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -o "${OUTPUT_PATH}" -g -v -l -r report.txt -M 0 -F -Y -P -n -e -a -s -d -O matched.txt

python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_0.txt -M 0 -F -Y -P -n -e -a -s -d -O matched_M_0.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_1.txt -M 1 -F -Y -P -n -e -a -s -d -O matched_M_1.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_2.txt -M 2 -F -Y -P -n -e -a -s -d -O matched_M_2.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_3.txt -M 3 -F -Y -P -n -e -a -s -d -O matched_M_3.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_4.txt -M 4 -F -Y -P -n -e -a -s -d -O matched_M_4.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_5.txt -M 5 -F -Y -P -n -e -a -s -d -O matched_M_5.txt

python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_0_b_2_ld_1_ff.txt -M 0 -F -Y -P -n -e -a -s -d --ld -b 2 -t 1 --ff -O matched_M_0_b_2_ld_1_ff.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_0_b_2_ld_2_ff.txt -M 0 -F -Y -P -n -e -a -s -d --ld -b 2 -t 2 --ff -O matched_M_0_b_2_ld_2_ff.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_0_b_2_ld_3_ff.txt -M 0 -F -Y -P -n -e -a -s -d --ld -b 2 -t 3 --ff -O matched_M_0_b_2_ld_3_ff.txt

python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_1_b_2_ld_1_ff.txt -M 1 -F -Y -P -n -e -a -s -d --ld -b 2 -t 1 --ff -O matched_M_1_b_2_ld_1_ff.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_1_b_2_ld_2_ff.txt -M 1 -F -Y -P -n -e -a -s -d --ld -b 2 -t 2 --ff -O matched_M_1_b_2_ld_2_ff.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_1_b_2_ld_3_ff.txt -M 1 -F -Y -P -n -e -a -s -d --ld -b 2 -t 3 --ff -O matched_M_1_b_2_ld_3_ff.txt

python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_2_b_2_ld_1_ff.txt -M 2 -F -Y -P -n -e -a -s -d --ld -b 2 -t 1 --ff -O matched_M_2_b_2_ld_1_ff.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_2_b_2_ld_2_ff.txt -M 2 -F -Y -P -n -e -a -s -d --ld -b 2 -t 2 --ff -O matched_M_2_b_2_ld_2_ff.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_2_b_2_ld_3_ff.txt -M 2 -F -Y -P -n -e -a -s -d --ld -b 2 -t 3 --ff -O matched_M_2_b_2_ld_3_ff.txt

python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_3_b_2_ld_1_ff.txt -M 3 -F -Y -P -n -e -a -s -d --ld -b 2 -t 1 --ff -O matched_M_3_b_2_ld_1_ff.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_3_b_2_ld_2_ff.txt -M 3 -F -Y -P -n -e -a -s -d --ld -b 2 -t 2 --ff -O matched_M_3_b_2_ld_2_ff.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_3_b_2_ld_3_ff.txt -M 3 -F -Y -P -n -e -a -s -d --ld -b 2 -t 3 --ff -O matched_M_3_b_2_ld_3_ff.txt

python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_4_b_2_ld_1_ff.txt -M 4 -F -Y -P -n -e -a -s -d --ld -b 2 -t 1 --ff -O matched_M_4_b_2_ld_1_ff.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_4_b_2_ld_2_ff.txt -M 4 -F -Y -P -n -e -a -s -d --ld -b 2 -t 2 --ff -O matched_M_4_b_2_ld_2_ff.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_4_b_2_ld_3_ff.txt -M 4 -F -Y -P -n -e -a -s -d --ld -b 2 -t 3 --ff -O matched_M_4_b_2_ld_3_ff.txt

python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_5_b_2_ld_1_ff.txt -M 5 -F -Y -P -n -e -a -s -d --ld -b 2 -t 1 --ff -O matched_M_5_b_2_ld_1_ff.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_5_b_2_ld_2_ff.txt -M 5 -F -Y -P -n -e -a -s -d --ld -b 2 -t 2 --ff -O matched_M_5_b_2_ld_2_ff.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_M_5_b_2_ld_3_ff.txt -M 5 -F -Y -P -n -e -a -s -d --ld -b 2 -t 3 --ff -O matched_M_5_b_2_ld_3_ff.txt


python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_fs_ld_0.txt -M 0 -F -Y -P -n -s -d --ld -b 2 -t 0 --ff --fs --score -E estimation.txt --fs-review review_ld_0.tsv -O matched_fs_ld_0.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_fs_ld_1.txt -M 0 -F -Y -P -n -s -d --ld -b 2 -t 1 --ff --fs --score -E estimation.txt --fs-review review_ld_1.tsv -O matched_fs_ld_1.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_fs_ld_2.txt -M 0 -F -Y -P -n -s -d --ld -b 2 -t 2 --ff --fs --score -E estimation.txt --fs-review review_ld_2.tsv -O matched_fs_ld_2.txt
python3 "${SCRIPT_DIR}/match.py" -j "${JMS_INPUT_PATH}" -u "${JMS_LINKS_PATH}" -m "${MG1964_INPUT_PATH}" -g -v -l -r report_fs_ld_3.txt -M 0 -F -Y -P -n -s -d --ld -b 2 -t 3 --ff --fs --score -E estimation.txt --fs-review review_ld_3.tsv -O matched_fs_ld_3.txt



