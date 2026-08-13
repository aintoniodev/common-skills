---
name: research
description: Delegate noisy investigation to one or more subagents so the orchestrator's context stays clean, then work from the distilled answer. Use this skill whenever answering a question would require reading many files, long logs, large diffs, or wide codebase surveys — i.e. when producing the answer generates far more noise than the answer itself. Use it for "how does X work", "where is Y used", "what's the root cause of Z", "summarize this PR/log" style questions, and reach for it liberally before reading a pile of files inline.
---

# Research

Use this skill to answer a question by delegating the *work of finding the answer* to a subagent, so that the byproducts of that work — file contents, log noise, dead-end reads — never enter your own context. You get back a distilled answer plus the evidence that supports it, and you stay sharp for the actual task.

## Why this matters

Your context window is your most valuable and limited resource. Reading twenty files to discover that three of them mattered permanently pollutes your context with seventeen files of noise, degrading every subsequent decision you make. A subagent absorbs that noise on your behalf and hands you only the signal. Think of it as asking a colleague to dig through the archives and report back, rather than dumping the whole archive on your desk.

## If your own assignment is already the investigation

This skill's trigger ("would require reading many files", "reach for it liberally") reads the same whether you are the one asking for research or the one who was asked. Before delegating, check which one you are.

If you were yourself dispatched to investigate something — a subagent, a child agent, or any delegate whose brief is "look into X and report/distill/summarize" — you are already the colleague digging through the archives for someone else. Delegating again does not remove noise from anyone's context that matters: it just adds a layer of latency and token cost between you and the answer you were asked to produce. Do the reading yourself.

The one legitimate exception is when your own brief genuinely decomposes into independent sub-parts you cannot investigate faster alone (see "Single vs. parallel" below). That is the same tradeoff your own dispatcher made when it delegated to you, not a redundant one — but a single, cohesive investigation assigned to you is not that case, even if it touches many files.

## When to use it

Reach for research delegation when **the cost of producing the answer is far greater than the answer itself**. Strong signals:

- You'd need to read many files to find the few that are relevant.
- You'd need to wade through long test output, CI logs, or stack traces to extract a failure.
- You'd need to survey how a pattern, API, or symbol is used across the whole repo.
- You'd need to read and summarize a large diff or PR.
- The question has several independent sub-parts that could be investigated separately.

**Examples — good fits:**

- "What's the root cause of this failing test?" (the subagent reads the logs and traces the code; you get the cause)
- "How is `SessionManager` used across the codebase?" (the subagent greps and reads; you get a summary with call sites)
- "Summarize what this 4,000-line PR changes and why." (the subagent reads the diff; you get the shape of it)

**Examples — do NOT delegate:**

- Reading 2–3 files you already know you need. Just read them directly; delegation adds latency for no context savings.
- A single `grep` or one-line lookup. Do it yourself.
- **Anything where you need the raw material for your next step.** If you're about to *edit* the files you'd be reading, delegating is counterproductive — you'd just have to re-read them yourself to make the change. Research delegation pays off when the output is a *conclusion*, not when it's *material you'll work on directly*.
- **Your own assignment is already "go investigate this."** See "If your own assignment is already the investigation" above — do the work instead of handing it to a subagent of your own.

The cost of a subagent is real (latency and tokens), so the test is always: does the noise I'd avoid outweigh that cost?

## How to do it

### Single vs. parallel

Default to a **single subagent**. Spawn **multiple subagents in parallel** only when the question genuinely decomposes into independent sub-parts that don't need to share intermediate findings — for example, "how does auth work AND how does billing work AND how does the rate limiter work" are three independent investigations that can run at once. Parallelism is a capability worth using when the parts are truly independent, since separate subagents can investigate simultaneously; but don't force a single coherent question into artificial fragments.

### Brief the subagent well

The subagent does not share your intent, so spell it out. A good research brief includes:

- The exact question to answer.
- Where to look (repo path, branch, suspected files/symbols if you know them).
- That it is **read-only** — it should investigate and report, not modify files, unless the task explicitly calls for changes.
- The output you want back (see below).

### Ask for signal, not transcript

Tell the subagent to return a **distilled answer plus its supporting evidence**, not a raw dump. Specifically:

1. The direct answer to the question.
2. The key evidence: exact file paths and symbols (e.g. `src/session.rs:142`, `fn reconnect`), so you can jump straight to what matters.
3. Anything surprising or any caveats/unknowns it hit.

The whole point is that the noise stays with the subagent. If a report comes back bloated, send a focused follow-up to the *same* subagent asking it to tighten the answer — it retains its context and can refine cheaply.

## After you get the answer

Work from the distilled result. If you later find you need the underlying files to make edits, read them directly at that point — now you know exactly which ones matter, so you read three files instead of twenty.
