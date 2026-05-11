Before starting, resolve `{PRODUCT_ROOT}` per `agents/docs/AGENT-USE.md` → Session Setup and echo its absolute path on your first turn; every command below assumes that resolution.

Run `agents/actions/review.md` for `SCOPE={feature | PR | full-codebase}` with `AI_SCOPE={true | false}` and `RUN_ID={uuid4 generated at session start}`. Set `AI_SCOPE=true` when `{PRODUCT_ROOT}/{AI_LAYER}/` is in scope.

Start only when implementation is complete for the declared scope, tests are written and passing in application runtime containers, code is committed to version control, and `{PRODUCT_ROOT}/planning-mds/architecture/SOLUTION-PATTERNS.md` exists.

Load context in this order and navigate instead of eager-loading:
1. `agents/code-reviewer/SKILL.md` (Step 1a — parallel)
2. `agents/security/SKILL.md` (Step 1b — parallel)
3. Source code: backend and frontend (both agents); `{PRODUCT_ROOT}/{AI_LAYER}/` when `AI_SCOPE=true`
4. Test suites and application runtime validation outputs (test, lint, SAST, dependency scan reports)
5. `{PRODUCT_ROOT}/planning-mds/BLUEPRINT.md`
6. `{PRODUCT_ROOT}/planning-mds/architecture/SOLUTION-PATTERNS.md`
7. User stories with acceptance criteria for the declared scope
8. `agents/frontend-developer/references/ux-audit-ruleset.md` (Step 1a — when UI code changed)
9. `{PRODUCT_ROOT}/planning-mds/security/` (Step 1b — threat model if present)

Run Step 1 with both agents in parallel. The code reviewer checks SOLID principles, clean architecture boundaries, test coverage, acceptance criteria mapping, naming conventions, error handling, SOLUTION-PATTERNS.md compliance, and UX rule-set compliance when UI code changed. The security reviewer runs the full OWASP Top 10 scan, authorization review, secrets management check, audit logging validation, and dependency vulnerability assessment. The security report must be saved under `{PRODUCT_ROOT}/planning-mds/security/reviews/security-review-{date}.md`.

After both reviews complete (G1), compute combined severity counts across both reports and present the approval gate (G2). Gate state is determined as follows: if required runtime evidence is missing, status is BLOCKED — offer generate-evidence or reject, not approve. If combined critical count is greater than zero, status is BLOCKED — offer fix-critical or reject, not approve. If combined high count is greater than zero, status is WARNING — offer fix-all-high, approve-with-justification, or reject. If combined critical and high are both zero, status is ACCEPTABLE — offer approve, fix-issues-anyway, or reject.

When the user selects fix-critical or fix-all-high, developers resolve the identified issues and the action returns to Step 1 for a full re-review. When the user selects approve-with-justification, capture the explicit mitigation justification for each remaining high issue before proceeding. Log all user decisions with rationale.

Don't proceed past G2 without an explicit user decision token. Don't approve when combined critical issues are greater than zero. Don't use narrative summaries in place of runtime-generated evidence. Don't omit evidence paths from application runtime containers in review reports. Don't invent findings without referencing specific file:line locations.

Stop immediately if a critical finding persists after one full review cycle, if required runtime evidence cannot be generated from application runtime containers, or if scope drifts outside the declared scope.

Close the run by executing these in order:
- `Confirm security report saved under {PRODUCT_ROOT}/planning-mds/security/reviews/`
- `python3 agents/scripts/validate_templates.py`

Resolve conflicts like this:
- `code vs SOLUTION-PATTERNS.md → patterns win; deviation requires justification recorded in the review report`
- `combined critical > 0 → approval blocked regardless of individual review verdicts`
- `runtime evidence vs narrative summary → runtime evidence wins; missing evidence blocks approval`
