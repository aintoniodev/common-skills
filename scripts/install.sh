#!/usr/bin/env bash

set -euo pipefail

REPO_URL="https://github.com/warpdotdev/common-skills/"
DEST_SKILLS_DIR="${HOME}/.agents/skills"
CLONE_DIR=""
CLEANUP_CLONE_DIR=0

usage() {
  cat <<EOF
Usage: ./install.sh [--clone-dir DIR] [--dest-dir DIR]

Clone common-skills and copy its skills into ${DEST_SKILLS_DIR}.

Options:
  -d, --clone-dir DIR   Directory to clone common-skills into.
      --dest-dir DIR    Directory to install skills into.
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
    --dest-dir)
      if [[ $# -lt 2 || -z "$2" ]]; then
        echo "error: --dest-dir requires a directory" >&2
        exit 1
      fi
      DEST_SKILLS_DIR="$2"
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

should_overwrite_skill() {
  local skill_name="$1"
  local response=""

  while true; do
    read -r -p "Skill '${skill_name}' already exists. Overwrite it? [y/N] " response
    case "${response}" in
      [yY]|[yY][eE][sS])
        return 0
        ;;
      ""|[nN]|[nN][oO])
        return 1
        ;;
      *)
        echo "Please answer yes or no."
        ;;
    esac
  done
}

installed_skills=()
skipped_skills=()

while IFS= read -r skill_name; do
  source_skill_dir="${SOURCE_SKILLS_DIR}/${skill_name}"
  dest_skill_dir="${DEST_SKILLS_DIR}/${skill_name}"

  if [[ -e "${dest_skill_dir}" ]]; then
    if ! should_overwrite_skill "${skill_name}"; then
      skipped_skills+=("${skill_name}")
      continue
    fi

    rm -rf "${dest_skill_dir}"
  fi

  cp -R "${source_skill_dir}" "${dest_skill_dir}"
  installed_skills+=("${skill_name}")
done < <(find "${SOURCE_SKILLS_DIR}" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)

echo "Installed common-skills into ${DEST_SKILLS_DIR}"

if [[ "${#installed_skills[@]}" -gt 0 ]]; then
  echo "Installed skills:"
  printf '  - %s\n' "${installed_skills[@]}"
else
  echo "No skills installed."
fi

if [[ "${#skipped_skills[@]}" -gt 0 ]]; then
  echo "Skipped existing skills:"
  printf '  - %s\n' "${skipped_skills[@]}"
fi
