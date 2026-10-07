# Issues and waiting

- Confirm the defect and existing fixes. Missing reporter evidence gets one focused request and needs-info; maintainer requirements/decisions get needs-owner.
- Separate the defect from a proposed redesign. Deliver an independent repair within established behavior when possible; gate only the broader decision and record what remains open. Before implementation, read [pull-requests.md](pull-requests.md).
- Link the delivered PR with validation. Close only after the fix lands or explicit maintainer direction; closing keywords must reflect an established closure decision. Waiting never justifies closure or wontfix.
- Measure waiting from the latest unanswered concrete request or substantive discussion, excluding bots, unrelated comments, and label changes. Consider one reminder after **14 calendar days**, then needs-owner after another 14 days without a reply. Check reminder history; honor maintainer timing/keep-waiting instructions. Urgent security/release blockers may be raised immediately in the appropriate context.
