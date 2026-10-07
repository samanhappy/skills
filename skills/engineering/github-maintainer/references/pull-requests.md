# PR implementation and independent review

Workers follow their assigned phase; the item coordinator owns publication and state transitions.

## Implementation

- For an existing PR, verify source-branch write permission. Otherwise return suggestions or deliver a linked repair draft PR; do not take over the author's branch.
- The implementer returns the root-cause fix and validation. The coordinator checks scope/diff/results, commits and pushes the task branch, and creates a draft PR with linked issues, behavior changes, and validation limits.
- After validating a newly created draft, move it to ready and start independent review unless instructed to keep it draft. Do not promote another author's draft. Attach delivered PRs to the chat when platform tools are available.

## Review and fix loop

1. Review selected non-draft PRs, including workflow-created PRs. Drafts get necessary diagnosis only unless review is requested. Deferred ready PRs retain an explicit reason and are not marked reviewed.
2. Set in-progress and clear resolved waiting-feedback. Assess fixed base/head SHAs, complete diff, linked issues, prior reviews/unresolved threads, and current checks.
3. The independent reviewer returns findings; the coordinator verifies evidence and filters duplicates/resolved findings. Publish a comment, not a formal APPROVE/REQUEST_CHANGES review, with reviewed SHA, concrete findings/locations, validation limits, and next action. If none remain, state “No blocking issues found.”
4. For UI additions/changes, optionally include screenshots when useful to show behavior or findings, with before/after views where appropriate and captured page/state and SHA. Screenshots supplement validation and follow the entrypoint's privacy boundary.
5. Refresh head before publication; reassess changed SHAs and do not repeat the same conclusion for the same SHA. Mark reviewed only after publication.
6. For confirmed actionable findings within scope and branch-write permission, keep in-progress, delegate fixes, validate/push, invalidate reviewed, and request independent review of the new SHA. Repeat until resolved or blocked.
7. For author/permission/dependency blockers, remove in-progress, set waiting-feedback, and record SHA, next owner, and unblock condition. Use needs-owner for required maintainer decisions; resume only with new evidence/guidance.
8. When no actionable findings remain and required validation/checks pass for the current SHA, clear in-progress/waiting-feedback, keep reviewed, and set needs-owner with a concise owner-review request and recommendation. This does not authorize merging. New commits invalidate reviewed and the completed owner-review handoff, clear only its needs-owner state (preserve unrelated decisions), and restart review. Do not requeue closed/merged PRs.
