SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
docker run -it --rm -v "${SCRIPT_DIR}/..:/working" matching_jms_and_mg /working/pipeline.sh
