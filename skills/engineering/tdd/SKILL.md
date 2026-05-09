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

1. **Test first when feasible.** Prefer a failing test before changing implementation.
2. **Protect behavior, not internals.** Test externally visible outcomes whenever possible.
3. **Go minimal in Green.** Write the smallest implementation that satisfies the failing test.
4. **Refactor only on green.** If tests are red, do not mix in cleanup work.
5. **Adapt to the repo.** Detect the actual test framework, test file layout, and validation commands from the repository.
6. **State limits clearly.** If a true failing test cannot be written, explain why and switch to best-effort mode explicitly.

## Procedure

### 1. Understand the task

Classify the work:

- **Bug fix** → reproduce existing broken behavior with a regression test
- **Feature** → define expected behavior with a new test
- **Refactor-safe change** → tighten or add tests around current behavior before changing structure

Read the relevant implementation and nearby tests first. Match the repository's naming, assertion style, fixtures, and test placement.

For repository adaptation, load [the adaptation guide](./references/adaptation-guide.md).

### 2. Find the test seam

Before writing code, decide:

- which public behavior should be asserted
- where the test belongs
- what is the smallest test scope that proves the change
- which command can run the narrowest useful test slice

Prefer the narrowest test that captures the real behavior. A focused regression test beats a huge integration detour.

### 3. Write the failing test (Red)

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

### 4. Implement the smallest change (Green)

Change production code only after the failing test exists.

Rules for Green:

- keep the change tightly scoped
- avoid drive-by refactors
- do not change unrelated behavior just because the file is open
- prefer existing abstractions unless the test proves a new seam is necessary

Re-run the narrowest relevant tests until they pass.

### 5. Refactor on green

Once the tests are green:

- remove duplication
- improve names and structure
- align with local architecture and conventions
- keep behavior unchanged

Run the same tests again after each meaningful cleanup step.

### 6. Run broader validation

After the focused tests are green, run the repository's broader validation command set.

Detection order:

1. repository instructions such as `AGENTS.md`, `copilot-instructions.md`, or local customization files
2. package manifests and scripts
3. test/build/lint configuration files
4. existing CI workflow commands
5. existing contributor conventions visible in nearby files

If no reliable command can be determined, state that explicitly instead of pretending validation happened.

### 7. Report outcome

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

- you are about to implement behavior without first checking whether a test can capture it
- you are about to refactor unrelated code during the Green phase
- you cannot identify where tests belong and have not inspected existing test patterns
- you are about to claim validation without running a real command

## Gotchas

| What happened | Rule |
| --- | --- |
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
