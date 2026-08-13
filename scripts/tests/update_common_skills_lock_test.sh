#!/usr/bin/env bash
# Regression tests for scripts/update_common_skills_lock.
#
# Runs the real script against a fake `npx` (scripts/tests/fake-bin/npx) that
# deterministically models `skills add ... --copy` from a local fixture
# directory, so these tests need no network access and don't depend on the
# real warpdotdev/common-skills repo's current contents.
#
# Usage: scripts/tests/update_common_skills_lock_test.sh
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
UPDATE_SCRIPT="${REPO_ROOT}/scripts/update_common_skills_lock"
FAKE_BIN_DIR="${SCRIPT_DIR}/fake-bin"
COMMON_SKILLS_SOURCE="warpdotdev/common-skills"
FOREIGN_SOURCE="someorg/other-skills-repo"

WORK_DIR=""
FAILURES=0

cleanup() {
  if [[ -n "${WORK_DIR}" ]]; then
    rm -rf "${WORK_DIR}"
  fi
}
trap cleanup EXIT

fail() {
  echo "FAIL: $1" >&2
  FAILURES=$((FAILURES + 1))
}

pass() {
  echo "PASS: $1"
}

# write_skill <source_dir> <name>
# Creates a minimal valid SKILL.md for <name> under <source_dir>.
write_skill() {
  local dir="$1/$2"
  mkdir -p "${dir}"
  cat > "${dir}/SKILL.md" <<EOF
---
name: $2
description: Test skill $2 used by update_common_skills_lock_test.sh.
---
# $2
Body for $2.
EOF
}

# write_initial_lock <lock_file> <skill_names...>
# Writes a downstream skills-lock.json with one entry per <skill_names> from
# ${COMMON_SKILLS_SOURCE}, plus one fixed entry from ${FOREIGN_SOURCE} that
# every assertion below expects to survive untouched.
write_initial_lock() {
  local lock_file="$1"
  shift
  node - "${lock_file}" "${COMMON_SKILLS_SOURCE}" "${FOREIGN_SOURCE}" "$@" <<'NODE'
const fs = require("fs");

const lockFile = process.argv[2];
const source = process.argv[3];
const foreignSource = process.argv[4];
const names = process.argv.slice(5);

const skills = {};
for (const name of names) {
  skills[name] = {
    source,
    sourceType: "github",
    skillPath: `.agents/skills/${name}/SKILL.md`,
    computedHash: `placeholder-hash-for-${name}`,
  };
}
skills["hand-added"] = {
  source: foreignSource,
  sourceType: "github",
  skillPath: ".agents/skills/hand-added/SKILL.md",
  computedHash: "placeholder-hash-for-hand-added",
};

const sorted = {};
for (const name of Object.keys(skills).sort()) {
  sorted[name] = skills[name];
}
fs.writeFileSync(lockFile, JSON.stringify({ version: 1, skills: sorted }, null, 2) + "\n");
NODE
}

# run_update <repo_root> <source_dir>
# Runs the real script with the fake npx on PATH ahead of the real one.
run_update() {
  local repo_root="$1"
  local source_dir="$2"
  FAKE_NPX_SOURCE_DIR="${source_dir}" PATH="${FAKE_BIN_DIR}:${PATH}" "${UPDATE_SCRIPT}" --repo-root "${repo_root}"
}

# lock_has_key <lock_file> <name>
lock_has_key() {
  node -e '
const fs = require("fs");
const lock = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
process.exit(Object.prototype.hasOwnProperty.call(lock.skills || {}, process.argv[2]) ? 0 : 1);
' "$1" "$2"
}

# lock_entry_matches <lock_file> <name> <expected_source> <expected_skill_path>
lock_entry_matches() {
  node -e '
const fs = require("fs");
const lock = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
const entry = (lock.skills || {})[process.argv[2]];
if (!entry) process.exit(1);
process.exit(entry.source === process.argv[3] && entry.skillPath === process.argv[4] ? 0 : 1);
' "$1" "$2" "$3" "$4"
}

