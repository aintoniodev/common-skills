---
name: scan-new-specs
description: Scan warpdotdev/warp and warp-server for recently merged PRODUCT.md specs that don't yet have a corresponding docs PR in warpdotdev/docs. When a complete spec is found, auto-generates a full docs draft PR and tags the engineer. When a spec is too thin to draft from, pings the engineer directly. Designed to run as a scheduled Oz ambient agent (e.g., every 2-3 days). Use when setting up the automated docs trigger or running a manual docs coverage sweep.
---

# scan-new-specs

Scan `warpdotdev/warp` and `warp-server` for recently merged product or tech specs that lack a corresponding docs draft. For each gap:

- **If the spec is complete** — automatically run `write-feature-docs` in ambient mode to generate a full draft PR in `warpdotdev/docs`, then ping the engineer to review it
- **If the spec is thin** — ping the engineer directly to either flesh out the spec or kick off the docs workflow manually

In both cases, post a summary to `#growth-docs`.

> **TODO for reviewers:** `#growth-docs` is a temporary channel for engineer pings. Identify a more appropriate eng-facing channel (e.g. a shared eng/docs channel, `#dev`, or a dedicated `#docs-requests` channel) once this workflow is established.

## Configuration

Before running, confirm these values (or accept the defaults):

| Setting | Default | Description |
|---|---|---|
| `LOOKBACK_DAYS` | `3` | How many days back to scan for merged spec PRs |
| `SLACK_CHANNEL` | `#growth-docs` | Slack channel for engineer pings and summaries (temporary — see TODO above) |
| `SLACK_WEBHOOK_URL` | Required | Slack incoming webhook URL (store as a secret) |

If `SLACK_WEBHOOK_URL` is not set, print all messages to stdout instead.

## Step 1: Find recently merged specs

Use the GitHub CLI to search both repos for PRs merged in the last `LOOKBACK_DAYS` days that added a new `PRODUCT.md` file under `specs/`:

```bash
# Find merged PRs in warpdotdev/warp (OSS repo) that added a PRODUCT.md
gh pr list \
  --repo warpdotdev/warp \
  --state merged \
  --search "merged:>$(date -v-${LOOKBACK_DAYS}d +%Y-%m-%d) specs PRODUCT.md in:files" \
  --json number,title,author,mergedAt,url \
  --limit 50

# Repeat for warp-server
gh pr list \
  --repo warpdotdev/warp-server \
  --state merged \
  --search "merged:>$(date -v-${LOOKBACK_DAYS}d +%Y-%m-%d) specs PRODUCT.md in:files" \
  --json number,title,author,mergedAt,url \
  --limit 50
```

For each PR returned, verify it actually contains a new `specs/*/PRODUCT.md` by inspecting the files changed:

```bash
gh pr view <number> --repo warpdotdev/<repo> --json files -q '.files[].path' \
  | grep -E '^specs/.+/PRODUCT\.md$'
```

Collect the list of: spec ID (the directory name under `specs/`), spec PR number and URL, PR author GitHub username, repo (`warp` or `warp-server`), and merge date.

For each PR author's GitHub username, also resolve their likely Slack handle:

```bash
# Get the engineer's display name from GitHub
ENG_NAME=$(gh api users/<github-username> -q '.name // .login')
# Use the full name for the Slack @mention (e.g. "Harry Albert" → @Harry Albert)
# Most Warp engineers use first+last name as their Slack handle
# Flag the mention as unverified in the message so readers can correct it if wrong
```

Store `ENG_NAME` and `ENG_GITHUB` (the GitHub username) for use in Slack messages.

## Step 2: Check for existing docs coverage

For each spec found, search `warpdotdev/docs` for an open or recently merged PR that mentions the spec ID or feature name:

```bash
gh pr list \
  --repo warpdotdev/docs \
  --state all \
  --search "<spec-id>" \
  --json number,title,state,url \
  --limit 10
```

A spec is considered **covered** if any matching PR exists (open, merged, or draft). Skip covered specs.

A spec is **uncovered** if no matching PR is found in `warpdotdev/docs`.

