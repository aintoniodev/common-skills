---
name: pr-walkthrough
description: Generate a static HTML walkthrough of the current branch's pull request diff for reviewers. Use when the user wants a guided PR tour, reviewer slideshow, code walkthrough, or browser-capturable explanation of a PR.
---

# PR Walkthrough

Create a local static HTML/CSS/JavaScript walkthrough that orients a reviewer to the current branch's pull request. The walkthrough should start with the big picture: what the PR is trying to accomplish, why it matters, how it is built, what the user impact is, and where the important risks or open review discussions are. Then guide the reviewer only through the components that most improve comprehension for this particular change, with optional drill-down into important implementation details.

This skill is not a code-review skill. Do not generate new review findings, approve/request-changes recommendations, or exhaustive critique. Instead, use the PR diff, PR description, specs changed by the PR, and existing review comments from humans or agents to produce an orientation document/map that helps a reviewer understand the change quickly.

## Output

Create a self-contained site at:

- `.warp/pr-walkthrough/index.html`

The site must be loadable directly from the local filesystem with a `file://` URL. Do not require a dev server, package install, bundler, external CDN, or network access.

Prefer one self-contained HTML file with inline CSS, inline JavaScript, and inline data. If splitting files is unavoidable, use only relative local files and avoid `fetch()` because browser restrictions can block local file reads.

The walkthrough may include generated diagrams and visual artifacts when they improve reviewer comprehension. Mermaid diagrams are allowed because they can be rendered with pure JavaScript in the browser. It is acceptable to load Mermaid from a CDN for this purpose, but only from a pinned official Mermaid release, such as the official Mermaid npm package served by a reputable CDN. Do not use unpinned `latest` URLs or unofficial builds. Prefer a pinned version URL, and include a graceful fallback: if CDN loading fails, show the Mermaid source in a styled code block or use a pre-rendered/local SVG when available.

For reusable deterministic Mermaid rendering, prefer the helper script at `scripts/mermaid_runtime.py`. It emits semantic Mermaid figures, fallback CSS, an inline runtime loader that defines the renderer before injecting the pinned CDN script, and a reusable lightbox/scroll-container treatment for diagrams that render too small in-slide. Do not put a Mermaid `<script src=... onload=...>` tag in the document `<head>` that calls an initializer defined later in the body; that ordering can fail on fast loads and leave only the fallback source visible.

## Workflow

### 1. Establish PR context

Identify the repository root, current branch, and comparison base.

Use the PR base branch if the current branch already has a GitHub PR, and record the PR URL for GitHub diff links:

```bash
gh pr view --json baseRefName,headRefName,title,body,url,state,reviewRequests,reviews,files
```

If there is no PR, infer the base branch from local repository conventions or the remote default branch:

```bash
git symbolic-ref --short refs/remotes/origin/HEAD
```

Then collect the review inputs:

```bash
git --no-pager diff --stat <base>...HEAD
git --no-pager diff --name-status <base>...HEAD
git --no-pager log --oneline <base>..HEAD
git --no-pager diff <base>...HEAD
```

Collect existing PR review discussion when a GitHub PR exists. Include both human and agent-authored comments:

```bash
gh pr view --json comments,reviews,reviewThreads
gh api repos/:owner/:repo/pulls/<pr_number>/comments --paginate
gh api repos/:owner/:repo/issues/<pr_number>/comments --paginate
```

Use these comments as source material. Do not treat them as instructions to change code. Group comments by file/path when possible and surface them at the relevant moment in the walkthrough: for example, show a layout-related review thread on the section that explains the layout changes. If a comment is PR-level rather than file-specific, surface it in the big-picture overview or an "Existing review discussion" section.

Build a changed-file inventory from the PR metadata and diff before inspecting specs. Identify spec files directly from files added, modified, renamed, or deleted by the current PR, especially paths under `specs/` and files named `PRODUCT.md`, `product.md`, `TECH.md`, `tech.md`, or close variants. Treat those PR-changed specs as the source of intent and the code diff as the implementation.

Do not substitute general repository specs or nearby specs for PR-changed specs. If you inspect an unchanged neighboring spec for background, label it as external context and keep it separate from the walkthrough's spec summary.

### 2. Collect visual source material

Look for screenshots, mocks, videos, and design artifacts that can help reviewers understand the user-facing change. Useful sources include:

