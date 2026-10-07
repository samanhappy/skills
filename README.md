# Saman's Skills

[![skills.sh](https://skills.sh/b/samanhappy/skills)](https://skills.sh/samanhappy/skills)

Personal agent skills I use to build real software with discipline, feedback loops, and a healthy respect for tests.

I’m [Saman](https://github.com/samanhappy) — a software engineer based in Nanjing, China, with 15+ years of experience building backend systems, AI infrastructure, and developer tools. I build in public at [samanhappy.com](https://samanhappy.com/) and care a lot about craftsmanship over cargo-cult speed.

This repository is where I collect the skills I actually want my coding agents to use. The goal is simple: keep them practical, composable, and grounded in real engineering work.

Current skills:

- **[github-maintainer](./skills/engineering/github-maintainer/SKILL.md)** — Advance GitHub issues, PRs, security, and quality asynchronously with gh, subagents, and maintainer approval gates.
- **[verified-dev](./skills/engineering/verified-dev/SKILL.md)** — Disciplined, verification-driven development with a Red → Green → Refactor loop and visual proof.
- **[optimize-prompt](./skills/engineering/optimize-prompt/SKILL.md)** — Diagnose and optimize agent prompts via decision-chain analysis and invariant fixes.
- **[clip-subtitle-video](./skills/media/clip-subtitle-video/SKILL.md)** — Clip videos and burn bilingual subtitles into MP4 deliverables.
- **[clean-paper-scan](./skills/documents/clean-paper-scan/SKILL.md)** — Turn phone photos of paper documents into clean printable A4 PDFs: erase handwriting, remove shadows and show-through, straighten curled pages, clear edge grime.
- **[write-blog](./skills/writing/write-blog/SKILL.md)** — Write deep-analysis technical blog posts in Chinese.
- **[translate-blog](./skills/writing/translate-blog/SKILL.md)** — Translate English technical blog posts to Chinese with glossary-driven terminology consistency.

## Quickstart

1. Install from `skills.sh`:

```bash
npx skills@latest add samanhappy/skills
```

2. Choose the skills you want to install.

3. Start with [`/verified-dev`](./skills/engineering/verified-dev/SKILL.md) when you want a change driven by tests first.

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

- **[github-maintainer](./skills/engineering/github-maintainer/SKILL.md)** — Advance GitHub issues, PRs, security, and quality asynchronously with gh, subagents, and maintainer approval gates.
- **[verified-dev](./skills/engineering/verified-dev/SKILL.md)** — Disciplined, verification-driven development with a red-green-refactor loop and visual proof.
- **[optimize-prompt](./skills/engineering/optimize-prompt/SKILL.md)** — Diagnose and optimize agent prompts via decision-chain analysis and invariant fixes.

### Media

- **[clip-subtitle-video](./skills/media/clip-subtitle-video/SKILL.md)** — Clip videos and burn bilingual subtitles into MP4 deliverables.

### Documents

- **[clean-paper-scan](./skills/documents/clean-paper-scan/SKILL.md)** — Turn phone photos of paper documents into clean printable A4 PDFs: perspective correction, lighting normalization, handwriting erasure, de-warping, edge-grime cleanup, and verified page order.

### Writing

- **[write-blog](./skills/writing/write-blog/SKILL.md)** — Write deep-analysis blog posts in Chinese.
- **[translate-blog](./skills/writing/translate-blog/SKILL.md)** — Translate English technical blog posts to Chinese with glossary-driven terminology consistency.

## License

[MIT](./LICENSE)
