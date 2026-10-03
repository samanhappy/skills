---
name: tdd
description: 'Use Test-Driven Development for bug fixes, features, regression tests, and safe refactors. Follows Red → Green → Refactor, writes failing tests first, adapts to the repository''s test framework and verification commands, and avoids implementation-first changes. Triggers: TDD, test-first, red green refactor, regression test, behavior test, failing test first, use TDD to fix bug, write tests before code, 用 TDD 修 bug, 先写测试, 回归测试, 红绿重构.'
argument-hint: 'Describe the bug, feature, or change to drive with TDD.'
---

# TDD: Red → Green → Refactor

A disciplined, feedback-driven workflow that turns requirements into verified behavior. Drives changes with focused tests first, keeps changes minimal, and guards against both model complacency and implementation-first drift.

## When to Use

- Bug fixes requiring regression prevention
- New features requiring behavior verification
- Structural refactors that must preserve existing semantics
- Explicit requests for TDD, "test first", or "Red-Green-Refactor"

**Do NOT use for:**
- Pure text, comments, or documentation changes
- Exploratory throwaway scripts
- Pure visual styling, layout, or aesthetic tweaks (use Before/After visual comparison instead)

---

## Core Invariants

1. **Inspect before asking.** Ground all questions and challenges in existing code and test conventions. Never interrogate in a vacuum.
2. **Challenge the approach.** Confidence is not correctness. If a proposed solution duplicates existing tools, fights architecture, or overcomplicates, propose the simpler alternative.
3. **Behavior over internals.** Assert externally observable outcomes, not private variables, implementation details, or CSS classes.
4. **Valid Red only.** A failing test is only valid when it cleanly fails on an asserted behavioral contract. Syntax errors, bad imports, or broken harnesses do not count as Red.
5. **Minimal Green.** Write only the code required to make the failing test pass. No drive-by refactoring during Green.
6. **Refactor only on Green.** Clean up duplication and structure only when all tests pass, and re-run tests after each step.
7. **Zero pollution.** Tests must be isolated and idempotent. Teardown temporary files, reset mocks, and rollback state mutations.
8. **Honor repository reality.** Detect and mirror local test frameworks, runners, and conventions. Never assume stacks from memory.

---

## Workflow: The State Machine

```text
[0. Frame & Challenge] ──> [1. Red (Valid Fail)] ──> [2. Green (Minimal Fix)] ──> [3. Refactor on Green]
        │                           ▲                                                     │
        │                           └──────────────── (Next slice) ───────────────────────┘
        └──────── (Pure visual UI change) ──> [Visual Comparison (Before/After Screenshots)]
```

### 0. Frame & Challenge (Before Touching Code)

1. **Inspect first**: Read relevant implementation and nearby test files. Discover local test commands, runners, and conventions before forming opinions.
2. **Calibrate clarity**:
   - *Clear spec*: Confirm scope and proceed immediately.
   - *Ambiguous spec*: Clarify inputs, outputs, branch conditions, and acceptance criteria. Consolidate questions into a single round; do not interrogate incrementally. If blocked by unanswerable unknowns, state explicit assumptions and proceed.
3. **Challenge the solution (Immunize against sycophancy)**:
   - Does this solve the root cause or mask a symptom?
   - Is there already an existing helper, utility, or pattern in the codebase?
   - Is there a simpler, lower-maintenance alternative? Push back respectfully if the user's plan is over-engineered.
4. **Draft the test list**: For non-trivial work, list discrete behavioral slices from simplest happy path to edge cases. Tackle one slice per micro-cycle.

### 1. Write the Failing Test (Red)

- Write the narrowest test capturing the intended behavior or reproducing the bug.
- Run the targeted test command and verify it fails **for the expected reason**.
- **Gate Check**: If the test fails due to syntax error, missing import, or runner crash, fix the harness first. If the test passes immediately, the bug was not reproduced or the test is toothless.
- **UI Boundary Rule**:
  - *UI Behavior & States* (validation, modal visibility, keyboard nav, network states): Apply TDD using user-centric queries (`getByRole`, `findByText`). Never assert internal component state.
  - *Pure Visual Styling* (padding, colors, typography, responsiveness): **Waive unit tests.** Do not assert CSS classes. Instead, take a **Before screenshot** using browser tools.

### 2. Implement the Smallest Change (Green)

- Write only enough production code to make the failing test pass.
- Resist the urge to clean up surrounding code, rename modules, or fix unrelated issues.
- Re-run the narrow test command and verify it passes cleanly.

### 3. Refactor on Green

- Once green, eliminate duplication, improve clarity, and align with codebase conventions.
- Verify test cleanliness: ensure mocks reset, temp files unlink, and state resets cleanly.
- Re-run tests after each refactor step to guarantee behavior remains intact.
- If slices remain on the test list, advance to the next slice (back to **Red**).

### 4. Broader Validation & Outcome

- Run the repository's broader test suite or lint/typecheck command to catch regressions.
- For UI visual changes, capture the **After screenshot** under the identical viewport and present Before/After evidence.
- If environment limits or architecture gaps block a true test, state the blocker explicitly (Best-Effort Mode) rather than faking validation.

---

## Hard Stops

Cease execution and resolve immediately if:

- You are asking generic questions without inspecting relevant repository code first.
- You are implementing an obviously flawed or redundant approach without challenging it.
- You treat a compilation error, bad import, or broken test setup as a valid "Red" test.
- You write brittle unit tests asserting CSS classes or computed styles instead of behavior.
- You modify unrelated code or perform refactoring while the test is still Red or in the Green phase.
- Your tests leave persistent disk files, unreset mocks, or mutated global state.
- You claim tests passed or validation succeeded without executing a real command.

---

## Gotchas

| Symptom | Root Cause | Rule |
| :--- | :--- | :--- |
| Bombarding user with generic questions | Lazy grilling | Inspect codebase first; anchor questions in real code facts |
| Faithfully implementing a flawed design | Sycophancy | Challenge solution framing, architecture fit, and minimal alternatives |
| Test fails on syntax or bad import | Broken harness | Fix test setup first; Red requires an asserted contract mismatch |
| Testing CSS classes (`toHaveClass('px-4')`) | Brittle testing | Waive TDD for pure visual styling; use Before/After screenshot comparison |
| Big monolithic test jump | Oversized increment | Break requirements into a slice-by-slice test list; drive micro-cycles |
| Refactoring while trying to pass test | Tangled concerns | Get to Green with the smallest change first, refactor only on Green |
| Tests fail when run in sequence | State leak / pollution | Ensure idempotent cleanup: reset mocks, wipe temp files, rollback DB |
| Claiming success without run | Fake validation | Execute the narrowest real test command; report failures or limits honestly |