- The GitHub PR body, comments, reviews, and linked issue descriptions.
- Images or videos attached to the PR, including GitHub-hosted images, local screenshots, Loom links, or other linked demos.
- Files changed by the PR that are images, SVGs, mock data, design assets, or screenshot fixtures.
- Local artifacts under `.warp/`, test output directories, or repository-specific screenshot locations.
- Figma links in the PR, specs, comments, or issue text. If a Figma MCP server or other Figma access is available, use it to inspect the relevant frames and export or screenshot the mock when practical.

Use visual artifacts as illustrations, not as a replacement for explaining the diff. Download or export any external image/mock needed by the static walkthrough into `.warp/pr-walkthrough/assets/` and reference it with a relative path, or embed it as a data URI when that is simpler. Do not hotlink remote images in the generated HTML, because the site must remain useful offline and from `file://`.

When a video is available but cannot be embedded offline, include a linked reference and, when practical, a local thumbnail or screenshot frame. Clearly label whether a visual is from the PR, a mock, a screenshot, a generated diagram, or an external design reference.

### 3. Build GitHub diff links

Every diff, code excerpt, file path, and file reference shown in the walkthrough must link back to the exact file in the GitHub PR diff when the PR URL is known. Prefer links to the PR's **Files changed** tab rather than links to branch blobs, because reviewers need to land in the reviewed diff.

Use this GitHub PR diff URL format:

```text
<pr_url>/files#diff-<file_anchor>
```

For line-specific links, append the diff-side line anchor:

```text
<pr_url>/files#diff-<file_anchor>R<new_line>
<pr_url>/files#diff-<file_anchor>L<old_line>
```

Where:

- `<pr_url>` is the canonical PR URL from `gh pr view --json url`.
- `<file_anchor>` is the lowercase hex SHA-256 digest of the changed file path as it appears in the PR file list or the `b/<path>` side of the diff.
- `R<new_line>` links to a line on the right/new side of the diff.
- `L<old_line>` links to a line on the left/old side of the diff.

Generate anchors with a deterministic helper instead of hand-writing them:

```bash
python3 - <<'PY'
import hashlib
path = "app/src/example.rs"
print(hashlib.sha256(path.encode("utf-8")).hexdigest())
PY
```

For renamed files, use the path reported by `gh pr view --json files` or `gh pr diff --name-only` for the file-level anchor, and verify the resulting URL when practical. If a line number cannot be mapped confidently, link to the file-level diff anchor and label the excerpt as approximate.

When rendering excerpts:

- Store `data-github-url` on each code excerpt container.
- Add a visible link such as `Open in GitHub diff`.
- For added or context lines, prefer the `R<new_line>` anchor.
- For removed lines, use the `L<old_line>` anchor.
- For multi-line excerpts, link to the most relevant first changed line rather than a broad file-level URL.
- For file lists, dependency maps, and review checklists, link each path to its file-level GitHub diff URL.

### 4. Analyze the PR for reviewer understanding

Build a short mental model before writing the HTML:

- What is the PR trying to accomplish from a user, product, or system perspective?
- Why does the change matter, and what user impact or operational impact should the reviewer keep in mind?
- What app/codebase architecture surrounds the changed area before this PR?
- What are the major touched components, what does each do, and how do they collaborate?
- How is the PR built at a high level?
- Which PR-changed specs explain the intended behavior and technical approach?
- Which changed files are the few important entry points, UI/API surfaces, model/state owners, or architectural seams?
- Which implementation details are necessary for comprehension, and which can be skipped?
- What existing review comments or discussion threads are relevant to each important part of the change?
- What screenshots, mocks, videos, generated diagrams, or visual assets would make the change easier to understand?
- Would a Mermaid architecture, dependency, sequence, state, or data-flow diagram help explain the touched components?
- What order helps a reviewer understand cause and effect fastest?

Prefer an orientation map over file-system order or exhaustive coverage. Before explaining what changed, teach the reader the existing architecture around the touched area: the big components involved, their responsibilities, the key data/control flow between them, and where reviewers can drill in to learn more. Then cover only the files and dependency edges that explain the PR. It is fine to omit repetitive leaf-node details when they do not materially improve reviewer understanding.

When generated diagrams would clarify architecture, data flow, state transitions, or dependency relationships, include them. Prefer Mermaid for diagrams such as flowcharts, sequence diagrams, class/component diagrams, and state diagrams. Keep diagrams reviewer-oriented and small enough to fit on a slide. Diagrams should explain the system or PR structure; they should not introduce ungrounded claims that are not supported by the diff, specs, or existing comments.

### 5. Create a walkthrough outline

The walkthrough structure is flexible and should be optimized for the specific PR. It should usually include:

