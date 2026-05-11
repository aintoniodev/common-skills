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
scripts/install_common_skills --project --if-needed --non-interactive
```
Verify the installed skills without installing:
```sh
scripts/install_common_skills --verify-only
```
Remove installed common skills:
```sh
scripts/remove_common_skills --project
```
## Invoking from client repositories
Client repositories do not need to vendor these scripts. `warpdotdev/warp#10617` adds a small `script/resolve_common_skills` wrapper to the Warp repo that resolves a script from this repository and forwards arguments to it.
The wrapper's default path executes the raw GitHub script through `curl`:
```sh
curl -fsSL "https://raw.githubusercontent.com/warpdotdev/common-skills/${WARP_COMMON_SKILLS_REF:-main}/scripts/install_common_skills" | bash -s -- --repo-root "${REPO_ROOT}" --if-needed --prompt-for-target
```
Warp's bootstrap and run scripts call the wrapper instead of calling `curl` directly:
```sh
./script/resolve_common_skills install_common_skills -- --repo-root "${REPO_ROOT}" --if-needed --prompt-for-target
```
With an explicit target, client repos pass the same installer flags they would pass locally:
```sh
./script/resolve_common_skills install_common_skills -- --repo-root "${REPO_ROOT}" --global --if-needed
./script/resolve_common_skills install_common_skills -- --repo-root "${REPO_ROOT}" --project --force
```
The resolver supports these development overrides:
- `WARP_COMMON_SKILLS_REF=<git-ref>`: fetch scripts from a branch, tag, or commit in `warpdotdev/common-skills`; also forwarded to the installer so missing-lock creation and interactive lock update checks use the same ref.
- `WARP_COMMON_SKILLS_SCRIPTS_DIR=/path/to/common-skills/scripts`: execute scripts from a local checkout or worktree instead of fetching from GitHub.
- `WARP_COMMON_SKILLS_RAW_BASE_URL=https://...`: override the raw URL base used by the resolver.
## Developing against these scripts from a client repo
For normal client-repo development, test the remote path first:
```sh
WARP_COMMON_SKILLS_REF=<your-common-skills-branch> ./script/bootstrap --install-common-skills-globally
WARP_COMMON_SKILLS_REF=<your-common-skills-branch> ./script/run --install-common-skills
```
Use `WARP_COMMON_SKILLS_SCRIPTS_DIR` when iterating on unpushed local script changes:
```sh
WARP_COMMON_SKILLS_SCRIPTS_DIR=/path/to/common-skills/scripts ./script/run --install-common-skills
```
Client repos should keep their own `skills-lock.json` checked in. Normal install flows use that lock as the source of truth; interactive flows may ask to update it when this repo would produce a different lock. Review and commit lock changes in the client repo separately from changes to this repo.
## Install script
`install_common_skills` installs common agent skills from `warpdotdev/common-skills`.
When `skills-lock.json` is missing, the script creates it by running the `skills` CLI against the source repo and selecting all valid skills. This is intentionally dynamic: the script should not hardcode a fixed list of common skill names. Set `WARP_COMMON_SKILLS_REF=<git-ref>` to create the lock from a branch, tag, or commit such as `warpdotdev/common-skills#my-branch`.
When `skills-lock.json` already exists and the script is running interactively, it checks whether `warpdotdev/common-skills` would produce an updated lock before prompting for a project/global install target. If `WARP_COMMON_SKILLS_REF` is set, the check uses that branch, tag, or commit as the candidate source. If a different lock is available, it asks before updating `skills-lock.json` and reinstalling from the updated lock. Non-interactive and verify-only runs skip this upstream update prompt and use the existing lock.
When `skills-lock.json` already exists, the script installs from the lock file:
- Project target: `npx --yes skills@1.5.6 experimental_install`
- Global target: `npx --yes skills@1.5.6 add warpdotdev/common-skills --global --agent warp --skill <locked skills> --yes --copy`
The script supports:
- `--repo-root <path>`: repository containing `skills-lock.json`.
- `--project`: install into `.agents/skills`.
- `--global`: install into `~/.agents/skills`.
- `--if-needed`: skip when the stamp matches the lock and locked skills are present.
- `--prompt-for-target`: prompt for project/global when no explicit target is set.
- `--non-interactive`: do not prompt; fail when no target is explicit.
- `--force`: install even if already up to date.
- `--quiet`: suppress no-op output.
- `--verify-only`: verify installed skills match `skills-lock.json` without installing.
Successful install and skip paths verify that exactly one install target contains the locked common skills and that each installed skill matches `skills-lock.json`.
Project installs add local Git exclude entries for only the locked common-skill directories so unrelated project skills in `.agents/skills` remain visible to Git.
Global installs are shared across client repositories. A second repo pinned to the same lock verifies and succeeds without unnecessarily reinstalling; a repo pinned to a different lock fails with a version-mismatch error instead of overwriting the shared global install.
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
- `WARP_COMMON_SKILLS_INSTALL_TARGET=project|global`: explicit install or removal target.
- `WARP_COMMON_SKILLS_TARGET_REPO_ROOT=/path/to/repo`: repository containing `skills-lock.json` and project-local `.agents/skills`.
- `WARP_COMMON_SKILLS_REF=<git-ref>`: use a specific `warpdotdev/common-skills` branch, tag, or commit when creating a missing lock or checking interactively for lock updates.
## Lock hash stamps
After a successful install, `install_common_skills` writes a stamp with the current `skills-lock.json` hash.
- Project installs use git path `warp/common-skills-lock.hash`, or `.agents/skills/.common-skills-lock.hash` when git metadata is unavailable.
- Global installs use `~/.agents/warp/common-skills-lock.hash`.
The stamp lets `--if-needed` avoid reinstalling when the lock file and installed skills are already current.
