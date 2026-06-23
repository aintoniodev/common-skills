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
6. Attempt screenshot capture via computer use (if available)
7. Open a draft PR in `warpdotdev/docs` and tag the docs team

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
- Screenshots where computer use fails the quality gate, is unavailable, or the feature isn't yet shipped
- Video/GIF embeds
- Exact Settings path if the feature hasn't shipped yet
- Final URL path (docs team confirms placement)
- Any behavior that remained unverified after engineer confirmation

---

## Step 4.5: Capture screenshots via computer use (if available)

After generating the draft, attempt to capture screenshots for any `[TODO: docs reviewer — screenshot needed]` placeholders using computer use. This step is **optional** — only run it if the `computer_use` tool is available. If computer use is unavailable, leave all placeholders as-is.

### Decide which screenshots to attempt

Only attempt screenshots where **all** of the following are true:
- The feature is already shipped (not behind a feature flag or unreleased)
- The UI state can be reliably navigated to programmatically
- The placeholder specifies a concrete UI surface (not vague like "show the feature working")

Skip screenshots that require account-specific state, specific data, or content that would expose sensitive information.

### Pre-capture setup

Before taking any screenshot:
1. Launch Warp at a consistent window size (use the `warp-internal-computer-use` skill for launch guidance)
2. Navigate to the relevant UI surface or trigger the relevant feature state
3. **Wait** for all animations to complete and the UI to be fully settled
4. Dismiss any unrelated popups, notifications, or toasts that aren't part of the feature being documented
5. Close any sidebar panels or panes not relevant to this screenshot
6. **Verify no sensitive data is visible**: check for tokens, API keys, private repo names, customer workspace data, email addresses, or personal information. If any is visible, do not take the screenshot.

### Capture protocol: predict → capture → verify → retry once

This is a structured self-verification loop. Do not skip it — it's the primary guard against wrong-state, wrong-crop, and wrong-framing captures.

**Step 1: State the expectation before capturing**

Before taking any screenshot, write out what you expect to see:

```
CAPTURE EXPECTATION
  Subject:            [The specific UI element or surface being documented]
  Expected elements:  [2-3 specific things that MUST be visible — e.g. a panel title, a button, a specific setting]
  Expected state:     [The UI state — e.g. "Settings panel open", "Modal visible", "Feature active and showing output"]
  Must not contain:   [Anything that must NOT be visible — e.g. sensitive data, unrelated popups, loading spinners]
```

**Step 2: Capture**

Take the screenshot.

**Step 3: View and verify against the expectation**

Use computer use to view the captured image, then check it against the expectation:

- Is the stated **subject** visible and clearly the focal point?
- Are all **expected elements** present?
- Is the UI in the **expected state** (not a transitional or loading state)?
- Is anything from **must not contain** visible?
- Is text **legible** at the target display width?

If all pass → proceed to the quality gate.

If any fail → **attempt once more**: re-navigate to the UI state, wait longer for the UI to settle, then re-capture and re-verify.

If the second attempt also fails → **discard** the screenshot and leave the `[TODO: docs reviewer — screenshot]` placeholder. Do not include a screenshot you can't verify.

**Step 4: Quality gate — final check before including**

- [ ] Text in the screenshot is **legible** at the target display size
- [ ] The documented UI element is **clearly the focal point** — not buried, cropped out, or obscured
- [ ] **No sensitive data** is visible (tokens, private repos, personal info, customer data)
- [ ] UI is in a **stable, non-loading state** — no spinners, skeleton screens, or transitional states
- [ ] Screenshot **matches the capture expectation** stated before capture
- [ ] The screenshot would make sense at its target rendered width without looking blurry or oversized

If any item fails, discard the screenshot and leave the `[TODO: docs reviewer — screenshot]` placeholder.

> **Maximum attempts per screenshot: 2.** If both fail, move on.

### Sizing — choose the closest standard width

- **Full-width (default)** — full-window captures, broad product surfaces, layouts where surrounding context matters
- **~375px** — narrow UI surfaces: popovers, command menus, side panes, dropdowns, focused interaction flows
- **~300–350px** — tightly cropped controls, chips, buttons, tooltips, small menus