test_rename() {
  local name="rename: stale entry pruned, renamed entry added, siblings and foreign entry untouched"
  WORK_DIR="$(mktemp -d)"
  local source_dir="${WORK_DIR}/source"
  local repo_dir="${WORK_DIR}/repo"
  mkdir -p "${source_dir}" "${repo_dir}"

  write_skill "${source_dir}" alpha
  write_skill "${source_dir}" beta
  write_skill "${source_dir}" gamma
  write_initial_lock "${repo_dir}/skills-lock.json" alpha beta gamma

  mv "${source_dir}/alpha" "${source_dir}/alpha-renamed"
  sed -i 's/name: alpha/name: alpha-renamed/' "${source_dir}/alpha-renamed/SKILL.md"

  if ! run_update "${repo_dir}" "${source_dir}" >/dev/null; then
    fail "${name} (script exited nonzero)"
    rm -rf "${WORK_DIR}"
    return
  fi

  local lock_file="${repo_dir}/skills-lock.json"
  if lock_has_key "${lock_file}" alpha; then
    fail "${name} (stale 'alpha' entry survived)"
  elif ! lock_entry_matches "${lock_file}" alpha-renamed "${COMMON_SKILLS_SOURCE}" ".agents/skills/alpha-renamed/SKILL.md"; then
    fail "${name} ('alpha-renamed' entry missing or wrong)"
  elif ! lock_entry_matches "${lock_file}" beta "${COMMON_SKILLS_SOURCE}" ".agents/skills/beta/SKILL.md"; then
    fail "${name} ('beta' entry missing or wrong)"
  elif ! lock_entry_matches "${lock_file}" gamma "${COMMON_SKILLS_SOURCE}" ".agents/skills/gamma/SKILL.md"; then
    fail "${name} ('gamma' entry missing or wrong)"
  elif ! lock_entry_matches "${lock_file}" hand-added "${FOREIGN_SOURCE}" ".agents/skills/hand-added/SKILL.md"; then
    fail "${name} (foreign 'hand-added' entry missing or modified)"
  else
    pass "${name}"
  fi

  rm -rf "${WORK_DIR}"
  WORK_DIR=""
}

test_plain_deletion() {
  local name="plain deletion: stale entry pruned, siblings and foreign entry untouched"
  WORK_DIR="$(mktemp -d)"
  local source_dir="${WORK_DIR}/source"
  local repo_dir="${WORK_DIR}/repo"
  mkdir -p "${source_dir}" "${repo_dir}"

  write_skill "${source_dir}" alpha
  write_skill "${source_dir}" beta
  write_skill "${source_dir}" gamma
  write_initial_lock "${repo_dir}/skills-lock.json" alpha beta gamma

  rm -rf "${source_dir}/gamma"

  if ! run_update "${repo_dir}" "${source_dir}" >/dev/null; then
    fail "${name} (script exited nonzero)"
    rm -rf "${WORK_DIR}"
    return
  fi

  local lock_file="${repo_dir}/skills-lock.json"
  if lock_has_key "${lock_file}" gamma; then
    fail "${name} (stale 'gamma' entry survived)"
  elif ! lock_entry_matches "${lock_file}" alpha "${COMMON_SKILLS_SOURCE}" ".agents/skills/alpha/SKILL.md"; then
    fail "${name} ('alpha' entry missing or wrong)"
  elif ! lock_entry_matches "${lock_file}" beta "${COMMON_SKILLS_SOURCE}" ".agents/skills/beta/SKILL.md"; then
    fail "${name} ('beta' entry missing or wrong)"
  elif ! lock_entry_matches "${lock_file}" hand-added "${FOREIGN_SOURCE}" ".agents/skills/hand-added/SKILL.md"; then
    fail "${name} (foreign 'hand-added' entry missing or modified)"
  else
    pass "${name}"
  fi

  rm -rf "${WORK_DIR}"
  WORK_DIR=""
}

