# TDD Anti-Patterns

Use this file when the task starts to look like TDD on paper but not in practice.

## Pseudo-TDD patterns to avoid

### 0. Obedient implementation of bad solutions

The user proposes a solution, and the agent faithfully implements it under the TDD cycle — tests first, green, refactor — without ever questioning whether the solution itself is reasonable. The result: well-tested code that solves the wrong problem, fights the architecture, duplicates existing functionality, or is needlessly complex.

This is the most dangerous TDD anti-pattern because it *looks* like good practice. The cycle runs cleanly. The tests pass. But the solution is worse than doing nothing — it adds code the team now has to maintain or undo.

**Fix:** grill the proposed solution. Phase 1: nail down every fuzzy detail until the problem fits in one unambiguous sentence. Phase 2: challenge the approach — is this the simplest thing? Does it work with the architecture? Is there already a way to do this? If the answer points to a different approach, propose it. TDD without this step is just well-documented obedience.

### -1. Implementing ambiguity

The user says "add caching," "fix the login bug," or "make it faster," and the agent starts writing tests and code — filling in the gaps with guesses. The tests pass, but the implementation doesn't match what the user actually needed, because the user never said what they actually needed.

Vague input is not a task. It's an invitation to grill. Every unasked question is a future revert.

**Fix:** before any code, grill until all branch conditions, scope boundaries, inputs/outputs, error states, and acceptance criteria are nailed down. The answer to "what exactly do we need to do?" must fit in one unambiguous sentence. If the user can't answer, that's the real problem — not the code.

### 1. Implementation-first disguised as TDD

The code is changed first and the test is added afterward as paperwork.

**Fix:** revert mentally to the behavioral gap, write the failing test, and only then continue.

### 2. Testing internals instead of behavior

The test locks in private helpers, exact call counts, or fragile structure instead of user-visible outcomes.

**Fix:** move the assertion up to the observable contract whenever possible.

### 3. Oversized first increment

The first test requires many files, complex fixtures, and a large design decision before any behavior is proven.

**Fix:** shrink to the smallest observable slice that still matters.

### 4. Refactor mixed into Green

The change that makes the test pass also renames modules, rearranges architecture, or rewrites nearby code.

**Fix:** get to green first, then refactor in separate, test-backed cleanup steps.

### 5. Fake validation

The agent says tests passed or the change is safe without running a real command.

**Fix:** run a real command and report it accurately. If no command exists, say so plainly.

### 6. Best-effort mode as a convenience excuse

Strict TDD is skipped because writing the test feels slower.

**Fix:** best-effort mode is only for real blockers such as environment limits, missing seams, or broken test infrastructure.

## Acceptable exceptions

A strict failing test may be blocked when:

- required infrastructure is unavailable
- reproducing the bug needs an external dependency that cannot be simulated locally
- the repository's current test setup is broken
- creating the seam is a larger approved design task outside the current change

Even then:

- explain the blocker explicitly
- add the closest useful test possible
- keep the code change narrow and reversible
- describe the missing ideal test for follow-up
