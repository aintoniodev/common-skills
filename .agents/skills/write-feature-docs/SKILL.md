---
name: write-feature-docs
description: Draft a complete documentation page for a new Warp feature from its PRODUCT.md and/or TECH.md spec. Use when an engineer has written a spec and needs to produce a first-pass MDX draft for the warpdotdev/docs repo. Also handles features without specs by researching the codebase first. Invoke this skill whenever an engineer mentions writing docs for a feature, drafting a docs page, creating feature documentation, starting the eng-docs workflow, or converting a spec into documentation. Works from warp-internal or warp-server.
---

# write-feature-docs

Draft a complete documentation page for a new Warp feature. You read the feature's spec, verify technical claims by researching the codebase yourself, present a concise outline for the engineer to confirm, then produce a complete MDX draft and open a draft PR in `warpdotdev/docs` — tagging the docs team for review.

The engineer's job is to confirm what you couldn't verify from the spec and code — not to do a full accuracy review, not to polish prose, not to know docs conventions.

## The workflow

1. Find and read the spec files
2. Research the codebase to verify technical claims — minimize what the engineer needs to check
3. Generate a concise outline, distinguishing verified facts from open questions
4. Engineer confirms or corrects
5. Generate the complete MDX draft
6. Open a draft PR in `warpdotdev/docs` and tag the docs team

---

## Step 1: Find and read the spec

Ask the engineer for the spec ID if they haven't provided it. The spec ID is one of:
- A Linear ticket number: `APP-1234`
- A GitHub issue (prefixed with `gh-`): `gh-4567`
- A short kebab-case feature name: `vertical-tabs-hover-sidecar`

Look for the spec files at:
- `specs/<id>/PRODUCT.md` — primary source: user-facing behavior, what and why
- `specs/<id>/TECH.md` — secondary source: implementation, data model

Read both files if both exist. `PRODUCT.md` is the primary driver for the docs content.

**When reading `TECH.md`:** Before incorporating anything from it, identify content that looks like internal implementation detail — database schema, internal service names, private API endpoints, confidential server architecture. Present these flagged items to the engineer and ask them to confirm what's safe to include in public docs and what should stay internal. Do not include anything marked confidential in the draft.

