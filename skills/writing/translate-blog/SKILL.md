---
name: translate-blog
description: 'Translate English technical blog posts to Chinese. Triggers: 翻译, translate, 翻译一下, 翻一下, translate this. Use when the user wants to translate a technical article (EN → ZH) with a natural, developer-friendly voice.'
argument-hint: '[file path or URL to translate]'
---

# Translate Blog

Translate English technical blog posts into idiomatic, developer-friendly Chinese. Single-pass workflow: analyze → translate → highlight.

## Input

| Type | Action |
|------|--------|
| Local `.md` file | Read directly |
| URL | Fetch with `scrapling`, save as `translate/{slug}.md`, then translate |

### URL Fetching

Use `scrapling` to extract clean markdown from URLs (handles JS-rendered pages, Cloudflare, and other anti-bot protections):

```bash
scrapling extract stealthy-fetch \
  '<url>' \
  translate/{slug}.md \
  --real-chrome \
  --no-headless \
  --solve-cloudflare \
  --network-idle \
  --wait 5000 \
  --timeout 90000 \
  --ai-targeted
```

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

Translation saved as `{basename}-zh.md` next to the source file.

Example: `posts/react-hooks.md` → `posts/react-hooks-zh.md`

If the output file already exists, rename existing to `{basename}-zh.backup-{timestamp}.md`.

## Workflow

### Step 1: Analyze

Read the source and identify:

- **Terminology**: technical terms, proper nouns, acronyms, framework/library names. Cross-reference with [references/glossary.md](references/glossary.md). For terms not in the glossary, determine standard Chinese translations.
- **Tone**: formal or conversational? Humor, metaphors, cultural references?
- **Challenges**: passages that need creative adaptation (figurative language, long sentences, culturally-specific references).

### Step 2: Translate

Apply the following principles:

**Style**: technical precision first, storytelling flow second. Terminology must be accurate and consistent. For narrative passages (intros, analogies, conclusions), rewrite into natural Chinese as if a native writer composed it — break long English sentences into shorter idiomatic ones, interpret metaphors by intended meaning not word-for-word.

**Audience**: Chinese-speaking developers/engineers. Assume familiarity with common technical terms — no annotation needed for words like API, container, framework, runtime.

**Translator notes**: only add concise explanations `（**解释**）` for genuinely niche or ambiguous terms the audience may not know (obscure startup names, inside jokes, rarely-used acronyms). Keep annotations minimal.

**Code blocks**: leave completely untouched. Do not translate comments, variable names, or strings inside code blocks.

**Frontmatter**: translate `title` and `description` fields to Chinese. Keep all other fields (tags, date, author, slug, etc.) as-is. Tags stay in English for search compatibility.

**Images**: preserve all image references as-is. Do not check or warn about image text language.

**Markdown formatting**: preserve all headings, links, lists, tables, and formatting exactly.

### Step 3: Highlight Key Sentences

After translation, identify 3-8 sentences in the translated text that are:

- Core arguments or key insights
- Well-crafted phrases that capture the author's main point
- Memorable "golden lines" worth the reader's attention

Wrap these sentences in **bold** (`**...**`) inline in the final translation. A golden sentence is usually a standalone statement, not a transitional or descriptive sentence. Choose sparingly — if everything is bold, nothing stands out.

## Glossary

Terminology mappings are maintained in [references/glossary.md](references/glossary.md). Read it during the analysis step. Add new terms as you encounter them — the glossary is a living document.

Format: `| English | Chinese | Notes |` markdown table.

## Summary

After translation completes, display:

```
**Translation complete**

Source: {source-path}
Output: {output-path}
Golden sentences highlighted: {count}
Glossary terms applied: {count}
```