# Saman's Skills

[![skills.sh](https://skills.sh/b/samanhappy/skills)](https://skills.sh/samanhappy/skills)

Personal agent skills I use to build real software with discipline, feedback loops, and a healthy respect for tests.

I’m [Saman](https://github.com/samanhappy) — a software engineer based in Nanjing, China, with 15+ years of experience building backend systems, AI infrastructure, and developer tools. I build in public at [samanhappy.com](https://samanhappy.com/) and care a lot about craftsmanship over cargo-cult speed.

This repository is where I collect the skills I actually want my coding agents to use. The goal is simple: keep them practical, composable, and grounded in real engineering work.

Right now this repo starts with one skill:

- **[tdd](./skills/engineering/tdd/SKILL.md)** — Test-driven development with a Red → Green → Refactor loop. Useful for bug fixes, features, regression tests, and safe refactors.

More skills will land here over time.

## Quickstart

1. Install from `skills.sh`:

```bash
npx skills@latest add samanhappy/skills
```

2. Choose the skills you want to install.

3. Start with [`/tdd`](./skills/engineering/tdd/SKILL.md) when you want a change driven by tests first.

## Why this repo exists

AI can write code quickly. That does **not** automatically mean it writes good code.

I use skills like these to push agents toward better engineering habits:

- clarify the behavior before changing code
- prefer feedback loops over guesswork
- write the smallest change that proves value
- keep quality high while still shipping fast

That philosophy matches how I work elsewhere too:

- building [MCPHub](https://github.com/samanhappy/mcphub), a popular open-source MCP orchestration platform
- practicing AI Coding + TDD daily
- writing about engineering decisions and AI-native workflows at [samanhappy.com](https://samanhappy.com/)

## Reference

### Engineering

- **[tdd](./skills/engineering/tdd/SKILL.md)** — Test-driven development with a red-green-refactor loop. Builds features or fixes bugs one small vertical slice at a time.

## License

[MIT](./LICENSE)
