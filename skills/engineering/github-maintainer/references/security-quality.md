# Security and quality

- Cover accessible advisories, Dependabot, code scanning, secret scanning, and CI/checks; report inaccessible categories individually.
- Verify affected versions/branches, reachability, and existing fixes. Preserve quality gates; diagnose failures rather than weakening expectations.
- Route ordinary dependency/quality work through existing or minimal actionable issues: read [issues.md](issues.md), then [pull-requests.md](pull-requests.md) for repair implementation/review.
- GHSA fixes use the advisory's private fork/PR. Verify visibility/remotes before creating a worktree or pushing; no public fallback on permission failure. The entrypoint's approval gates apply even if repository policy permits direct default-branch fixes.
- If GHSA labels/comments are unavailable, record state on the private repair PR or provide the GHSA link and private decision summary in chat. Do not force the issue workflow, repeatedly retry, or switch to web messaging.
