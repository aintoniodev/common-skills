---
name: implement-specs
description: Implements approved work from whichever valuable specs exist, including PRODUCT.md, TECH.md, or both. Keeps applicable specs and code aligned as implementation evolves without creating or preserving redundant documents.
---

# implement-specs

Implement approved work from `PRODUCT.md`, `TECH.md`, or both.

## Overview

Use this skill after the warranted specs are approved. The goal is to build the change described by the available specs while keeping those checked-in specs and the implementation aligned as the work evolves.

Approved specs should live directly under a ticket-named directory in `specs/`, for example `specs/APP-1234/PRODUCT.md`, `specs/APP-1234/TECH.md`, or both.

In many cases, the implementation should be pushed in the same PR as the applicable specs. As the engineer iterates, changes to those specs and the code should all be pushed in that same PR so review stays anchored to the change that will actually ship.

## Prerequisites

Before using this skill:

- confirm which of `PRODUCT.md` and `TECH.md` exist and that each still adds independent value
- confirm that at least one approved spec exists
- confirm that the relevant specs have been reviewed and approved enough to start implementation

## Workflow

### 1. Read the approved specs first

Treat whichever sources exist as authoritative for their scope:

- `PRODUCT.md` as the source of truth for meaningful user-facing or public-contract behavior
- `TECH.md` as the source of truth for architecture, sequencing, implementation shape, validation, and standalone behavioral guarantees when there is no product spec

Make sure you understand the expected behavior, constraints, risks, and validation plan before writing code.

### 2. Offer optional implementation aids for large features

For large or long-running features, optionally offer one of these aids to the user before implementation begins:

- `PROJECT_LOG.md` to track checkpoints, explored paths, partial findings, and current implementation state
- `DECISIONS.md` to capture concrete product and technical decisions made during the PRD and tech design process

These are optional aids, not required deliverables. Offer them when they would reduce confusion or help future agents avoid re-exploring the same paths.

### 3. Plan and implement against the specs

Break the work into concrete implementation steps, then implement the change against the approved specs.

During implementation:

- keep behavior aligned with `PRODUCT.md` when it exists, otherwise with the behavioral guarantees in `TECH.md`
- keep architecture and sequencing aligned with `TECH.md` when it exists
- add or update tests and verification artifacts as the work lands

Use the same PR for the specs and implementation when practical so the full evolution of the change is reviewable in one place.

### 4. Update specs as the implementation evolves

If implementation reveals that the intended behavior or design should change, update the checked-in specs rather than letting them go stale.

In particular:

- update `PRODUCT.md`, when it exists, when meaningful user-facing behavior, UX, or public-contract decisions change
- update `TECH.md`, when it exists, when architecture, sequencing, module boundaries, behavioral guarantees, or validation strategy change
- keep those updates in the same PR as the corresponding code changes

If a spec stops adding independent value as the design evolves, consolidate any durable guarantees into the remaining source of truth and remove the redundant document rather than maintaining synchronized copies.

The PR should describe the change that actually ships, not just the initial draft of the specs.

### 5. Verify against the specs

Before considering the work complete, verify that the code matches the current specs.

Prefer:

- unit tests and regression coverage that follow the repository's local testing conventions
- integration or end-to-end tests for important user flows

## Best Practices

- Keep specs and code synchronized throughout implementation.
- Prefer updating the spec immediately when decisions change rather than batching spec cleanup until the end.
- Use optional tracking documents only when they add real value for a complex feature.
- Keep the same PR coherent: spec updates, code changes, tests, and optional tracking docs should all support the same change narrative.

## Related Skills

- `spec-driven-implementation`
- `write-product-spec`
- `write-tech-spec`
