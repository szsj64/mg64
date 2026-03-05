SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
docker build -t matching_jms_and_mg . -f "${SCRIPT_DIR}/Dockerfile"
