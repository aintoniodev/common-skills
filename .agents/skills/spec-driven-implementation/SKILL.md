---
name: spec-driven-implementation
description: Drives a pragmatic spec-first workflow by choosing among no spec, PRODUCT.md only, standalone TECH.md with behavioral guarantees, or both. Use when starting significant feature or hardening work, planning agent-driven implementation, or deciding which specs should be checked into source control.
---

# spec-driven-implementation

Drive a spec-first workflow for substantial work in Warp.

## Overview

Use this skill for significant work where a written spec will improve implementation quality, reduce ambiguity, or make review easier. Be pragmatic: not every change needs specs, and not every technically complex change needs a product spec.

Specs may live in:

- `specs/<linear-ticket-number>/PRODUCT.md`
- `specs/<linear-ticket-number>/TECH.md`

For example:

- `specs/APP-1234/PRODUCT.md`
- `specs/APP-1234/TECH.md`

`specs/` should contain only ticket-named directories as direct children. Do not create engineer-named subdirectories or feature-slug directories there.

Use a relevant Linear issue when one already exists. Only create one when the user explicitly asks; in that case use the Linear MCP tools directly:

- `list_teams` to find the appropriate team
- `list_issue_labels` to inspect the expected labels/tags
- `save_issue` to create the issue with the appropriate team and labels

If the correct team or labels are not obvious from the request and surrounding context, use `ask_user_question` to clarify rather than guessing.

Specs should largely be written by agents, not by hand, and should be checked into source control when their ongoing review value exceeds the cost of keeping them current with the code.

## When specs are required

Strongly prefer specs when the change is substantial, such as:

- product or architectural ambiguity
- expected implementation size around 1k+ LOC
- deep or cross-cutting stack changes
- risky behavior changes where regressions would be expensive
- work where agent quality will improve materially from clearer inputs

Specs are often unnecessary for:

- small, local bug fixes
- straightforward refactors
- narrow UI tweaks with little ambiguity

For pure UI changes, the product spec is often useful while the tech spec may be unnecessary.

Choose the smallest document set that adds independent value:

- **No spec** — Small, clear work that is better captured by the issue, code, and tests.
- **`PRODUCT.md` only** — Meaningful user-facing or public-contract behavior is ambiguous, but implementation is straightforward.
- **`TECH.md` only** — Internal hardening, a bug fix, refactor, migration, lifecycle/concurrency work, or other technically complex change that preserves existing product semantics. Include a concise `Behavioral guarantees` section.
- **Both** — Product behavior and technical design each contain meaningful, independently reviewable decisions.

Technical size or cross-cutting scope alone is not a reason to create `PRODUCT.md`.

## Workflow

### 1. Decide whether the work needs specs

Evaluate the size, ambiguity, and risk of the work. If specs will not meaningfully improve execution or review, skip them and focus on verification instead.

### 2. Choose and write only the warranted specs

Do not assume `PRODUCT.md` comes first or that both documents are required.

Use the `write-product-spec` skill only when the product behavior has independent review value. The product spec should define:

- what problem is being solved
- the desired user experience
- meaningful product invariants and user-visible edge cases

If the work has UI or interaction design, ask for a Figma mock if one exists. If there is no mock, continue but call that out explicitly in the product spec.

Reference the Linear issue in the spec when one exists. Because specs live under `specs/<linear-ticket-number>/...`, this should usually be straightforward.

For technically complex work that preserves existing product semantics, skip `PRODUCT.md` and use a standalone `TECH.md` with concise behavioral guarantees.

### 3. Write the tech spec when warranted

Use the `write-tech-spec` skill for substantial or ambiguous implementation work.

Prefer a tech spec when:

- the implementation spans multiple subsystems
- architecture or extensibility matters
- there are meaningful tradeoffs to document
- reviewers will benefit more from reviewing the plan than the raw code

It is acceptable to write the tech spec after an e2e prototype if that leads to a more accurate implementation plan. Do not force a premature tech spec when the implementation details are still too uncertain.

### 4. Implement approved specs

After the warranted specs are approved, use the `implement-specs` skill to build from whichever approved documents exist.

The implementation can often be pushed in the same PR as the specs. As the engineer iterates, keep the applicable specs, code changes, and tests in that same PR so the review reflects the change that will actually ship.

For large features, the implementer may optionally offer:

- `PROJECT_LOG.md` to track explored paths, checkpoints, and current implementation state
- `DECISIONS.md` to capture concrete product and technical decisions made during design and implementation

These are optional aids, not required outputs.

### 5. Keep specs current during implementation

If implementation changes from the spec, update the spec rather than leaving it stale.

Update `PRODUCT.md`, when it exists, when:

- user-facing behavior changes
- meaningful product guarantees change
- UX details or edge cases change

Update `TECH.md`, when it exists, when:

- the implementation approach changes
- architectural boundaries move
- risks, dependencies, or rollout details change
- the testing or validation plan changes

The checked-in specs should describe the change that actually ships, not just the initial intent. Keep those spec updates in the same PR as the related code changes whenever practical.

If a spec stops adding independent value as the design evolves, consolidate any durable guarantees into the remaining source of truth and remove the redundant document rather than maintaining two synchronized copies.

### 6. Verify behavior against the spec

Before considering the work complete, make sure verification maps back to the applicable specs. Prefer tests and artifacts that validate the product behavior or standalone behavioral guarantees directly:

- unit tests and regression coverage that follow the repository's local testing conventions
- integration tests for critical user flows
- loom walkthroughs or equivalent feature demonstrations when appropriate
- screenshots or videos when useful for UI-heavy work

## Best Practices

- Be pragmatic above all else.
- Write specs to improve input quality for agents, not as ceremony.
- Choose document types based on independent review value, not implementation size alone.
- Keep product specs behavior-oriented and implementation-light.
- Keep tech specs implementation-oriented and grounded in current codebase patterns; use concise behavioral guarantees when no product spec is warranted.
- When a spec references relevant code chunks, include the inspected commit SHA in the file reference when possible and link the reference to the exact GitHub `blob/<sha>/...#Lx-Ly` lines.
- Use review time to validate specs and behavior, not to over-index on code style nits.

## Related Skills

- `implement-specs`
- `write-product-spec`
- `write-tech-spec`
