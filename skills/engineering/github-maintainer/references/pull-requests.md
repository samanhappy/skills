# PR implementation and independent review

Before creating, fixing, or reviewing a PR, all participating roles read [SKILL.md](../SKILL.md) and this file. The item coordinator also reads [github-state.md](github-state.md) before investigation or external operations. Implementation and review workers follow their assigned phase and return results to the item coordinator.

## PR evidence

Inspect draft status, base/head SHAs, commits, complete diff, reviews, unresolved threads, and checks for the current SHA, together with the linked items and latest maintainer guidance.

## Implementation

- Delegate implementation for every new PR to a subagent. Supply the issue, confirmed scope, guides, acceptance criteria, and authorization boundaries. Follow the isolation and delegation rules in [SKILL.md](../SKILL.md). The item coordinator integrates and validates.
- Before fixing an existing PR, verify its source branch and write permissions. Without permission, provide suggestions or create a clearly linked repair draft PR; do not force-push or take over the author's work.
- The implementer delivers the smallest root-cause fix and appropriate validation, or returns evidence and decision points when uncertain. The coordinator checks the actual diff, scope, and validation before committing, pushing a task branch, and creating a draft PR with linked issues, behavior changes, and validation limits.
- After validating a newly created draft PR, move it to ready with `gh pr ready` without requesting maintainer approval, then immediately start independent subagent review. Honor an explicit instruction to keep it draft; do not automatically promote another author's draft PR.
- Attach created PRs to the current chat using platform tools when available.

## Ready for review

- Every non-draft PR selected for review requires an independent reviewing subagent, including all PRs created by this workflow. Report ready PRs deferred this pass with the reason; do not label them reviewed. Apply in-progress when review starts and remove waiting-feedback once its blocker is resolved. Remove needs-owner when new commits invalidate a completed owner-review handoff; preserve unrelated pending owner decisions. Limit draft PR work to necessary diagnosis unless the maintainer explicitly requests review.
- Fix the base/head SHAs and supply linked issues, complete diff, prior feedback, project conventions, and necessary context. Evaluate correctness, regressions, authorization/data boundaries, and validation evidence; do not invent findings to fill a quota.
- The subagent returns findings. The coordinator verifies evidence, locations, and severity, filters duplicate or resolved findings, then publishes using `gh pr comment --body-file`. This workflow requests comments; do not automatically submit formal APPROVE or REQUEST_CHANGES reviews.
- Include the reviewed SHA, key findings, validation limits, and next action. Findings need concrete triggers, impact, and file locations. If none remain, say “No blocking issues found,” without claiming absolute safety.
- When changes add or modify UI, consider including screenshots in the review comment when they help demonstrate the resulting behavior or a finding; use before/after views when useful. Identify the captured page/state and reviewed SHA, and keep sensitive data within the appropriate private context. Screenshots are optional and do not replace validation.
- Refresh head before publication. If it changed, update the review rather than marking stale results as current. Do not repeat the same conclusion for the same SHA. For new commits, verify old findings and review the changes and their impact.
- Apply reviewed after publication. When confirmed actionable findings remain and branch writes are authorized, keep in-progress and delegate fixes to an implementing subagent. The coordinator validates and pushes the fixes, removes reviewed because the head changed, and automatically requests independent subagent review of the new SHA. Repeat until no confirmed actionable findings remain.
- When fixes require author input, missing permissions, or an external dependency, remove in-progress, apply waiting-feedback, and record the findings, current SHA, next owner, and exact unblock condition in a comment. For uncertain scope or significant decisions, apply needs-owner with a concrete proposal. Resume from labels, comments, and current repository state on a later invocation; do not poll or repeat a stalled fix without new evidence.
- Once independent review finds no remaining actionable issues and required validation/checks pass for the current SHA, remove in-progress and waiting-feedback, keep reviewed, and apply needs-owner. Publish a concise owner-review request with the SHA, validation evidence/limits, and recommended next action. Passing agent review does not authorize merging. New commits invalidate this handoff and restart review. Do not requeue closed or merged PRs.
