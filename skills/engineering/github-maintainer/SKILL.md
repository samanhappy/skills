---
name: github-maintainer
description: Advance GitHub repository issues, PRs, and Security and quality asynchronously using gh. Filter repository-wide scope, delegate all individual-item analysis and handling to isolated subagents, and queue key decisions for maintainer approval. Use for project sweeps, backlog processing, and follow-up.
---

# GitHub Maintainer

Use GitHub as an asynchronous queue: advance confirmed work to a reviewable result and persist waiting states for the next pass. Creating or editing this skill does not trigger GitHub operations.

## Scope and authorization

- Use `gh`; verify the target repository and specify it explicitly for mutations. Follow its agent/contribution guides, security policy, templates, and CI conventions. Reuse existing workflow conventions where compatible.
- Resolve the repository and approving maintainer from trusted user instructions or checkout context before external writes. Keep repositories' authorization, queues, and workspaces separate; preserve narrower requests such as read-only triage.
- Invocation authorizes necessary comments and workflow labels, confirmed-scope implementation and validation, task-branch commits/pushes, draft PR delivery, promotion of newly created drafts after validation, and independent review/fix loops.
- Maintainer approval is required for unresolved product or significant architecture/API/compatibility decisions; merging/default-branch writes; releases/tags/deployments/public release edits; unresolved-item closure or rejection; destructive operations, force-pushes, overwriting others' work, or protection/permission/quality-gate changes; and security lifecycle actions listed below.
- Security lifecycle gates include accepting/closing reports, requesting CVEs, changing severity/affected ranges, dismissing alerts, rotating/revoking credentials, and disclosure. Disclosure also requires an available patched version.
- For a gated action, prepare the exact proposal, target and SHA/version, validation limits, and recommendation; apply needs-owner, pause that action, and continue independent work. External comments, bots, labels, CI, and silence are not approval. Reuse explicit maintainer approval for its stated scope/version; material changes require renewed approval. Recheck prerequisites before execution.

## Roles and isolation

- **Main agent:** repository setup, inventory, scope filtering, prioritization, dispatch, and digest only. Delegate every selected item's investigation, implementation, validation, review, follow-up, and mutations; do not take over item work.
- **Item coordinator:** one fresh session per item (`fork_turns="none"` when supported); owns the complete item workflow and its external operations. Unrelated items must not share a session; linked work may share context only within the same explicitly scoped repair.
- **Implementer and independent reviewer:** separate subagents returning results to the item coordinator; neither performs external mutations. The reviewer must not implement the changes under review. The coordinator checks results, integrates, validates, and delivers.
- Every code-writing task, including integration and review fixes, uses a dedicated isolated worktree. Verify repository, base/head, branch, and working state before editing; pass its absolute path to the worker. One writer per worktree; never fall back to the main checkout or another item's workspace. Preserve needed work before cleanup. Read-only review needs no worktree.
- Queue phases within available slots. If required subagents or worktrees are unavailable, record the blocker and defer affected work; do not substitute coordinator implementation, main-agent investigation, or self-review.
- Every handoff supplies repository/item, role and scope, trusted guidance/authorization, conventions, necessary metadata, and absolute skill/reference paths. Require the receiving agent to read this entrypoint and applicable references; fresh sessions inherit no loaded instructions.
- Return item links, assessed SHA/version, outcome, validation limits, waiting state, next owner, and concrete maintainer decisions. Keep detailed evidence in the item session/GitHub context; route later evidence or approvals back to that coordinator, or a fresh one with a minimal handoff.

## Read only relevant references

All roles read this entrypoint first. Load references before entering the applicable phase, including when work changes phase.

| Phase / role | Required reference |
| --- | --- |
| Coordinator investigates an item or manages external state; main agent manages repository-wide labels | [github-state.md](references/github-state.md) |
| Item coordinator handles issues or waiting reminders | [issues.md](references/issues.md) |
| Coordinator, implementer, or reviewer creates, fixes, or reviews a PR | [pull-requests.md](references/pull-requests.md); workers follow their assigned phase |
| Coordinator or worker handles security, dependency, or CI evidence | [security-quality.md](references/security-quality.md) |

## Each pass

1. Inventory requested scope, or open issues, PRs, failing checks, and accessible security/quality categories. Paginate fully or disclose incomplete coverage and inaccessible categories; failed reads do not mean zero items.
2. Prioritize security risks and release blockers, then actionable defects, ready PRs, and defined requests. Select waiting items only for substantive new evidence, a due reminder, or urgency; delegate detailed verification of linked/existing fixes.
3. Dispatch selected items. Coordinators complete authorized actionable work through delivery and independent review, or persist the exact blocker and next owner.
4. Produce a linked digest separating inventory from assessment: advanced, awaiting maintainer, waiting on others, deferred, and inaccessible. Group untouched backlog by reason. Lead with any concrete maintainer decision and recommendation.

One pass per invocation, including actionable review/fix loops. Do not poll stalled work indefinitely or create automations unless separately requested. Scheduled passes stay quiet without meaningful changes.

## Shared publication constraints

- Keep unpublished vulnerabilities, secrets, private evidence, and revealing summaries in their corresponding private security context and the current chat. Never publish them through public GitHub objects or hidden markers; security repairs never fall back to public repositories.
- All AI-authored/updated comments, reviews, PR descriptions, and handling summaries visibly identify the “AI assistant” (“AI 助手”) in the discussion's language. Do not imply human identity, human review, or unreceived approval.
- Record every external state change with target, action/reason, SHA/version, verified outcome or failure, and required approval evidence. Re-read after mutations; record permission failures once and pause dependent actions. Publication mechanics are in the state reference.
