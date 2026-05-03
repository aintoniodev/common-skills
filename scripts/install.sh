#!/usr/bin/env bash

set -euo pipefail

REPO_URL="https://github.com/warpdotdev/common-skills/"
DEST_SKILLS_DIR="${HOME}/.agents/skills"
CLONE_DIR=""
CLEANUP_CLONE_DIR=0

usage() {
  cat <<EOF
Usage: ./install.sh [--clone-dir DIR]

Clone common-skills and copy its skills into ${DEST_SKILLS_DIR}.

Options:
  -d, --clone-dir DIR   Directory to clone common-skills into.
  -h, --help            Show this help message.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--clone-dir)
      if [[ $# -lt 2 || -z "$2" ]]; then
        echo "error: --clone-dir requires a directory" >&2
        exit 1
      fi
      CLONE_DIR="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "${CLONE_DIR}" ]]; then
  CLONE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/common-skills.XXXXXX")"
  CLEANUP_CLONE_DIR=1
fi

cleanup() {
  if [[ "${CLEANUP_CLONE_DIR}" -eq 1 ]]; then
    rm -rf "${CLONE_DIR}"
  fi
}

trap cleanup EXIT

if [[ -e "${CLONE_DIR}" ]]; then
  if [[ ! -d "${CLONE_DIR}" ]]; then
    echo "error: clone path already exists and is not a directory: ${CLONE_DIR}" >&2
    exit 1
  fi

  if [[ -n "$(ls -A "${CLONE_DIR}")" ]]; then
    echo "error: clone directory already exists and is not empty: ${CLONE_DIR}" >&2
    exit 1
  fi
fi

mkdir -p "${CLONE_DIR}"
git clone --depth 1 "${REPO_URL}" "${CLONE_DIR}"

SOURCE_SKILLS_DIR="${CLONE_DIR}/.agents/skills"

if [[ ! -d "${SOURCE_SKILLS_DIR}" ]]; then
  echo "error: cloned repo does not contain ${SOURCE_SKILLS_DIR}" >&2
  exit 1
fi

mkdir -p "${DEST_SKILLS_DIR}"
cp -R "${SOURCE_SKILLS_DIR}/." "${DEST_SKILLS_DIR}/"

echo "Installed common-skills into ${DEST_SKILLS_DIR}"
echo "Installed skills:"
find "${SOURCE_SKILLS_DIR}" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort | while read -r skill_name; do
  echo "  - ${skill_name}"
done
