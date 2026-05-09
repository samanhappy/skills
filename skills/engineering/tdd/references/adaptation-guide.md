# Repository Adaptation Guide

Use this guide to adapt the TDD workflow to the current repository instead of assuming a default stack.

## Read in this order

1. `AGENTS.md`, `copilot-instructions.md`, or equivalent project instructions
2. package manifests such as `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`
3. test configuration such as `jest.config.*`, `vitest.config.*`, `pytest.ini`, `tox.ini`, `playwright.config.*`
4. CI workflows and reusable test scripts
5. nearby test files covering the same module or feature

## Detect the local test shape

Identify:

- test framework and runner
- test file naming pattern
- preferred test directory or co-located style
- fixture, mock, and helper patterns
- focused test commands and full validation commands

## Good adaptation questions

- Where do similar tests live?
- How are test names phrased in this codebase?
- Are assertions behavioral or implementation-heavy?
- Is there a quick command for one file, one suite, or one package?
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
