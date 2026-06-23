---
name: tdd
description: 'Use Test-Driven Development for bug fixes, features, regression tests, and safe refactors. Follows Red → Green → Refactor, writes failing tests first, adapts to the repository''s test framework and verification commands, and avoids implementation-first changes. Triggers: TDD, test-first, red green refactor, regression test, behavior test, failing test first, use TDD to fix bug, write tests before code, 用 TDD 修 bug, 先写测试, 回归测试, 红绿重构.'
argument-hint: 'Describe the bug, feature, or change to drive with TDD.'
---

# TDD: Red → Green → Refactor

Use this skill when the user wants a code change to be driven by tests first.

This skill is for **methodology**, not repository-specific release workflow. It helps the agent:

- understand the behavior to protect or introduce
- write a failing test before implementation when feasible
- make the smallest change needed to turn the test green
- refactor only after tests pass
- adapt to the target repository instead of assuming Jest, pytest, pnpm, or any single stack

## When to Use

Use this skill for:

- bug fixes that need a regression test
- new features that should start with a behavior test
- risky refactors where test coverage should guard the change
- requests like “use TDD”, “write the test first”, “add a regression test”, or “Red Green Refactor”

Do **not** use this skill for:

- tiny text-only edits with no behavior change
- pure documentation work
- one-off exploratory scripts where tests add no value
- tasks where the user explicitly asks to skip tests

## Core Rules

1. **Grill relentlessly before you write.** Phase 1: nail down every fuzzy detail, branch condition, and acceptance criterion — ambiguity kills. Phase 2: challenge the proposed solution — is it the simplest, does it fit the architecture, is there already a way to do it? A well-tested answer to the wrong question is still wrong.
2. **Test first when feasible.** Prefer a failing test before changing implementation.
3. **Protect behavior, not internals.** Test externally visible outcomes whenever possible.
4. **Go minimal in Green.** Write the smallest implementation that satisfies the failing test.
5. **Refactor only on green.** If tests are red, do not mix in cleanup work.
6. **Adapt to the repo.** Detect the actual test framework, test file layout, and validation commands from the repository.
7. **State limits clearly.** If a true failing test cannot be written, explain why and switch to best-effort mode explicitly.

## Procedure

### 1. Grill relentlessly (before any code)

**The worst code is code that shouldn't have been written — either because the problem wasn't understood, or the proposed solution was wrong.**

Before typing a single line, grill on two fronts. Do not proceed until every branch node is resolved.

---

**Phase 1: Nail down the problem (clarity before correctness)**

Most user inputs are fuzzy. A bug report that says "it crashes when I click save." A feature request that says "add caching." A refactor ask that says "clean up this module." None of these are actionable. Grill until the ambiguity is gone:

- **What exactly happens, and what should happen?** Get concrete: inputs, outputs, error messages, stack traces, timing. "It's slow" → where, under what load, what's the number? "It's broken" → broken how, since when, what's the first observable symptom?
- **What's the scope boundary?** What's in, what's explicitly out? If the user says "add error handling," do they mean network errors, validation errors, panics, or all three? If they say "refactor the auth module," which files, which behaviors must not change?
- **What are the branch conditions?** For every conditional in the task — "if this, then that" — ask: is this branch defined? If the user says "if the API returns an error, show a message," what about timeout vs 4xx vs 5xx? What about when the error body is empty?
- **What's the acceptance criterion?** How will we know this is done? "Make it faster" → from what to what, measured how? "Fix the login bug" → on which browser/device, with which auth provider, under which conditions?

Keep asking until the answer to "what exactly do we need to do?" fits in one unambiguous sentence. If the user can't answer, that's the first problem to solve — not the code.

---

**Phase 2: Challenge the solution (correctness after clarity)**

Once the problem is nailed down, question whether the proposed solution is the right one:

- **Problem framing:** Is this the root cause, or a symptom? Has this been "fixed" before — and why didn't it stick?
- **Simplest fix:** What's the minimal thing that could work? What alternatives were considered?
- **Architecture fit:** Does the proposed approach work with the grain of the codebase, or fight it? Is there already a function, utility, or pattern that does this?
- **Hidden assumptions:** What must be true for this to work? What external systems, invariants, or undocumented contracts does it depend on? Who else depends on the code being changed?
- **Push back:** If the proposed solution is needlessly complex → propose a simpler one and explain why. If it duplicates existing functionality → point to the existing solution. If the problem is better solved elsewhere (upstream, in config, in process) → say so explicitly.

---

