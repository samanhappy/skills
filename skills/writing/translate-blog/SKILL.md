---
name: translate-blog
description: 'Translate English technical blog posts to Chinese. Triggers: 翻译, translate, 翻译一下, 翻一下, translate this. Use when the user wants to translate a technical article (EN → ZH) with a natural, developer-friendly voice.'
argument-hint: '[file path or URL to translate]'
---

# Translate Blog

Translate English technical blog posts into idiomatic, developer-friendly Chinese. Single-pass workflow: analyze → translate → review → highlight → summarize.

## Input

| Type | Action |
|------|--------|
| Local `.md` file | Read directly |
| URL | Fetch with `scrapling`, save as `{slug}.md` to target directory, then translate |

### URL Fetching

Use `scrapling` to extract clean markdown from URLs. Apply progressive fallback:

**Level 1 — Lightweight** (static pages, no bot protection):

```bash
scrapling extract get '<url>' <output-path> --ai-targeted --timeout 30
```

**Level 2 — Heavy** (JS-rendered, Cloudflare-protected):

```bash
scrapling extract stealthy-fetch '<url>' <output-path> \
  --real-chrome --no-headless \
  --solve-cloudflare \
  --network-idle --wait 5000 \
  --timeout 90000 \
  --ai-targeted
```

**Level 3 — Manual fallback**: If both fail, ask the user to copy-paste the article content into the conversation.

- `{slug}`: 2-4 word kebab-case from the article title (e.g. `building-a-react-hook`)
- `--ai-targeted`: optimizes extracted content for AI consumption (removes nav, ads, sidebars)
- `--real-chrome --no-headless`: uses a visible Chrome instance to bypass bot detection
- `--network-idle --wait 5000`: waits for JS to finish rendering before extraction

### URL Content Cleanup

Scraped content often includes non-article noise. Before translating, strip the following from the saved markdown file:

- **Navigation**: site headers, breadcrumbs, sidebars, menus
- **Footer clutter**: copyright notices, "related posts", "read next", newsletter signup forms, comment sections
- **Sharing links**: "Share on Twitter/LinkedIn", "Discuss on Hacker News", etc.
- **Author bio boxes**: author blurbs, "written by" cards at the bottom

Keep only the **article body**: title, publication date, article text, code blocks, and embedded images. The result should read as a clean, standalone article.

**Format repair**: scraped content often has formatting issues — broken paragraphs, missing line breaks between sections, orphaned list items, inconsistent heading levels, stray punctuation, or garbled whitespace. Fix these during cleanup so the source is well-structured before translation begins.

## Output

### Directory Selection

Determine the output directory by inspecting the current project structure:

1. If directories like `posts/`, `articles/`, `content/`, `blog/` exist, save source and translation there.
2. Otherwise, save to the current working directory.

Do not ask the user — infer from the project layout.

### File Naming

Translation saved as `{basename}-zh.md` in the target directory.

Example: `posts/react-hooks.md` → `posts/react-hooks-zh.md`

If the output file already exists, rename existing to `{basename}-zh.backup-{timestamp}.md`.

## Workflow

### Step 1: Analyze

Read the source and identify:

**Content type** — classify the article and set translation strategy:

| Type | Strategy |
|------|----------|
| Tutorial / How-to | Precision > Fluency. Instructions must be unambiguous |
| Opinion piece | Preserve author's voice and stance, even if controversial |
| Research paper explainer | Highest terminology precision, add translator notes for obscure concepts |
| Documentation | Strict heading/code correspondence, structural fidelity |
| Blog / Narrative | Fluency > Precision. Allow liberal adaptation for natural flow |

**Terminology**: technical terms, proper nouns, acronyms, framework/library names. Cross-reference with `~/.claude/skills/translate-blog/glossary.md`. For terms not in the glossary, determine standard Chinese translations.

**Multi-meaning terms**: for glossary entries with multiple translation options (e.g. `Grounding → 基础化/落地`), examine the article context and **lock in one translation** for the entire article. Record the choice to maintain consistency.

**Tone**: formal or conversational? Humor, metaphors, cultural references?

**Challenges**: passages that need creative adaptation (figurative language, long sentences, culturally-specific references).

### Step 2: Translate

Apply the following principles:

**Style**: adapt precision/fluency balance based on content type identified in Step 1. Technical terms must be accurate and consistent across the full text. For narrative passages (intros, analogies, conclusions), rewrite into natural Chinese as if a native writer composed it — break long English sentences into shorter idiomatic ones, interpret metaphors by intended meaning not word-for-word.

**Audience**: Chinese-speaking developers/engineers. Assume familiarity with common technical terms — no annotation needed for words like API, container, framework, runtime.

**Translator notes**: only add concise explanations `（**译注**：...）` for genuinely niche or ambiguous terms the audience may not know (obscure startup names, inside jokes, rarely-used acronyms). Keep annotations minimal.

**Code blocks**: translate comments to Chinese. Leave variable names, function names, class names, and string literals in English.

**Frontmatter**: translate `title` and `description` fields to Chinese. Keep all other fields (tags, date, author, slug, etc.) as-is. Tags stay in English for search compatibility.

**Images**: preserve all image references as-is. Do not check or warn about image text language.

**Markdown formatting**: preserve all headings, links, lists, tables, and formatting exactly.

### Step 3: Review Pass

Re-read the full translation against the source. Check for:

1. **Terminology consistency** — every glossary term translated identically across all paragraphs. Multi-meaning terms use the translation locked in Step 1.
2. **Natural Chinese** — no translationese (翻译腔). Flag and rewrite any sentence that reads as a word-for-word translation.
3. **Completeness** — no skipped paragraphs, sentences, or list items.
4. **Markdown integrity** — all headings, links, lists, tables, code blocks, and formatting preserved correctly.

Fix issues in-place before proceeding. Track the number and nature of fixes for the summary.

### Step 4: Highlight Key Sentences

Identify sentences in the translated text that match these criteria:

- The article's central thesis or core argument (usually in intro or conclusion)
- Counter-intuitive or surprising claims that challenge common assumptions
- Original analogies or metaphors coined by the author
- Highly quotable summary statements that capture a key insight

**Count**: ~1 per 500 source words. Minimum 2, maximum 8.

Wrap selected sentences in **bold** (`**...**`) inline. A golden sentence is usually a standalone statement. Exclude: transitional sentences, purely descriptive sentences, example-illustration sentences.

### Step 5: Summary

After translation completes, display:

```
**Translation complete**

Source: {source-path} ({word-count} words)
Output: {output-path}
Content type: {type}

Translation stats:
  Glossary terms applied: {count} ({new-count} new terms added)
  Golden sentences highlighted: {count}
  Translator notes added: {count}

Review notes:
  - {issues found and fixed during review, e.g. "3 sentences rewritten for natural flow"}
```

If no issues were found during review, display "No issues found."

## Glossary

Terminology mappings are maintained locally at `~/.claude/skills/translate-blog/glossary.md`.

**Initialization**: On first use, if the file does not exist, copy the seed glossary from `references/glossary.md` (relative to this skill) to the local path.

**Updates**: When new terms are encountered during translation, append them to the local glossary immediately. Do not wait for user confirmation.

Format: `| English | Chinese | Notes |` markdown table.
