---
name: write-feature-docs
description: Draft the first ~80% documentation page for a new Warp feature from its PRODUCT.md and/or TECH.md spec. Use when an engineer has written a spec and needs to produce a first-pass MDX draft for the warpdotdev/docs repo. Also handles features without specs via an interactive interview. Invoke this skill whenever an engineer mentions writing docs for a feature, drafting a docs page, creating feature documentation, starting the eng-docs workflow, or converting a spec into documentation. Works from warp-internal or warp-server.
---

# write-feature-docs

Draft the first ~80% documentation page for a new Warp feature. You read the feature's spec, generate a concise outline for the engineer to confirm, then produce a complete MDX draft ready for a draft PR to `warpdotdev/docs`.

The engineer's job is to verify **technical accuracy** — not polish prose, fix formatting, or know docs conventions. Your job is everything else.

## The workflow

1. Find the spec files for the feature
2. Generate a concise outline and present it in the terminal
3. Engineer confirms the outline is accurate (or replies with corrections)
4. Generate the full ~80% MDX draft from the confirmed outline
5. Tell the engineer how to submit it as a draft PR to `warpdotdev/docs`

---

## Step 1: Find the spec

Ask the engineer for the spec ID if they haven't provided it. The spec ID is one of:
- A Linear ticket number: `APP-1234`
- A GitHub issue (prefixed with `gh-`): `gh-4567`
- A short kebab-case feature name: `vertical-tabs-hover-sidecar`

Look for the spec files at:
- `specs/<id>/PRODUCT.md` — primary source: user-facing behavior, what and why
- `specs/<id>/TECH.md` — secondary source: implementation, data model

Read both files if both exist. `PRODUCT.md` is the primary driver for the docs content. Reference `TECH.md` only to check technical accuracy and understand implementation constraints — don't let implementation details leak into the user-facing prose.

If neither file exists, skip to [No-spec fallback](#no-spec-fallback).

---

## Step 2: Generate and present the outline

Read the spec(s) and generate a concise outline. **The outline has no prose** — its purpose is to give the engineer a quick technical accuracy check before you write anything.

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

KEY TERMS TO VERIFY
  - "<Term>": [your understanding — confirm this is accurate]
  - "<Term>": [your understanding — confirm this is accurate]
```

After printing the outline, say:

> "Does this outline accurately represent the feature? Reply with any corrections or say 'looks good' to proceed to the full draft."

Wait for the engineer's reply before continuing. Their reply is a free-form terminal response — they may correct steps, rename concepts, add missing behavior, or just confirm. Incorporate their feedback before drafting.

---

## Step 3: Generate the MDX draft

Generate a complete `.mdx` file based on the confirmed outline. The output should be ready to drop into `src/content/docs/<section>/<filename>.mdx` in the `warpdotdev/docs` repo.

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

**What to leave as placeholders**
Mark these with `[TODO: docs reviewer — ...]` in the draft:
- Screenshots (you can't capture live UI)
- Video/GIF embeds
- Exact Settings path if the feature hasn't shipped yet
- Final URL path (docs team confirms placement)
- Any behavior you're uncertain about after reading the spec

---

## No-spec fallback

If `specs/<id>/PRODUCT.md` and `specs/<id>/TECH.md` don't exist, use `ask_user_question` to interview the engineer. Ask about:

1. What this feature does in one sentence
2. The 2–3 most important things a user can do with it
3. The step-by-step actions a user takes to use it
4. Any prerequisites, limitations, or gotchas the reader needs to know
5. Any related features or pages to cross-reference

Build the outline from their answers, then present it for confirmation (Step 2) before drafting. Don't skip the outline confirmation step — it's the engineer's technical accuracy check regardless of whether a spec exists.

---

## Step 4: Handoff instructions

After presenting the draft, tell the engineer:

> "Here's your ~80% draft. To hand it off for docs review:
>
> 1. Save this file to the `warpdotdev/docs` repo at the proposed path above
> 2. Add an entry for it in `src/sidebar.ts` under the appropriate section
> 3. Open a **draft PR** in `warpdotdev/docs` — feature docs PRs don't need to be kept private before launch
>
> The docs team will take it from there: terminology, readability, screenshots, final placement, navigation, and redirects."

---

## Related skills

- `write-product-spec` — produces the `PRODUCT.md` this skill reads
- `write-tech-spec` — produces the `TECH.md` this skill reads
