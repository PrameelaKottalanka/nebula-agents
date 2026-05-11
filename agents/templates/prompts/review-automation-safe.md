ACTION: agents/actions/review.md

SESSION_SETUP:
- Resolve {PRODUCT_ROOT} per agents/docs/AGENT-USE.md → Session Setup
- Echo the resolved absolute {PRODUCT_ROOT} path on the first turn before any shell command
- All paths and commands below assume that resolution

PARAMETERS:
  SCOPE:     {feature | PR | full-codebase}   # what is being reviewed
  AI_SCOPE:  {true | false}                   # true when {PRODUCT_ROOT}/{AI_LAYER}/ is in scope
  RUN_ID:    {uuid4 generated at session start}

PRECONDITIONS:
- Implementation completed for declared SCOPE
- Tests written and passing in application runtime containers
- Code committed to version control
- {PRODUCT_ROOT}/planning-mds/architecture/SOLUTION-PATTERNS.md exists

CONTEXT LOADING ORDER (navigate; do not eager-load):
1. agents/code-reviewer/SKILL.md                                     (Step 1a — parallel)
2. agents/security/SKILL.md                                          (Step 1b — parallel)
3. Source code: backend, frontend                                     (both agents)
4. {PRODUCT_ROOT}/{AI_LAYER}/                                        (AI_SCOPE=true only)
5. Test suites and application runtime validation outputs             (test, lint, SAST, dependency scan reports)
6. {PRODUCT_ROOT}/planning-mds/BLUEPRINT.md
7. {PRODUCT_ROOT}/planning-mds/architecture/SOLUTION-PATTERNS.md
8. User stories with acceptance criteria for declared SCOPE
9. agents/frontend-developer/references/ux-audit-ruleset.md          (Step 1a — when UI code changed)
10. {PRODUCT_ROOT}/planning-mds/security/                            (Step 1b — threat model if present)

OUTPUTS:
- Code quality review report                                                                    (Step 1a)
- Security review report → {PRODUCT_ROOT}/planning-mds/security/reviews/security-review-{date}.md   (Step 1b)

GATES (sequential, all mandatory):
G1    PARALLEL REVIEWS — both code-reviewer and security reviews completed; reports generated with severity counts
G2    APPROVAL — combined critical=0 before approve is enabled; high requires explicit mitigation justification; user decision logged with rationale

GATE STATE LOGIC:
- required_runtime_evidence_missing → STATUS: BLOCKED; OPTIONS: generate evidence/reject; approve disabled
- combined_critical > 0             → STATUS: BLOCKED; OPTIONS: fix critical/reject; approve disabled
- combined_high > 0                 → STATUS: WARNING; OPTIONS: fix all high/approve with justification/reject
- combined_critical = 0 AND combined_high = 0 → STATUS: ACCEPTABLE; OPTIONS: approve/fix issues anyway/reject

FORBIDDEN:
- Proceeding past G2 without an explicit user decision token
- Approving when combined critical issues > 0
- Using narrative summaries in place of runtime-generated evidence
- Omitting evidence paths from application runtime containers in review reports
- Inventing findings without referencing specific file:line locations

STOP CONDITIONS:
- Critical finding persists after one full review cycle
- Required runtime evidence cannot be generated from application runtime containers
- Scope drifts outside declared SCOPE

EXIT VALIDATION (run in order; all exit 0):
- Security report saved under {PRODUCT_ROOT}/planning-mds/security/reviews/
- python3 agents/scripts/validate_templates.py

CONFLICT RESOLUTION:
- code vs SOLUTION-PATTERNS.md → patterns win; deviation requires justification recorded in review report
- combined critical > 0 → approval blocked regardless of individual review verdicts
- runtime evidence vs narrative summary → runtime evidence wins; missing evidence blocks approval