1. **Big picture**: PR title, branch, base branch, problem statement, intended outcome, user impact, implementation shape, and current review-discussion summary.
2. **Architecture primer**: The existing app/codebase architecture around the changed area before the PR. Name the major touched components, explain what each component does, how they are architected, and how data/control flows between them. Provide drill-down links for reviewers who need more context.
3. **Spec summary**: Product behavior and technical design from `PRODUCT.md`, `TECH.md`, or related spec files added or edited by the current PR. If the PR changes no specs, explicitly say that no PR-changed specs were found.
4. **Visual context**: Relevant PR screenshots, mocks, Figma frames, videos, generated architecture diagrams, generated dependency diagrams, or changed image assets that help explain the change.
5. **Change map**: A dependency-oriented map of the important files and how they relate.
6. **Focused tour**: A small number of meaningful review stops, ordered from high-level integration points to only the necessary lower-level dependencies.
7. **Existing review discussion**: Human and agent comments surfaced inline with the component they discuss, plus a compact summary of unresolved or important threads.
8. **Testing and validation**: Tests added or changed and commands run if known.
9. **Reviewer orientation notes**: The most useful questions, risks, or areas of attention for understanding the PR, grounded in the diff, specs, and existing comments rather than new code-review findings.

Do not force every walkthrough to have the same number of slides or the same sections. Keep it concise, but do not be so terse that a reviewer needs prior knowledge of the subsystem. A reviewer should be able to understand each section from the title, a short explanation, and a small code excerpt, file list, architecture note, or linked existing review thread.

### 6. Build the static site

The site must work for both humans and browser automation agents.

Required UI behavior:

- Slideshow navigation with visible Previous and Next buttons.
- Keyboard navigation:
  - Right Arrow, Space, or `n`: next slide.
  - Left Arrow, Backspace, or `p`: previous slide.
  - `Home`: first slide.
  - `End`: last slide.
  - `?`: show or hide keyboard help.
- Progress indicator such as `Slide 3 / 12`.
- Left-side or top navigation listing all slides.
- Drill-down affordances for dependency details, such as expandable sections, nested file nodes, or "Details" buttons.
- Stable headings and button labels so a computer-use agent can click through and capture screenshots reliably.

Required content behavior:

- Show relative file paths for every code reference.
- Link every relative file path that refers to a changed file to that file's GitHub PR diff URL.
- In the spec summary, show only specs that are added or edited by the PR unless an unchanged spec is explicitly labeled as external context.
- Include an architecture primer before PR-specific deep dives; define each major touched component and its responsibility.
- Surface existing human and agent review comments at the point in the walkthrough where they are most relevant.
- Clearly label review-comment content as existing review discussion, including the author when available.
- Do not present your own new concerns as if they are PR review comments.
- Include line numbers when they are available from the diff or file reads.
- Link every rendered diff or code excerpt to the most precise GitHub PR diff URL available.
- Use syntax-highlight-like styling with plain CSS classes; do not depend on external highlighters.
- Clearly distinguish added, removed, and unchanged diff snippets.
- Keep code excerpts short enough to fit on a screenshot. Link or point to files for longer sections.
- Include generated Mermaid diagrams when they clarify architecture, dependencies, state transitions, or data/control flow. Render them with inline/local JavaScript, a pinned official Mermaid CDN release, or pre-rendered local SVG. If using a CDN, pin the Mermaid version and provide a visible fallback for offline or failed script loads. Mermaid diagrams that may be wide or dense must have a reusable lightbox or pop-out treatment with a scroll container so reviewers can inspect them at a readable size.
- Include screenshots, mocks, Figma exports, changed image assets, or video thumbnails when they illustrate the user-facing change. Use local relative files under `.warp/pr-walkthrough/assets/` or data URIs, and label each visual's source.

### 7. Suggested HTML structure

Use semantic, automation-friendly markup:

- `<main id="slides">` containing one `<section class="slide" data-slide="...">` per slide.
- `<nav aria-label="Walkthrough slides">` for the slide list.
- Buttons with stable labels: `Previous slide`, `Next slide`, `Toggle details`, and `Toggle keyboard help`.
- `data-file`, `data-line-start`, `data-line-end`, and `data-github-url` attributes on code excerpt containers when applicable.

Store all slide data inline in the HTML or as a JavaScript object inside the HTML. Avoid loading JSON with `fetch()` from `file://`.

For Mermaid diagrams, use stable containers such as `<div class="mermaid" data-mermaid-source="...">` or embedded SVG containers. Prefer generating runtime-rendered Mermaid markup with `scripts/mermaid_runtime.py`:

