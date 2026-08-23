---
name: optimize-prompt
description: 'Diagnose and optimize system prompts for LLM agents using a decision-chain method. Turns individual failure cases into reusable invariant fixes instead of case-by-case patches. Use when analyzing why a model misjudged or misrouted an input, when asked to fix or tune a prompt, when deciding whether a fix belongs in the prompt or in runtime code, or when validating a prompt change against affected test cases. Triggers: prompt optimization, tune the prompt, fix the prompt, why did the model get this wrong, 提示词优化, 优化提示词, 改提示词, 为什么误判.'
argument-hint: 'Describe the failure case, paste the model output, or point to the prompt diff to analyze.'
---

# Optimize Prompt: Decision-Chain Diagnosis and Invariant Fixes

Use this skill when an LLM agent produced a wrong output and the prompt is the suspected layer to fix.

This skill turns single failures into reusable decision-chain defects. It follows one philosophy above all: **patching by case is a failure signal.** The goal is to keep only the rules that decide the main outcome and cannot be replaced — prefer deleting or merging over appending.

## When to Use

Use this skill for:

- diagnosing why a model misjudged, misrouted, or hallucinated on specific inputs
- fixing or tuning a system prompt after regression cases
- deciding whether a constraint belongs in the prompt or belongs in runtime code
- validating a prompt change without running full regression suites

Do **not** use this skill for:

- writing a system prompt from scratch with no failure signal
- runtime code changes unrelated to prompt behavior
- evaluating model quality in general (benchmarks, sampling strategy)

## Core Rules

1. **Locate the first broken layer, not the ugly final text.** Model the task as an explicit decision chain and find the earliest stage where behavior diverges.
2. **Never let later results pollute earlier facts.** Upstream facts must be derived from input only — never rewritten or fabricated to make a candidate answer fit.
3. **Classify by mechanism, not by surface.** Two failures that swap names but share a mechanism are one case; drop non-discriminative labels.
4. **Fix one root cause per change.**
5. **Write invariants, not instances.** New rules must be universal constraints; never patch toward a specific input or expected answer.
6. **Keep net length flat or shrinking.** Every new rule must replace or merge conflicting/duplicate ones. Use abstract examples only for boundaries that prose cannot express.
7. **Know the prompt-only boundary.** Deterministic cross-field checks, tool-call ordering, and retrieval termination conditions do not belong in a prompt — move them to runtime gates and say so.
8. **Assert behavior, not wording.** Select affected tests from the diff; never loosen assertions to make a change pass.

## Procedure

### 1. Reconstruct the current scene

1. Read repository instructions (`AGENTS.md`, `docs/testing.md`, etc.) and check `git status` plus the current prompt and its diff. Never reason from stale drafts or cached runs.
2. Preserve the full shape of the failing request: multi-part inputs, attachment order, user-stated constraints and exclusions.
3. Compare against the existing case catalog if one exists. A new case earns a place only if it covers a mechanism no existing case covers; otherwise delete or merge it.

### 2. Build a diagnostic snapshot

Before proposing any edit, record internally — per stage of the chain — what the model had available and what it concluded:

- **input understanding:** what the user actually asked, stated, and explicitly excluded
- **facts:** what is confirmed vs. conditional vs. negated
- **intermediate decisions:** classifications, levels, gate hits, retrieval calls
- **final output:** the five-or-N fields your agent must emit

Then walk the chain front-to-back and mark the **first** stage whose conclusion does not follow from its inputs. Also inspect tool-call traces and logs for that stage — do not judge only the final wording.

A generic reference chain for tool-using agents:

```text
scope → evidence → risk/constraint factors → derived classification → gates → candidates → output
```

Adapt the stages to the domain; keep them ordered and keep each stage fed only by upstream stages.

### 3. Apply the invariants at the broken layer

At the identified stage, check which invariant was violated. The recurring families:

- **Evidence priority:** confirmed facts outrank candidate references; explicit negations outrank conventions; insufficient information stays conditional — never fabricate to force a match.
- **Derivation direction:** downstream values derive one-way from confirmed upstream facts. Candidates can never raise or lower a derivation.
- **Gate semantics:** split compound conditions before judging scope; match by meaning within boundary, never generalize across boundaries; a hard gate stops the pipeline — candidates may not bypass it.
- **Retrieval discipline:** keyword recall is candidacy only, never confirmation; "only weak candidates found" means *search incomplete*, not *answer with the best of them*.
- **Output contract:** fixed fields always emitted, business language only, no internal jargon, aggregation rules stated once.

### 4. Choose the modification layer

Prefer editing the prompt's semantic boundaries, evidence priorities, decision order, and output constraints. Every edit must satisfy:

1. one root cause per change
2. universal invariants only — no occupation, product name, or this-time answer baked in
3. new rules replace or merge existing ones; total length does not grow
4. abstract examples only where words alone fail
5. tests are never loosened to hide bad behavior

**Stop stacking prompt rules and report the prompt-only boundary** when you see:

- final output is correct, but forbidden tool calls still happen before the terminal state
- the model repeatedly ignores retrieval completion conditions or call ordering
- deterministic cross-field invariants keep breaking across attempts

These belong in runtime gates, structured state, or output normalization — say so explicitly instead of adding a sixth restatement of the same rule.

### 5. Verify selectively

- Map the prompt diff to affected mechanisms; pick exactly the cases covering those mechanisms. Run full suites only on explicit request.
- If the diff cannot be classified into known mechanisms, do not run live cases until someone classifies it or explicitly chooses full coverage.
- Assert field content with deterministic business invariants; fall back to field-level LLM judging only when no stable assertion exists.
- For gated behaviors, assert both the final fields **and** that forbidden tools were not called.
- Validate with fresh processes and clean state; never prove a fix with a stale server or cached results.
- After changes, run the repo's lint/typecheck/static checks.

### 6. Report results

Lead with the outcome, then cover:

1. the first broken layer and root cause
2. which universal rule changed, and which conflicts were deleted or merged
3. which cases were selected and why they were affected
4. whether real outputs and tool traces passed
5. which validations were skipped and why
6. if the prompt-only boundary was hit: the minimal runtime constraint needed next

## Hard Stops

Stop and call out the issue before proceeding if:

- you cannot name the first broken layer and are about to edit based on the final text alone
- the proposed rule mentions a specific input value, entity, or expected answer from the current case
- the fix would grow the prompt without deleting or merging anything
- the failure is a deterministic cross-field or ordering violation and you are still writing prompt prose for it
- you cannot map the diff to affected cases and are about to run everything (or nothing) anyway

## Gotchas

| What happened | Rule |
| --- | --- |
| Fix judged from the final answer text only | Walk the chain; find the first broken stage and its trace |
| The model invented facts to make a candidate fit | Backward contamination — upstream facts come from input only |
| Each new bug added a new rule and the prompt keeps growing | Merge into one invariant; net length must shrink |
| Same failure keeps returning despite reworded rules | Check the prompt-only boundary — move it to runtime |
| Full suite ran (or nothing ran) for a tiny diff | Map diff → mechanisms → affected cases; verify selectively |
| Test passed because assertions were relaxed | Never loosen assertions to mask bad behavior |
| Weak recall treated as a valid answer | Recall is candidacy; incomplete search means keep searching |

## Output Expectations

A good optimization run produces:

- a named first-broken-layer diagnosis backed by traces, not vibes
- one minimal prompt diff built from universal invariants, with length flat or reduced
- a selective set of affected cases run green — including negative assertions for gated behaviors
- an explicit statement when the fix outgrew the prompt layer, plus the minimal runtime remedy
