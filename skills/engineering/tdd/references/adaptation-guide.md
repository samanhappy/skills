# Repository Adaptation Guide

Use this guide to adapt the TDD workflow to the current repository instead of assuming a default stack.

## Read in this order

1. `AGENTS.md`, `copilot-instructions.md`, or equivalent project instructions
2. workspace and package manifests such as `pnpm-workspace.yaml`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`
3. test configuration such as `jest.config.*`, `vitest.config.*`, `pytest.ini`, `tox.ini`, `playwright.config.*`
4. CI workflows and reusable test scripts
5. nearby test files covering the same module or feature

## Detect the local test shape

Identify:

- **project structure**: standalone package vs. monorepo/workspace (e.g., pnpm workspaces, Turborepo, Nx, Cargo workspace). In a monorepo, locate the target sub-package manifest rather than defaulting to root commands.
- **test framework and runner**: Jest, Vitest, pytest, unittest, go test, cargo test, JUnit, etc.
- **test file naming pattern**: `*.test.ts`, `*_test.go`, `test_*.py`, etc.
- **test directory layout**: co-located beside code (`src/foo.test.ts`) vs. dedicated directory (`tests/`, `__tests__/`).
- **fixture, mock, and helper patterns**: local test helpers, factory patterns, DB seeders, teardown hooks.
- **focused vs. broad commands**: how to run a single test file or function vs. full test suite.

## Good adaptation questions

- Where do similar tests live?
- In a monorepo, how do you scope test runs to just the affected package (e.g. `pnpm --filter <pkg> test`, `cargo test -p <pkg>`)?
- How are test names phrased in this codebase?
- Are assertions behavioral or implementation-heavy?
- Is there a quick command for one file, one suite, or one package?
- How do existing tests handle cleanup and teardown (DB transactions, temp directories, mock resets)?
- What broader commands are expected before saying the change is done?

## Common command sources

- manifest scripts (`test`, `test:ci`, `lint`, `build`, `check`)
- Makefiles, task runners, or package manager scripts
- CI workflow steps
- contributor docs

## Priority rules

- Prefer repository-specific instructions over generic habits
- Prefer existing local test patterns over personal preference
- Prefer narrow test commands first, broader validation second
- Prefer one trustworthy command over several guessed commands

## Warning signs

Do not assume the repository uses:

- Jest just because it is JavaScript
- pytest just because it is Python
- `pnpm test` just because there is a `package.json`
- co-located tests just because a neighboring repository does that

When in doubt, inspect one real test and mirror it.
