---
name: sweep-low-value-tests
description: Sweep an existing test suite for low-value tests - tests that re-assert the source, assert implementation instead of behavior, duplicate coverage, or exist only to justify a production seam - then delete them in reviewable batches and remove the seams they leave behind. Use when asked to sweep for low-value tests, prune or clean up a test suite, do a test cleanup pass, remove tests that re-assert the source, or find tests that should not be in the codebase.
---

# Sweep Low-Value Tests

## Overview

A sweep is not a code review. A review reads a diff and reacts to what an author just added. A sweep reads a suite that was merged months ago, with no diff to anchor on: it has to find candidates at scale, rank them, prove each deletion did not drop real coverage, and remove the production indirection the deletions leave dead.

Deleting a test is not the goal. A suite you trust is the goal. A sweep that drops real coverage is worse than no sweep, and "found nothing worth deleting here" is a valid result.

Counterpart: the factory `code-review` skill (`v1/skills/code-review/SKILL.md` in `warpdotdev/factory-dev`) applies the same criteria to a single diff at review time. When the criteria change in one, update the other.

## Workflow

1. Pick a bounded target.
2. Surface candidates mechanically.
3. Judge each candidate.
4. Rank into delete, rewrite, ask, keep.
5. Prove each deletion is safe.
6. Delete in reviewable batches.
7. Remove the dead seams.

## The decision question

Apply one question to every candidate: what behavior change would make this test fail, and would that failure be a real defect? When the honest answer is "a behavior-preserving refactor" or "nothing", the test is a candidate for deletion.

## 1. Pick a bounded target

Sweep one package, crate, or directory at a time. A whole-repository sweep is not one task, and the deletions have to land in batches a human will actually read. Note the test command for that target before starting - step 5 needs it.

## 2. Surface candidates mechanically

### Git history: tests that change whenever their source changes

The sharpest signal available in a sweep. A test that is edited in the same commit as its production file is tracking the implementation, not the behavior. History measures this directly.

```bash
git ls-files '*_tests.rs' '*_test.go' '*.test.ts' '*.test.tsx' '*_test.py' | while read -r t; do
  p=$(printf '%s' "$t" | sed -E 's/(_tests?|\.test|\.spec|_spec)\.([A-Za-z]+)$/.\2/')
  [ "$p" != "$t" ] && [ -f "$p" ] || continue
  tc=$(git log --oneline -- "$t" | wc -l)
  pc=$(git log --oneline -- "$p" | wc -l)
  uc=$(git log --oneline -- "$t" "$p" | wc -l)
  [ "$tc" -ge 5 ] || continue
  awk -v t="$t" -v a=$((tc+pc-uc)) -v b="$tc" 'BEGIN{printf "%.2f %3d %s\n", a/b, b, t}'
done | sort -rn | head -40
```

The columns are co-change ratio, commit count, path. `tc + pc - uc` is the number of commits that touched both files, by inclusion-exclusion. A ratio above roughly 0.8 over a meaningful number of commits means the test has almost never changed for its own reasons. Adjust the globs and the `sed` pairing rule to the repository's naming convention, and verify the pairing prints real source paths before trusting the ranking.

The ratio nominates a file; it never convicts one. A file that legitimately grew alongside a young feature scores high too. Read the test before judging it.

### Shape heuristics

Cheap greps that correlate with low value. Use them to build a candidate list, not a verdict.

```bash
# Assertions on interactions rather than state.
grep -rnE 'toHaveBeenCalled|call_count|assert_called|\.mock\.calls|verify\(|\.times\(' <target>

# Mock density: which test files stub out every collaborator.
grep -rciE 'mock|stub|fake|spy' <target> | grep -v ':0$' | sort -t: -k2 -rn | head -20

# Test names that betray a trivial subject.
grep -rnE '(fn test_|func Test|[ (]it\(|[ (]test\()' <target> --include='*test*' \
  | grep -iE 'default|getter|setter|construct|to_string|new_|clone|display|debug'
```

Also compare sizes: a test file several times longer than the source it covers is usually enumerating the implementation rather than the behavior.

The name heuristic is the weakest of these and produces the most false positives - a test named for a trivial-sounding method often pins something real, such as a `Debug` implementation that must not leak a secret. Every heuristic here nominates a file to read; none of them convicts one.

## 3. Judge each candidate

Flag these, each with its correction:

- **Change-detector test**: asserts a call sequence, that a mock was configured, or private state, and needs editing on a refactor that no caller could observe. Rewrite as a state or behavior assertion, or delete.
- **Tautological test**: re-asserts a literal or a constant from the source, or verifies the stub instead of the unit under test. Delete.
- **Test of trivial code**: a getter, a pass-through conversion, a default, plain construction, or reading back a config or flag default. Delete.
- **Duplicative test**: a near-identical case another test already covers. Delete, or narrow it to the distinct path it adds.
- **Orphaned test**: the sweep-time form of an out-of-scope test. Its subject no longer exists in the form it tests, or the production code it exercises has no caller other than the test. Delete the test, and delete the dead production code with it - unless that code is public API for consumers outside the repository.
- **Never-load-bearing test**: the sweep-time form of scaffolding. The author is gone, so decide it on evidence instead of intent - `git log --follow` on the test shows only mechanical edits (renames, signature churn, compile fixes) and no commit where it changed as part of a bug fix, and step 5 shows another test already fails when the behavior breaks. Delete.
- **Wrong-level test**: a unit test that does real IO, spawns a process, or otherwise reaches for what a higher-level test covers. Move it to that level, or delete it when that level already covers the case.

## 4. Rank

Order by confidence, and act by tier:

- **Delete**: tautological, trivial-code, duplicative, and orphaned tests. Every deletion still goes through step 5 first.
- **Rewrite**: a change-detector test whose underlying behavior is real and uncovered. Replace the interaction assertion with a state assertion. Never delete it and leave the behavior unguarded.
- **Ask a human**: anything where the behavior the test guards is unclear, anything step 5 cannot settle, and anything in an authentication, authorization, billing, or data-integrity path. Hand these over with the reasoning; do not decide them on the sweep's own judgment.
- **Keep**: everything else. Default here.

## 5. Prove each deletion is safe

Deleting a test always makes the suite pass, so a green run proves nothing. Prove instead that something else still guards the behavior:

1. Name the behavior the candidate claims to cover.
2. Break that behavior in the production code: invert a condition, return a wrong constant, drop a branch.
3. Run the target's tests with the candidate still present. It must fail. If it does not, the test does not cover what it claims: re-read it to find what it does cover, and delete it when the answer is nothing.
4. Remove the candidate and run again. If something else fails, the coverage is duplicated and the deletion is safe. If nothing fails, the candidate was the only guard: do not delete it, rewrite it as a behavior assertion instead.
5. Revert the production break. Confirm the tree is clean before moving on.

One break can clear several candidates that claim the same behavior. Record, per deletion, the behavior and the test that still covers it - that record is the PR description in step 6.

## 6. Delete in reviewable batches

- One batch per package or area, small enough for a human to read in one sitting. Never one repository-wide deletion PR.
- Delete whole tests, not assertions inside a test you are keeping.
- List every deleted test in the PR description with one line each: the behavior it claimed to cover, and what still covers it.
- Keep rewrites in separate PRs from deletions. They need different review attention.

## 7. Remove the dead seams

The payoff. Production indirection that existed only to serve a deleted test is now dead, and this is the pass that usually gets skipped.

After a deletion batch, look for an injected collaborator, a wrapper, a trait or interface with one implementation, widened visibility, or a one-line function with a single call site that was extracted purely to be testable:

```bash
# The repository's own dead-code check first - it finds most of it.
# Rust: cargo clippy --workspace --all-targets. TypeScript: tsc --noUnusedLocals.
# Go: staticcheck ./... . Python: ruff check.
cargo clippy --workspace --all-targets 2>&1 | grep -E 'never used|never read'

# Then, per symbol the deleted tests referenced, count remaining non-test callers.
grep -rnE '\b<Symbol>\b' <target> --exclude='*test*' --exclude='*spec*' | wc -l
```

Narrow `pub(crate)` and `pub` back down, collapse a trait with one implementation into that implementation, and inline a wrapper whose only justification was the test. Land the seam removal in its own PR referencing the deletion batch, so a reviewer can judge the production change on its own merits.

If a seam turns out to make the code clearer regardless of testing, keep it. The test was not its only justification.

## What to leave alone

- **Small is not low value.** A one-line assertion that pins a real boundary, an edge case, or a fixed regression is valuable. The burden is "what defect does this catch", never "is this test big enough".
- **A test that references a bug or issue ID stays.** It exists because something actually broke.
- **A failing or flaky test is a different job.** Fix or quarantine it; do not sweep it away.
- **A coverage drop is not proof of harm, and a coverage target is not the goal.** Step 5 is the proof.
- **Never chase a deletion count.** The pressure to hit a number is much stronger in a sweep than at review time, and it is exactly how a sweep starts deleting real coverage.
- **Defer to the repository's own testing skills** when they exist. They state the local rules; this skill states the judgment.