test_idempotence() {
  local name="idempotence: second run is byte-identical and reports up to date"
  WORK_DIR="$(mktemp -d)"
  local source_dir="${WORK_DIR}/source"
  local repo_dir="${WORK_DIR}/repo"
  mkdir -p "${source_dir}" "${repo_dir}"

  write_skill "${source_dir}" alpha
  write_skill "${source_dir}" beta
  write_initial_lock "${repo_dir}/skills-lock.json" alpha beta

  if ! run_update "${repo_dir}" "${source_dir}" >/dev/null; then
    fail "${name} (first run exited nonzero)"
    rm -rf "${WORK_DIR}"
    return
  fi

  local lock_file="${repo_dir}/skills-lock.json"
  local first_run_copy="${WORK_DIR}/skills-lock.first.json"
  cp "${lock_file}" "${first_run_copy}"

  local second_run_output
  if ! second_run_output="$(run_update "${repo_dir}" "${source_dir}")"; then
    fail "${name} (second run exited nonzero)"
    rm -rf "${WORK_DIR}"
    return
  fi

  if [[ "${second_run_output}" != *"already up to date"* ]]; then
    fail "${name} (second run did not report already up to date; got: ${second_run_output})"
  elif ! cmp -s "${first_run_copy}" "${lock_file}"; then
    fail "${name} (lock file changed on the second run)"
  else
    pass "${name}"
  fi

  rm -rf "${WORK_DIR}"
  WORK_DIR=""
}

test_fails_closed_on_empty_result() {
  local name="fails closed: an empty regenerated lock aborts and leaves the existing lock untouched"
  WORK_DIR="$(mktemp -d)"
  local source_dir="${WORK_DIR}/source"
  local repo_dir="${WORK_DIR}/repo"
  mkdir -p "${source_dir}" "${repo_dir}"

  write_skill "${source_dir}" alpha
  write_skill "${source_dir}" beta
  write_initial_lock "${repo_dir}/skills-lock.json" alpha beta

  local lock_file="${repo_dir}/skills-lock.json"
  local before_copy="${WORK_DIR}/skills-lock.before.json"
  cp "${lock_file}" "${before_copy}"

  local exit_code=0
  FAKE_NPX_SOURCE_DIR="${source_dir}" FAKE_NPX_MODE=broken-empty-lock PATH="${FAKE_BIN_DIR}:${PATH}" \
    "${UPDATE_SCRIPT}" --repo-root "${repo_dir}" >/dev/null 2>&1 || exit_code=$?

  if [[ "${exit_code}" -eq 0 ]]; then
    fail "${name} (script exited 0 instead of failing)"
  elif ! cmp -s "${before_copy}" "${lock_file}"; then
    fail "${name} (existing lock was modified despite the failure)"
  else
    pass "${name}"
  fi

  rm -rf "${WORK_DIR}"
  WORK_DIR=""
}

test_fails_closed_on_no_candidate() {
  local name="fails closed: no candidate lock produced at all aborts and leaves the existing lock untouched"
  WORK_DIR="$(mktemp -d)"
  local source_dir="${WORK_DIR}/source"
  local repo_dir="${WORK_DIR}/repo"
  mkdir -p "${source_dir}" "${repo_dir}"

  write_skill "${source_dir}" alpha
  write_skill "${source_dir}" beta
  write_initial_lock "${repo_dir}/skills-lock.json" alpha beta

  local lock_file="${repo_dir}/skills-lock.json"
  local before_copy="${WORK_DIR}/skills-lock.before.json"
  cp "${lock_file}" "${before_copy}"

  local exit_code=0
  FAKE_NPX_SOURCE_DIR="${source_dir}" FAKE_NPX_MODE=broken-empty PATH="${FAKE_BIN_DIR}:${PATH}" \
    "${UPDATE_SCRIPT}" --repo-root "${repo_dir}" >/dev/null 2>&1 || exit_code=$?

  if [[ "${exit_code}" -eq 0 ]]; then
    fail "${name} (script exited 0 instead of failing)"
  elif ! cmp -s "${before_copy}" "${lock_file}"; then
    fail "${name} (existing lock was modified despite the failure)"
  else
    pass "${name}"
  fi

  rm -rf "${WORK_DIR}"
  WORK_DIR=""
}

test_rename
test_plain_deletion
test_idempotence
test_fails_closed_on_empty_result
test_fails_closed_on_no_candidate

if [[ "${FAILURES}" -gt 0 ]]; then
  echo "${FAILURES} test(s) failed." >&2
  exit 1
fi

echo "All tests passed."