## Step 3: Assess spec completeness

For each uncovered spec, read `specs/<id>/PRODUCT.md` and assess whether it has enough content to auto-draft from:

**Complete** (proceed to auto-draft) if ALL of the following are true:
- File is at least 40 lines long
- Contains a `## Behavior` section (or equivalent) with numbered invariants or user-facing steps
- Describes at least one concrete user action (not just a summary paragraph)

**Thin** (ping engineer instead) if the spec is a stub — only a Summary section, fewer than 40 lines, or no behavior detail.

## Step 4: Act based on spec completeness

### Path A: Complete spec → auto-draft

1. Run `write-feature-docs` in **ambient mode** (see `write-feature-docs` skill for details) — this skips the interactive outline confirmation and instead embeds the outline as a checklist in the PR description
2. The PR is opened in `warpdotdev/docs` with the draft and a checklist of items needing engineer verification
3. Request review from the engineer (`@<github-username>`) and from `@rachaelrenk`, `@petradonka`, and `@hongyi-chen`
4. Post this Slack message to `SLACK_CHANNEL`:

```
📄 *Docs draft auto-generated*

Feature: *<spec-id>* (from `<repo>`)
Spec PR: <spec-pr-url>
@<ENG_NAME> _(GitHub: <github-username> — verify this Slack handle is correct)_

I've opened a draft docs PR for review: <docs-pr-url>
Please check the items marked *[UNVERIFIED]* and *[TODO]* in the PR — those are the only things that need your input.
```

### Path B: Thin spec → ping engineer

Post this Slack message to `SLACK_CHANNEL`:

```
📋 *New spec needs docs — not enough detail to auto-draft*

Feature: *<spec-id>* (from `<repo>`)
Spec PR: <spec-pr-url>
@<ENG_NAME> _(GitHub: <github-username> — verify this Slack handle is correct)_

The spec doesn't have enough behavior detail for me to auto-generate docs yet. Please either:
• Add more detail to `specs/<spec-id>/PRODUCT.md` (a Behavior section with user-facing steps), OR
• Ping the docs team in this channel and we'll draft it manually
```

If there are no uncovered specs, post:

```
✅ *Docs coverage scan complete* — all recently merged specs have docs coverage.
```

## Step 5: Post to Slack

Send each message to `SLACK_CHANNEL` via the incoming webhook:

```bash
curl -s -X POST "$SLACK_WEBHOOK_URL" \
  -H 'Content-type: application/json' \
  --data "{\"text\": \"$MESSAGE\"}"
```

If `SLACK_WEBHOOK_URL` is not set, print the message to stdout instead.

## Step 6: Print a summary

Always print a run summary to stdout:

```
scan-new-specs run summary
  Repos scanned:         warpdotdev/warp, warp-server
  Lookback window:       <N> days (since <date>)
  Specs found:           <N>
  Already covered:       <N>
  Auto-drafted:          <N>   (complete spec → draft PR opened)
  Pinged (thin spec):    <N>   (incomplete spec → engineer notified)
  Slack channel:         <channel>
```

## Scheduling

This skill is designed to run as a **scheduled Oz ambient agent** every 2–3 days. A suggested prompt for the Oz agent configuration:

> "Run scan-new-specs to check warpdotdev/warp and warp-server for newly merged PRODUCT.md specs that don't have a corresponding docs PR in warpdotdev/docs. For complete specs, auto-generate a draft docs PR and tag the engineer. For thin specs, ping the engineer in Slack. Post a summary to #growth-docs. Use the last 3 days as the lookback window."

Suggested schedule: every Monday, Wednesday, and Friday at 9am PT — frequent enough to catch specs quickly, but not noisy.

## Deduplication note

This skill does not maintain persistent state between runs. Deduplication relies entirely on whether a docs PR exists in `warpdotdev/docs` — if a PR is open or merged for a spec, it won't be flagged again. This means a spec will continue to generate nudges until someone opens a docs PR for it (even a draft).

## Related skills

- `write-feature-docs` — the skill engineers run to generate the docs draft after being nudged
