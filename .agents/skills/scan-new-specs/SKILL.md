---
name: scan-new-specs
description: Scan warp-internal and warp-server for recently merged PRODUCT.md specs that don't yet have a corresponding docs PR in warpdotdev/docs, then post Slack nudges to a configured channel. Designed to run as a scheduled Oz ambient agent (e.g., every 2-3 days). Use when setting up the automated docs trigger, running a manual docs coverage sweep, or checking whether any new specs are missing documentation.
---

# scan-new-specs

Scan `warp-internal` and `warp-server` for recently merged product or tech specs that lack a corresponding docs draft, and post a Slack nudge to `#growth-docs` for each gap. This is the automated companion to the `write-feature-docs` skill — it surfaces docs gaps so the docs team can follow up with the engineer, without requiring engineers to remember to kick off the docs-drafting workflow themselves.

## Configuration

Before running, confirm these values (or accept the defaults):

| Setting | Default | Description |
|---|---|---|
| `LOOKBACK_DAYS` | `3` | How many days back to scan for merged spec PRs |
| `SLACK_CHANNEL` | `#growth-docs` | Slack channel to post nudges to |
| `SLACK_WEBHOOK_URL` | Required | Slack incoming webhook URL (should be stored as a secret) |

If `SLACK_WEBHOOK_URL` is not set in the environment, print the nudge messages to stdout instead so the output can be reviewed manually.

## Step 1: Find recently merged specs

Use the GitHub CLI to search both repos for PRs merged in the last `LOOKBACK_DAYS` days that added a new `PRODUCT.md` file under `specs/`:

```bash
# Find merged PRs in warp-internal that added a PRODUCT.md
gh pr list \
  --repo warpdotdev/warp-internal \
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

Collect the list of: spec ID (the directory name under `specs/`), spec PR number and URL, PR author GitHub username, repo (`warp-internal` or `warp-server`), and merge date.

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

A spec is considered **covered** if any matching PR exists (open, merged, or draft). Skip covered specs — do not send a nudge.

A spec is **uncovered** if no matching PR is found in `warpdotdev/docs`.

## Step 3: Build the nudge messages

For each uncovered spec, compose a Slack message. Keep it brief and actionable:

```
📄 *New spec merged, no docs yet*

Feature: *<spec-id>* (from `<repo>`)
Spec PR: <spec-pr-url>
Merged by: @<github-username> on <merge-date>

To create the docs draft, run `write-feature-docs` from `<repo>` with spec ID `<spec-id>`.
```

Group multiple nudges into a single Slack message when possible to avoid spamming the channel. Use a summary header if there are 3+ uncovered specs:

```
📄 *Docs coverage scan — <N> specs need docs*

<list of nudge items>
```

If there are no uncovered specs, post a single brief message:

```
✅ *Docs coverage scan complete* — all recently merged specs have docs coverage.
```

## Step 4: Post to Slack

Send the composed message to `SLACK_CHANNEL` via the incoming webhook:

```bash
curl -s -X POST "$SLACK_WEBHOOK_URL" \
  -H 'Content-type: application/json' \
  --data "{\"text\": \"$MESSAGE\"}"
```

If `SLACK_WEBHOOK_URL` is not set, print the message to stdout instead and note that no Slack notification was sent.

## Step 5: Print a summary

Always print a run summary to stdout:

```
scan-new-specs run summary
  Repos scanned:        warp-internal, warp-server
  Lookback window:      <N> days (since <date>)
  Specs found:          <N>
  Already covered:      <N>
  Nudges sent:          <N>
  Slack channel:        <channel>
```

## Scheduling

This skill is designed to run as a **scheduled Oz ambient agent** every 2–3 days. A suggested prompt for the Oz agent configuration:

> "Run scan-new-specs to check warp-internal and warp-server for newly merged PRODUCT.md specs that don't have a corresponding docs PR in warpdotdev/docs. Post nudges to #growth-docs for any gaps. Use the last 3 days as the lookback window."

Suggested schedule: every Monday, Wednesday, and Friday at 9am PT — frequent enough to catch specs quickly, but not noisy.

## Deduplication note

This skill does not maintain persistent state between runs. Deduplication relies entirely on whether a docs PR exists in `warpdotdev/docs` — if a PR is open or merged for a spec, it won't be flagged again. This means a spec will continue to generate nudges until someone opens a docs PR for it (even a draft).

## Related skills

- `write-feature-docs` — the skill engineers run to generate the docs draft after being nudged