Do not skip this step just because the user sounds confident. Confidence and correctness are uncorrelated. A crisp answer to a dumb question is still dumb. An elegant implementation of the wrong problem is still wrong.

If the problem is too fuzzy to proceed, grill until it isn't. If the approach doesn't survive the challenge, surface the better alternative and get alignment. Only then move forward.

### 2. Understand the task

Classify the work:

- **Bug fix** → reproduce existing broken behavior with a regression test
- **Feature** → define expected behavior with a new test
- **Refactor-safe change** → tighten or add tests around current behavior before changing structure

Read the relevant implementation and nearby tests first. Match the repository's naming, assertion style, fixtures, and test placement.

For repository adaptation, load [the adaptation guide](./references/adaptation-guide.md).

### 3. Find the test seam

Before writing code, decide:

- which public behavior should be asserted
- where the test belongs
- what is the smallest test scope that proves the change
- which command can run the narrowest useful test slice

Prefer the narrowest test that captures the real behavior. A focused regression test beats a huge integration detour.

### 4. Write the failing test (Red)

Write the test before changing implementation.

For bug fixes:
- reproduce the bug in one test
- assert the correct behavior, not the broken one

For features:
- write a behavior test that describes the intended outcome
- keep the first test small enough to drive one increment

Then run the smallest relevant test command and confirm it fails for the expected reason.

If the test passes immediately, one of three things is true:

- the bug was not reproduced
- the code already works
- the test is too weak

Fix that before moving on.

### 5. Implement the smallest change (Green)

Change production code only after the failing test exists.

Rules for Green:

- keep the change tightly scoped
- avoid drive-by refactors
- do not change unrelated behavior just because the file is open
- prefer existing abstractions unless the test proves a new seam is necessary

Re-run the narrowest relevant tests until they pass.

### 6. Refactor on green

Once the tests are green:

- remove duplication
- improve names and structure
- align with local architecture and conventions
- keep behavior unchanged

Run the same tests again after each meaningful cleanup step.

### 7. Run broader validation

After the focused tests are green, run the repository's broader validation command set.

Detection order:

1. repository instructions such as `AGENTS.md`, `copilot-instructions.md`, or local customization files
2. package manifests and scripts
3. test/build/lint configuration files
4. existing CI workflow commands
5. existing contributor conventions visible in nearby files

If no reliable command can be determined, state that explicitly instead of pretending validation happened.

### 8. Report outcome

Summarize:

- what failing test was added or updated
- what implementation changed to make it pass
- what validation was run
- whether any limits or follow-up work remain

## Best-Effort Mode

Sometimes strict Red is blocked by environment or architecture. Examples:

- external systems cannot be reproduced locally
- the code has no practical seam yet and creating one would be a larger design task
- the repository lacks a runnable test setup

In those cases:

1. say why strict TDD is blocked
2. add the closest useful test if possible
3. keep the implementation minimal and reversible
4. describe what test should exist once the blocker is removed

Best-effort mode is an exception, not the default.

## Hard Stops

Stop and call out the issue before proceeding if:

- the user's requirements are still fuzzy — branch conditions, scope boundaries, inputs/outputs, or acceptance criteria are undefined — and you haven't grilled to resolve them
- you have not questioned the user's proposed solution — clarity is not correctness; confidence is not correctness
- the user's approach fights the architecture, duplicates existing functionality, or is needlessly complex — and you haven't proposed a better alternative
- you are about to implement behavior without first checking whether a test can capture it
- you are about to refactor unrelated code during the Green phase
- you cannot identify where tests belong and have not inspected existing test patterns
- you are about to claim validation without running a real command

## Gotchas

| What happened | Rule |
| --- | --- |
| The user's request was vague — "add caching," "fix the login," "make it faster" | Grill until the problem is one unambiguous sentence; don't implement ambiguity |
| The agent accepted the user's solution without questioning it | Grill the approach — confidence is not correctness; propose alternatives when warranted |
| The agent jumped straight to implementation | Go back and write or strengthen the test first |
| The failing test failed for the wrong reason | Fix the test setup before coding the solution |
| The first test required too much setup | Shrink scope; choose a narrower seam |
| The fix needed many files immediately | Re-check whether the first test increment is too large |
| Refactor work expanded after tests passed | Keep refactor separate from behavior change and keep re-running tests |
| The repo uses unfamiliar tooling | Detect and mirror local patterns; do not assume a stack from memory |

## Output Expectations

A good TDD run usually produces:

- one new or updated failing test that demonstrated the need for change
- one minimal implementation change that made it pass
- evidence of focused and broader validation
- a clear note when strict TDD could not be followed end-to-end
