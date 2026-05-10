# Common skills scripts
These scripts help consuming repositories install, remove, and verify shared agent skills from `warpdotdev/common-skills`.
## Files
- `install_common_skills`: installs or updates common skills, then verifies the installed contents.
- `remove_common_skills`: removes installed common skills from a selected target.
## Quick start
Install common skills into the current checkout:
```sh
scripts/install_common_skills --project
```
Install common skills globally:
```sh
scripts/install_common_skills --global
```
Install only when the lock hash has changed or a locked skill is missing:
```sh
scripts/install_common_skills --if-needed --non-interactive
```
Verify the installed skills without installing:
```sh
scripts/install_common_skills --verify-only
```
Remove installed common skills:
```sh
scripts/remove_common_skills --project
```
## Install script
`install_common_skills` installs common agent skills from `warpdotdev/common-skills`.
When `skills-lock.json` is missing, the script creates it by running the `skills` CLI against the source repo and selecting all valid skills. This is intentionally dynamic: the script should not hardcode a fixed list of common skill names.
When `skills-lock.json` already exists, the script installs from the lock file:
- Project target: `npx --yes skills@1.5.6 experimental_install`
- Global target: `npx --yes skills@1.5.6 add warpdotdev/common-skills --global --agent warp --skill <locked skills> --yes --copy`
The script supports:
- `--repo-root <path>`: repository containing `skills-lock.json`.
- `--project`: install into `.agents/skills`.
- `--global`: install into `~/.agents/skills`.
- `--if-needed`: skip when the stamp matches the lock and locked skills are present.
- `--prompt-for-target`: prompt for project/global when no explicit target is set.
- `--non-interactive`: do not prompt; use detected/default target.
- `--force`: install even if already up to date.
- `--quiet`: suppress no-op output.
- `--verify-only`: verify installed skills match `skills-lock.json` without installing.
Successful install and skip paths verify that exactly one install target contains the locked common skills and that each installed skill matches `skills-lock.json`.
## Remove script
`remove_common_skills` removes common agent skills listed in `skills-lock.json`.
The script supports:
- `--repo-root <path>`: repository containing `skills-lock.json`.
- `--project`: remove from `.agents/skills`.
- `--global`: remove from `~/.agents/skills`.
- `--clear-lock`: remove `skills-lock.json` after removing locked skills.
The remove script only deletes paths derived from the lock file and includes path checks before removing project skill directories.
## Verification
`install_common_skills --verify-only` checks that exactly one install target contains the locked common skills and that each installed skill matches `skills-lock.json`.
Verification also runs after successful install and skip paths.
Verification fails if:
- `skills-lock.json` is missing.
- Locked skills are installed in both project and global targets.
- Locked skills are missing from both targets.
- Any installed skill directory hash differs from the lock file.
## Environment variables
- `WARP_SKIP_COMMON_SKILLS_INSTALL=1`: skip installation.
- `WARP_COMMON_SKILLS_INSTALL_TARGET=project|global`: default install or removal target.
- `WARP_COMMON_SKILLS_TARGET_REPO_ROOT=/path/to/repo`: repository containing `skills-lock.json` and project-local `.agents/skills`.
## Lock hash stamps
After a successful install, `install_common_skills` writes a stamp with the current `skills-lock.json` hash.
- Project installs use git path `warp/common-skills-lock.hash`, or `.agents/skills/.common-skills-lock.hash` when git metadata is unavailable.
- Global installs use `~/.agents/warp/common-skills-lock.hash`.
The stamp lets `--if-needed` avoid reinstalling when the lock file and installed skills are already current.