If neither file exists, skip to [No-spec fallback](#no-spec-fallback).

---

## Step 2: Research the codebase

Before presenting the outline, use the GitHub CLI to verify as much technical content as possible yourself — reducing what the engineer needs to confirm to only what you genuinely cannot determine from the code.

Things to verify from code:
- **Feature flag name**: `gh search code "<feature-name>" --repo warpdotdev/warp-internal`
- **UI strings**: search for user-visible button labels, menu item names, or setting names referenced in the spec
- **Settings paths**: confirm exact Settings menu paths (e.g., `**Settings** > **AI** > **Knowledge**`)
- **CLI commands or keyboard shortcuts** mentioned in the spec
- **Related features**: identify other features that cross-reference this one for "Related pages"

For each claim you verify from code, mark it confirmed. For claims you can't verify (UI behavior not in code, product intent, behavior of unreleased features), flag them as `[UNVERIFIED]` in the outline — those are the only things the engineer needs to focus on.

---

## Step 3: Generate and present the outline

Generate a concise outline — no prose. The outline shows what you've confirmed from research and exactly what still needs engineer input.

Print the outline to the terminal in this format:

```
📄 Docs outline for [Feature name]

PROPOSED PLACEMENT
  Section:  src/content/docs/<section>/   (e.g., agent-platform/cloud-agents/)
  File:     <feature-name>.mdx
  URL:      docs.warp.dev/<path>/<feature-name>

CONTENT SECTIONS
  H1:  <Feature name>
  Opening paragraph: [1-sentence description of what you'll write]
  ## Key features — [which 2-4 capabilities to highlight as bullets]
  ## How it works — [the conceptual model: what and why, no steps]
  ## <Usage section title> — [e.g., "Creating environments", "Configuring X"]
      Prerequisites: [any prerequisites to list]
      Steps:
        1. [Step description]
        2. [Step description]
        3. [Step description]
        ...
  ## Related pages — [cross-links to suggest]

VERIFIED FROM CODEBASE ✅
  - [e.g., "Feature flag: `my_feature_flag` confirmed in warp-internal"]
  - [e.g., "Settings path: confirmed as Settings > AI > Agents > Permissions"]

NEEDS YOUR CONFIRMATION ⚠️
  - [e.g., "Step 3 — does the sync trigger automatically or require a manual action?"]
  - [e.g., "Is the 'Export' button visible before the feature flag is enabled?"]
```

After printing the outline, say:

> "I've verified what I could from the codebase. Please check the items marked ⚠️ above and reply with any corrections, or say 'looks good' to proceed."

Wait for the engineer's reply before continuing. Incorporate their feedback, then draft.

---

## Step 4: Generate the MDX draft

Generate a complete `.mdx` file based on the confirmed outline. The output is ready to drop directly into `warpdotdev/docs`.

### Template structure

```mdx
---
description: >-
  [1-2 sentence standalone summary. Lead with the user benefit. Include the
  feature name and a key term or two so it works as a search result snippet.]
---

# [Feature name]

[Opening paragraph: what the feature does and its primary benefit.
1-3 sentences. Lead with what the user can accomplish, not the implementation.]

:::note
[Optional: key context the reader needs upfront — a prerequisite, a limitation,
or when NOT to use this feature. Delete this callout if nothing applies.]
:::

## Key features

* **Feature A** - What it does and why it matters to the user.
* **Feature B** - What it does and why it matters to the user.

## How it works

[CONCEPTUAL section: explain system behavior, data flow, or architecture.
Answer "what" and "why" before "how." Define any new terms when they
first appear. Do NOT include step-by-step procedures in this section —
keep conceptual and procedural content clearly separated.]

## [Usage section title]

[PROCEDURAL section: motivate the task first, then give numbered steps.
Briefly explain why the user is doing this before telling them how.]

### Prerequisites

* **[Prerequisite]** - What it is and where to get it. See [full reference](link-here).

### [Task name — sentence case, e.g., "Create an environment with the CLI"]

1. First step. Expected outcome if not obvious.
2. Second step.
3. Third step.

## Related pages

* [Related feature](../path/to/page.md)
* [Deeper guide](../path/to/guide.md)
```

### Style rules — apply exactly

These conventions come from the Warp docs style guide and must be followed:

**Headings**
- Sentence case for all headings: capitalize only the first word and proper feature names
- Proper feature names keep their capitalization: "Agent Mode", "Warp Drive", "Oz", "Command Palette"
- ✅ `## How it works` — ❌ `## How It Works`
- ✅ `## Agent Mode settings` — ❌ `## Agent mode settings`

**Lists**
- Bold term + dash + description: `* **Term** - Description`
- Never use a colon: ❌ `* **Term**: Description`

**UI elements and paths**
- Bold for buttons, links, menu items: `Click **Save**`, not `` Click `Save` ``
- Bold each segment in a Settings path, leave `>` plain: `**Settings** > **AI** > **Knowledge**`

**Voice and tone**
- Second person: "you can," "allows you to"
- Active voice: "Warp indexes your codebase" — not "your codebase is indexed"
- Avoid "simple," "easy," "just" — these dismiss the reader's experience
- Present tense for how things work; imperative for instructions

**Frontmatter description**
- Write as a standalone summary that works as a search result snippet
- Lead with user benefit, include the feature name and key terms
- ✅ `Environments ensure your cloud agents run with a consistent toolchain. Learn when to use environments and how to configure them.`
- ❌ `This page describes environments.`

**Callout syntax** (Astro Starlight)
- `:::note` — supplemental context, tips
- `:::caution` — caveats, limitations
- `:::danger` — destructive or irreversible actions
- `:::tip` — confirmation of expected outcomes

**What to leave as `[TODO: docs reviewer — ...]` placeholders**
- Screenshots (not captured by this skill)
- Video/GIF embeds
- Exact Settings path if the feature hasn't shipped yet
- Final URL path (docs team confirms placement)
- Any behavior that remained unverified after engineer confirmation

---

## Step 5: Open the draft PR

After generating the draft, submit it to `warpdotdev/docs` automatically:

1. Clone `warpdotdev/docs` to a temp directory (or use the local clone if available)
2. Write the MDX file to `src/content/docs/<proposed-section>/<filename>.mdx`
3. Add a placeholder entry to `src/sidebar.ts` under the appropriate section (mark it `[TODO: docs reviewer — confirm placement]`)
4. Commit and push on a new branch named `docs/<spec-id>-feature-draft`
5. Open a **draft PR** in `warpdotdev/docs` with a description that includes:
   - The feature name and spec ID
   - A link to the original spec PR
   - A list of all `[UNVERIFIED]` and `[TODO]` items in the draft for reviewer attention
6. Request review from `@rachaelrenk`, `@petradonka`, and `@hongyi-chen`

---

## No-spec fallback

If `specs/<id>/PRODUCT.md` and `specs/<id>/TECH.md` don't exist, research the codebase first before interviewing the engineer.

**Research steps:**
1. Search `warpdotdev/warp-internal` (or `warp-server` depending on context) for the feature name and related terms: `gh search code "<feature-name>" --repo warpdotdev/warp-internal`
2. Read the most relevant source files to understand what the feature does
3. Check for spec files under a different ID: `gh api repos/warpdotdev/warp-internal/git/trees/HEAD?recursive=1 | grep -i spec`
4. Review recent merged PRs related to the feature: `gh pr list --search "<feature-name>" --state merged --repo warpdotdev/warp-internal --limit 10`

**After research,** build as complete a picture as possible, then use `ask_user_question` only for specific gaps you couldn't fill from the code — not as a broad interview. Frame the questions concretely: "I found the feature in `app/src/ai/`. Based on the code, here's what I understand: [summary]. I couldn't determine these two things: [specific questions]."

Build the outline from your research and the engineer's targeted answers, then proceed to Step 3 (outline confirmation) before drafting.

---

## Related skills

- `write-product-spec` — produces the `PRODUCT.md` this skill reads
- `write-tech-spec` — produces the `TECH.md` this skill reads
