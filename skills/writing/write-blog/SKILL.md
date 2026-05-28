---
name: write-blog
description: 'Write a deep-analysis blog post in Chinese. Triggers: 写一篇文章, 写篇博客, write a blog post, write an article about, 帮我写一篇, 来一篇关于. Use when the user wants to create a structured, insight-driven blog post about a technical topic.'
argument-hint: 'Describe the topic to write about (e.g., "mattpocock/skills 的设计理念").'
---

# Write Blog

Use this skill when the user wants to write a deep-analysis blog post in Chinese.

This skill follows a **grill-then-write** workflow: ask clarifying questions first, then produce the draft.

## Step 1: Clarifying Questions

Ask the following 3 questions **one at a time**, providing a recommended answer for each:

1. **Target audience** — How familiar is the reader with the topic? What background can be assumed?
2. **Core thesis** — What is the single key insight the reader should walk away with?
3. **Key focus areas** — Which 3-4 points deserve deep analysis? Which can be mentioned briefly?

## Step 2: Write the Draft

After all 3 questions are answered, write the full article following these rules:

### Tone

Conversational, with personal perspective. Write like an experienced developer sharing insights with peers — not a textbook, not a product manual. Occasional bold judgments are welcome, but the overall tone is sharing, not lecturing.

### Structure

Follow this flow:

1. **Pain point hook** — Start with a relatable problem the reader recognizes
2. **Core analysis** — Deep dive into 3-4 key points, each with clear "why" and "what we can learn"
3. **Design insights** — Analyze the reasoning behind decisions, not just what was done
4. **Takeaway patterns** — Concrete, reusable patterns the reader can apply immediately
5. **Getting started** — Lower the barrier to action, tell the reader how to begin

### Technical Details

Keep code commands, tool names, and project names in English (e.g., `/grill-me`, `Claude Code`). Describe their function in Chinese within the analysis.

### Audience Assumption

Target readers are developers already using AI coding tools (Claude Code, Cursor, etc.). Assume familiarity with basic concepts. Focus on methodology and mindset, not installation guides.

### Content Strategy

Deep analysis over feature listing. Readers want "cognitive upgrade", not "user manual". Every technical point should answer "why" and "what can we learn", not just "what" and "how to use".

## Step 3: Review and Save

Output the full article for user review. After the user confirms (or provides feedback and revisions), ask where to save the file. Do not assume a default location — the user decides.
