# Common Skills

This repository is where common agent skills that should be shared across repositories should go.

A skill belongs here when it captures a reusable workflow, convention, or operating procedure that is useful in more than one repository. Repository-specific skills should stay with the repository they apply to unless they can be generalized without losing important context.

## Repository layout

```text
.agents/
  skills/
    <skill-name>/
      SKILL.md
      scripts/      # optional helper scripts
      references/   # optional supporting docs
      assets/       # optional bundled assets
```

Each skill lives in its own directory under `.agents/skills/`. The only required file for a skill is `SKILL.md` with YAML frontmatter containing at least:

- `name`: the kebab-case skill identifier
- `description`: what the skill does and when agents should use it

## Current skills

### Spec workflow

- `write-product-spec` — writes user-facing `PRODUCT.md` specs.
- `write-tech-spec` — writes implementation-oriented `TECH.md` specs.
- `spec-driven-implementation` — guides the full spec-first workflow for substantial features.
- `implement-specs` — implements approved `PRODUCT.md` and `TECH.md` files while keeping specs and code aligned.

### Development workflow

- `create-pr` — guidance for preparing and opening pull requests.
- `diagnose-ci-failures` — workflow for inspecting GitHub CI failures and producing a fix plan.
- `fix-errors` — guidance for fixing build, lint, formatting, and test failures.
- `resolve-merge-conflicts` — workflow and helper script for resolving git conflicts with compact context.
- `review-pr` — produces structured PR review feedback from local diff artifacts.

### Skill authoring

- `update-skill` — guidance for creating and maintaining skill directories and `SKILL.md` files.

## Adding a shared skill

When adding a skill to this repository:

1. Put it under `.agents/skills/<skill-name>/`.
2. Include a `SKILL.md` with clear frontmatter.
3. Keep the skill focused on a reusable workflow rather than one repository's private details.
4. Move large reference material into `references/` and helper automation into `scripts/`.
5. If copying from another repo, copy first, then generalize in a separate change so the provenance is easy to review.

## Generalizing repository-specific skills

Some skills copied here may still contain repository-specific examples, paths, commands, or assumptions. That is okay during initial migration, but shared skills should eventually be generalized by:

- replacing hard-coded repository names with placeholders or conditional guidance
- separating common workflow guidance from local repository conventions
- moving repo-specific overrides back into the repository that needs them
- keeping descriptions broad enough to trigger in multiple repositories, but specific enough to avoid unrelated tasks

## Usage

Consumers can install the shared skills into `~/.agents/skills`.

### macOS and Linux

Run the Bash installer:

```sh
curl -fsSL https://raw.githubusercontent.com/warpdotdev/common-skills/main/scripts/install.sh | bash
```

To clone into a specific temporary directory instead of using an automatically created one, run:

```sh
./scripts/install.sh --clone-dir /path/to/empty/clone-dir
```

To install into a repository-local skills directory instead of `~/.agents/skills`, run:

```sh
./scripts/install.sh --dest-dir /path/to/repo
```

When using the piped installer, pass installer arguments after `bash -s --`:

```sh
curl -fsSL https://raw.githubusercontent.com/warpdotdev/common-skills/main/scripts/install.sh | bash -s -- --dest-dir /path/to/repo
```

### Windows

Run the PowerShell installer:

```powershell
irm https://raw.githubusercontent.com/warpdotdev/common-skills/main/scripts/install.ps1 | iex
```

To clone into a specific temporary directory instead of using an automatically created one, run:

```powershell
.\scripts\install.ps1 -CloneDir C:\path\to\empty\clone-dir
```

To install into a repository-local skills directory instead of `~/.agents\skills`, run:

```powershell
.\scripts\install.ps1 -DestDir C:\path\to\repo
```

Both installers clone this repository, copy each skill directory from `.agents/skills/` into the destination skills directory, and prompt before overwriting an existing skill with the same name. If you decline the prompt, that skill is skipped and the installer continues.

You can also copy or sync selected directories from `.agents/skills/` into a repository's own `.agents/skills/` directory.

Prefer copying only the skills a repository actually needs. If a common skill needs repository-specific behavior, add a small local companion skill in that repository rather than forking the shared skill unless the change is useful everywhere.
