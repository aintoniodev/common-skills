---
name: fix-errors
description: Fix build, compilation, lint, formatting, and test errors in a repository. Use when the user hits build errors, lint or format failures, or test failures, or needs to run and interpret the repository's checks before a PR.
---

# fix-errors

Fix build, lint, formatting, and test errors in a repository.

## Overview

This skill helps resolve common issues encountered during development, including:
- Build and compilation errors (syntax errors, unresolved imports, type mismatches, etc.)
- Lint failures
- Formatting violations
- Test failures

Before opening or updating a pull request, the repository's checks must pass.

## Workflow

1. **Run the repository's own checks.** Use whatever the repo documents (a check script, a `Makefile` target, or the language toolchain's format/lint/build/test commands). If you are unsure which commands to run, look for an `AGENTS.md`, a contributing guide, a build config, or a CI workflow that lists them. A repo may also provide an optional `fix-errors-local` companion that names its exact toolchain commands.
2. **Read the full output and categorize the errors.** Group related errors by type (see categories below); fixing one often resolves others.
3. **Fix one class of error at a time.** Make the smallest change that addresses the root cause, not just the symptom.
4. **Re-run the narrow check** for the class you fixed to confirm it passes and did not introduce new errors.
5. **Run the repository's full check** once individual classes are resolved, and repeat until everything passes.

## Common Error Categories

These are language-agnostic categories; map them to your repository's toolchain.

### Build / compilation
- **Unresolved or unused imports** — add the correct import, or remove unused ones flagged by the compiler. Search the codebase to find the correct module path.
- **Type mismatches** — pass arguments of the expected type (convert, borrow, or reference as needed).
- **Signature changes** — when a function adds or changes a parameter, update all call sites.
- **Struct/record field changes** — when a type adds or removes fields, update every place it is constructed or destructured.
- **Enum/variant changes** — when adding a new variant, update exhaustive matches/switches with appropriate handling.

### Lint
- Resolve each warning at its root cause rather than blanket-suppressing it. Only suppress a lint when there is a clear, justified reason.

### Formatting
- Run the repository's formatter and commit the result.

### Test failures
- Read the assertion or error to understand expected vs. actual behavior.
- Fix the code when the test encodes correct behavior; update the test only when the behavior intentionally changed.
- Re-run the specific failing test before re-running the full suite.

## Best Practices

**Before fixing:**
- Read the full error message to understand the root cause.
- Check whether multiple errors are related (fixing one may resolve others).
- For type or signature errors, confirm you understand the expected vs. actual types.

**When fixing:**
- Fix one error type at a time when there are multiple issues.
- Re-run a fast build/check frequently to verify progress.
- Run relevant tests after non-trivial changes.

**After fixing:**
- Run the repository's full set of checks before opening or updating a PR. Use the `create-pr` skill for more detailed instructions.
- Verify tests pass in the areas you modified.

A repo may provide a `fix-errors-local` companion that documents its exact toolchain commands and repo-specific error patterns.
