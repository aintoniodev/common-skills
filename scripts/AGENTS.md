# Agent guidance for common-skills scripts
This directory contains self-contained scripts for installing, removing, and verifying common agent skills in consuming repositories. The scripts are intended to be copied into other repositories, run from that repository root, run with `--repo-root <path>`, or executed directly from the raw GitHub URL.
## Scripts
### `install_common_skills`
Installs or updates the common skills from `warpdotdev/common-skills`.
- Uses `skills-lock.json` when it already exists.
- Creates `skills-lock.json` from `warpdotdev/common-skills` when it is missing.
- Uses the `skills` CLI with agent target `warp`.
- Uses `COMMON_SKILL_SELECTOR="*"` for first-time lock creation so every valid skill in the common-skills repo is installed.
- Supports project installs into `.agents/skills` and global installs into `~/.agents/skills`.
- Writes a lock hash stamp after a successful install so `--if-needed` can skip no-op installs.
- Verifies installed contents after successful install and skip paths.
- Supports `--verify-only` to verify without installing.
### `remove_common_skills`
Removes skills listed in `skills-lock.json` from the selected target.
- Removes project skills by following locked `.agents/skills/<name>/SKILL.md` paths.
- Removes global skills by locked skill name from `~/.agents/skills/<name>`.
- Removes the install stamp for the selected target.
- Can remove `skills-lock.json` with `--clear-lock`.
### Verification
`install_common_skills --verify-only` verifies the installed common skills match `skills-lock.json`.
- Requires `skills-lock.json`.
- Fails if the locked skills are installed in both project and global targets.
- Fails if the locked skills are not installed in either target.
- Recomputes each installed skill directory hash and compares it to the lock file.
## Install targets
The install and remove scripts support two targets:
- `project`: repository-local `.agents/skills`
- `global`: user-level `~/.agents/skills`
The installer refuses to install into one target when the other target already contains the locked common skills. This prevents duplicate common-skill definitions from being present at both project and global scope.
## Lock file and stamps
`skills-lock.json` is the source of truth after it exists. Do not reintroduce fixed lists of common skill names into these scripts.
The installer writes a stamp containing the current lock hash:
- Project stamp: git path `warp/common-skills-lock.hash`, falling back to `.agents/skills/.common-skills-lock.hash` outside git.
- Global stamp: `~/.agents/warp/common-skills-lock.hash`.
`--if-needed` skips installation only when the stamp matches `skills-lock.json` and all locked skills are present in the selected target.
## Editing rules
- Keep skill selection dynamic. First-time installs should continue to install all valid common skills from the source repo.
- Prefer lock-file-driven behavior whenever `skills-lock.json` exists.
- Keep executable scripts self-contained so they can be run via `curl | bash`.
- Keep project and global target behavior symmetric unless a difference is required by the `skills` CLI.
- Preserve path safety checks before deleting skill directories.
- After edits, run `bash -n scripts/install_common_skills scripts/remove_common_skills`.
- For behavior changes, test in a temporary repo before relying on the scripts in a real checkout.
