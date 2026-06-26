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

- `create-pr` — generic guidance for preparing and opening pull requests; specialize per repo with a `create-pr-local` companion.
- `diagnose-ci-failures` — generic workflow for inspecting GitHub CI failures and producing a fix plan; specialize per repo with a `diagnose-ci-failures-local` companion.
- `fix-errors` — generic guidance for fixing build, lint, formatting, and test failures; specialize per repo with a `fix-errors-local` companion.
- `resolve-merge-conflicts` — workflow and helper script for resolving git conflicts with compact context.
- `review-pr` — produces structured PR review feedback from local diff artifacts.
- `check-impl-against-spec` — compares PR implementation changes against provided spec context during review.

### Investigation and decision-making

- `research` — delegates low signal-to-noise-ratio research work to subagents and returns distilled, evidence-backed findings.
- `cross-critique` — sharpens contested decisions by having agents critique one another's independent proposals before synthesis.

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

## Conventions

### Local specialization companions (`*-local`)

A generic core skill can be specialized for a specific repository or product by adding a companion skill named `<core>-local` in the consuming repository (for example, `create-pr-local`, `fix-errors-local`, `diagnose-ci-failures-local`, `pr-walkthrough-local`). The companion declares its parent in frontmatter and layers only repo/brand-specific guidance on top of the generic core:

- `specializes: <core-name>` — the core skill this companion extends.
- `specializes_source: <org>/<repo>:.agents/skills/<core-name>` — where the parent core lives, so it can be installed if missing.

A companion should not redefine the core's methodology, schemas, or safety rules. It should only add the local conventions (toolchain commands, CI check names, brand tokens, etc.) that the core intentionally leaves open. Include a short "Prerequisite: install the parent skill" note so the relationship is explicit.

### Soft / optional references

A generic core may name an optional runtime tool or workflow, but only with a fallback so the skill still works when that tool is absent (for example, "if the `insert_code_review_comments` tool is available, use it; otherwise fall back to plain-text or `gh`").

A generic core must NOT name a private or brand-specific skill. Brand-specific or private behavior belongs in a local companion (for example, a `pr-walkthrough-local` that supplies brand styling), not in the shared core.

## Usage

Consumers can install the shared skills with the `skills` CLI.

List available skills:

```sh
npx skills@latest add warpdotdev/common-skills --list
```

Install all common skills for Warp globally:

```sh
npx skills@latest add warpdotdev/common-skills --skill '*' --agent warp --global
```

Install one skill:

```sh
npx skills@latest add warpdotdev/common-skills --skill write-tech-spec --agent warp --global
```

Update installed skills later:

```sh
npx skills@latest update --global --agent warp
```

You can also copy or sync selected directories from `.agents/skills/` into a repository's own `.agents/skills/` directory.

Prefer copying only the skills a repository actually needs. If a common skill needs repository-specific behavior, add a small local companion skill in that repository rather than forking the shared skill unless the change is useful everywhere.
