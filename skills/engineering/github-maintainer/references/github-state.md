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

- In the discussion's language, lead with the conclusion, then give key evidence for the assessed SHA/version, material validation limits, and next action/owner. Use the entrypoint's visible AI identity; describe an independent reviewer as an independent AI assistant. Approved execution links the maintainer's approval when available.
- Keep public comments decision-focused. Put execution traces, agent coordination, fixture debugging, and routine cleanup in supporting records; include them in the comment only when they affect confidence or the next decision. Link accessible scripts, CI runs, or logs when citing validation; a local-only command is not a reproducible evidence link. If evidence cannot be shared, state that limit without exposing private data.
- Record related state changes in one handling summary, using the item's comment, PR description, or private security context. If no suitable interface exists, use the current chat with an object link. Timelines/Git history alone do not replace this record.
- Preserve approval/review evidence; avoid duplicate comments without meaningful changes. Follow-ups report new evidence and its effect on the prior conclusion, linking the earlier review instead of repeating unchanged coverage or approval requests. Edit only your own identifiable comments. Optional markers: `<!-- github-maintainer:status -->` and `<!-- github-maintainer:review HEAD_SHA -->`.
- Write multiline bodies with `--body-file` and API JSON with `--input` to avoid shell expansion.
- Security check links may refer to alerts rather than Actions runs; inspect the corresponding evidence.