Crop unnecessary empty space before sizing. Keep sequences of screenshots in the same section at the same width.

### Placement — where to insert the screenshot in the MDX

Insert each screenshot:
- **Immediately after** the paragraph that introduces the UI or state it shows
- **Near configuration instructions** — show settings panels or menus where users make choices
- **Near status or result explanations** — show completion states or outputs that help users recognize success
- **At the start of a visual feature page** — use a broad orientation screenshot early

Do **not** add a screenshot for every step in a procedure. Only add one where the visual genuinely aids comprehension.

### MDX format

```mdx
<figure>
  <img
    src="../../../assets/<section>/<feature-name>-<ui-state>.png"
    alt="[Descriptive alt text: what the image shows, not just 'screenshot']"
  />
  <figcaption>[Caption: complete sentence, ≤10 words, orient don’t instruct, no marketing language, sentence case, ends with period.]</figcaption>
</figure>
```

**Alt text rules:**
- Describe what the image shows, not just "screenshot"
- ✅ `alt="Agent permissions settings with 'Always allow' selected for file reads"`
- ❌ `alt="screenshot"` or `alt=""`

**Caption rules:**
- Orient the reader — describe what is shown, not what to do
- Complete sentence, ≤10 words ideally, never exceed ~20 words
- No marketing language (avoid "easily," "quickly," "powerful," "at a glance")
- Don't repeat the prose — the caption adds context, not an echo
- Don't list everything visible — name the subject
- ✅ `<figcaption>The Environments page in the Oz web app.</figcaption>`
- ❌ `<figcaption>Click the toast to jump to the agent’s session.</figcaption>` (procedural — put this in body text)

**File naming:** lowercase, hyphens, descriptive — e.g. `agent-mode-permissions-panel.png`

**File location:** Save PNGs to `src/assets/<section>/` in `warpdotdev/docs` (Astro optimizes them automatically).

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

## Ambient mode (called by scan-new-specs)

When this skill is invoked by `scan-new-specs` rather than an engineer directly, it runs in **ambient mode** — there is no interactive terminal session, so the outline confirmation step must be handled differently.

In ambient mode:

1. Complete Steps 1 and 2 (read spec, research codebase) as normal
2. **Skip the interactive outline confirmation.** Instead, embed the outline directly in the PR description as a checklist:

```markdown
## Docs outline (auto-generated)

The following outline was generated from the spec. **@<github-username>: please review and check off each item, or leave a comment with corrections.**

### Content structure
- [ ] H1: `<feature name>`
- [ ] Opening paragraph describes: [your 1-sentence summary]
- [ ] Key features section covers: [which capabilities]
- [ ] How it works section covers: [the conceptual model]
- [ ] `## <Usage section>` with steps: [numbered list]
- [ ] Related pages: [suggested cross-links]

### Items needing engineer verification ⚠️
- [ ] [UNVERIFIED item 1 — e.g. "Does this trigger automatically or require manual action?"]
- [ ] [UNVERIFIED item 2]

### Verified from codebase ✅
- [What was confirmed, e.g. "Feature flag: `my_feature` in warp-internal"]
```

3. Generate the full MDX draft (Step 4) with this constraint: **do not draft any content derived from `TECH.md` in ambient mode.** There is no engineer present to confirm what is confidential, so any detail that came exclusively from `TECH.md` (implementation internals, data model, server architecture, private API details) must be replaced with `[TODO: engineer to verify — pulled from TECH.md, confirm this is safe to publish]`. Only `PRODUCT.md` content and codebase-verified facts are safe to draft without confirmation.
4. **Attempt screenshots** (Step 4.5) — if computer use is available, run the predict-then-verify capture protocol for any screenshot placeholders. Include any screenshots that pass the quality gate in the draft.
5. Open the draft PR (Step 5) as normal — tag the spec author and docs reviewers
6. Do not post any interactive messages to the terminal; all output should go into the PR

---

## Related skills

- `write-product-spec` — produces the `PRODUCT.md` this skill reads
- `write-tech-spec` — produces the `TECH.md` this skill reads
- `scan-new-specs` — the scheduled agent that invokes this skill in ambient mode
