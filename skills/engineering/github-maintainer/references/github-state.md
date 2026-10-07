# GitHub state and operations

## Evidence freshness

Retrieve each item's discussion, timeline, linked work, and latest maintainer guidance. A repository-wide comment stream or latest comment alone is insufficient. `updatedAt` can reflect bots/labels; truncated output is incomplete evidence.

Before implementation or external writes, refresh open status, SHA/version, and guidance; reassess changed state.

## Workflow labels

Reuse existing equivalents; create fallback labels only when needed. Preserve unrelated and externally managed labels.

| Fallback label | Meaning / exit |
| --- | --- |
| `needs-triage` | Remove after assessment |
| `needs-info` | Reporter information missing; remove when sufficient |
| `ready-for-agent` | Defined implementation scope; remove when work starts |
| `ready-for-human` | Human implementation required, not approval |
| `agent:in-progress` | Active implementation/review this pass; remove on delivery, blocking, or waiting |
| `agent:waiting-feedback` | Author/reviewer/dependency blocker; remove when resolved |
| `agent:needs-owner` | Maintainer decision required; remove after guidance is acted on |
| `agent:reviewed` | Independent review published for a SHA; invalid after head changes |
| `wontfix` | Explicit maintainer rejection only |

Comments record actual state, version, and next owner; labels index it. Reviewed and needs-owner may coexist, but the same action cannot be active and waiting. Check actual work before recovering stale in-progress labels.

## Comments and action records

- In the discussion's language, record the conclusion, necessary evidence, validation limits, and next action/owner. Use the entrypoint's visible AI identity; describe an independent reviewer as an independent AI assistant. Approved execution links the maintainer's approval when available.
- Record related state changes in one handling summary, using the item's comment, PR description, or private security context. If no suitable interface exists, use the current chat with an object link. Timelines/Git history alone do not replace this record.
- Preserve approval/review evidence; avoid duplicate comments without meaningful changes. Edit only your own identifiable comments. Optional markers: `<!-- github-maintainer:status -->` and `<!-- github-maintainer:review HEAD_SHA -->`.
- Write multiline bodies with `--body-file` and API JSON with `--input` to avoid shell expansion.
- Security check links may refer to alerts rather than Actions runs; inspect the corresponding evidence.