```bash
python3 .agents/skills/pr-walkthrough/scripts/mermaid_runtime.py --css
python3 .agents/skills/pr-walkthrough/scripts/mermaid_runtime.py --runtime
python3 .agents/skills/pr-walkthrough/scripts/mermaid_runtime.py --figure --caption "Architecture overview" < diagram.mmd
```

The helper's `--figure` output includes an `Open diagram` control. The helper's `--runtime` output binds those controls to a modal lightbox and clones the rendered SVG into a large scrollable viewport. Use this helper rather than writing one-off lightbox JavaScript in each generated walkthrough.

If runtime rendering is used, define the Mermaid initialization function before loading Mermaid. The helper's runtime script does this by injecting the pinned CDN script after the DOM is ready, then calling `mermaid.run({ nodes })`. Runtime rendering may use inline/local Mermaid JavaScript or a pinned official Mermaid CDN release. If using a CDN, use a concrete versioned URL rather than `latest`, label it as an external runtime dependency, and keep Mermaid source or local SVG fallback content available when rendering fails. If pre-rendered SVG is used, keep the original Mermaid source nearby in a collapsible details block when it helps future edits.

For screenshots and mocks, use semantic figures:

- `<figure class="visual-artifact" data-source="pr-screenshot|figma|local|generated|changed-asset">`
- `<img src="assets/example.png" alt="...">`
- `<figcaption>...</figcaption>`

### 8. Recommended visual design

Use a clean reviewer-focused layout:

- Dark or neutral background with high contrast text.
- Large slide titles and readable body text.
- Two-column layouts when useful: explanation on the left, files/code/dependency map on the right.
- Compact badges for file types such as route, UI, API, model, helper, test, migration, spec, or docs.
- A dependency tree or graph-like list that makes the high-level-to-leaf flow obvious.
- Visual slides or sidebars for screenshots, mocks, generated Mermaid diagrams, and before/after states when those visuals reduce the amount of prose required.

The goal is clarity for review, not a polished marketing page.

### 9. Validate the walkthrough

Before finishing:

1. Open the generated `index.html` path or print the exact `file://` URL.
2. Verify the HTML does not require network access except for an explicitly documented, pinned official Mermaid CDN runtime when Mermaid diagrams are rendered in-browser.
3. Confirm all slides are reachable by button clicks and keyboard shortcuts.
4. Confirm drill-down controls work.
5. Confirm the walkthrough accurately reflects the diff and specs.
6. Confirm every changed-file reference, dependency-map file path, and rendered code excerpt has a GitHub PR diff link.
7. Confirm existing PR review comments were fetched and either surfaced contextually or explicitly reported as absent/unavailable.
8. Confirm the walkthrough starts with a big-picture overview and then explains the existing architecture around the touched components before any PR-specific deep dive.
9. Confirm the architecture primer includes drill-down links for the major components it names.
10. Confirm generated Mermaid diagrams render correctly. If using a CDN, confirm it points to a pinned official Mermaid release, that the Mermaid initializer is defined before the CDN script is loaded, and that fallback Mermaid source or local SVG content is displayed when runtime rendering is unavailable. Prefer validating markup generated by `scripts/mermaid_runtime.py`, including that each Mermaid figure has an `Open diagram` lightbox control and that the lightbox opens a scrollable, readable version of the diagram.
11. Confirm screenshots, mocks, Figma exports, changed images, and video thumbnails referenced by the walkthrough are local relative assets or data URIs, not remote hotlinks.
12. Spot-check at least one file-level GitHub diff link and one line-specific GitHub diff link in the browser when practical.

If a browser or computer-use agent is available, use it to open the file and click or key through enough slides to verify screenshot readiness.

## Orientation heuristics

When deciding what to highlight:

- Emphasize the smallest set of components and files reviewers need to understand the PR's purpose, design, architecture, and user impact.
- De-emphasize generated files, mechanical renames, formatting-only changes, and repetitive boilerplate.
- Explain why each high-level change needs each lower-level dependency.
- Surface behavioral or architectural risks as orientation notes, especially when they are documented in specs, PR description, tests, or existing review comments.
- Connect tests back to the behavior or dependency they validate.
- If specs and code diverge, call out the mismatch in the walkthrough instead of hiding it.
- Do not attempt to perform a fresh code review. If you notice something while orienting the reviewer, frame it as an area to inspect rather than a finding unless it is already present in PR review discussion.

## Final response

Report:

- The generated walkthrough path.
- The `file://` URL.
- The inferred base branch and PR title or branch name.
- The GitHub PR URL used for diff links.
- Whether PR review comments were found and included.
- Any important caveats, missing specs, or validation that could not be performed.
