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

Comments record actual state and version; labels index it. Clarify the next action or owner only when not already clear from context. Reviewed and needs-owner may coexist, but the same action cannot be active and waiting. Check actual work before recovering stale in-progress labels.

## Comments and action records

- Default to a short, scannable comment in the discussion's language: one-line conclusion with AI identity and short SHA, then brief bullets for actionable findings. Each finding states trigger, impact, and requested repair with a code link; avoid dense paragraphs and a separate next-action/owner line when already clear. Keep blocking risks and decisions visible; put supporting validation/coverage in links or a `<details>` section, retaining material limits beside the claims they qualify. Mention independent AI review once when applicable and link relevant approval.
- Omit routine execution, coordination, cleanup, permission fields, and label bookkeeping from public prose; retain them in supporting records. Explain blockers through their consequence, clarifying the action or owner only if ambiguous. Link accessible validation scripts, CI runs, or logs; local commands alone are not reproducible evidence. State unavailable evidence without exposing private data.
- Record related state changes in one handling summary, using the item's comment, PR description, or private security context. If no suitable interface exists, use the current chat with an object link. Timelines/Git history alone do not replace this record.
- Preserve approval/review evidence; avoid duplicate comments without meaningful changes. Follow-ups report new evidence and its effect on the prior conclusion, linking the earlier review instead of repeating unchanged coverage or approval requests. Edit only your own identifiable comments. Optional markers: `<!-- github-maintainer:status -->` and `<!-- github-maintainer:review HEAD_SHA -->`.
- Write multiline bodies with `--body-file` and API JSON with `--input` to avoid shell expansion.
- Security check links may refer to alerts rather than Actions runs; inspect the corresponding evidence.
