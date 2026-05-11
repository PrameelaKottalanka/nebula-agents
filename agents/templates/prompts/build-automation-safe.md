ACTION: agents/actions/build.md

SESSION_SETUP:
- Resolve {PRODUCT_ROOT} per agents/docs/AGENT-USE.md → Session Setup
- Echo the resolved absolute {PRODUCT_ROOT} path on the first turn before any shell command
- All paths and commands below assume that resolution

PARAMETERS:
  FEATURE_IDS:    [{F####}, {F####}]    # one or more features in build scope
  AI_SCOPE:       {true | false}         # true when any story meets the AI scope checklist
  RUN_ID:         {uuid4 generated at session start}

AI SCOPE CHECKLIST — set AI_SCOPE=true if ANY apply:
  - Story mentions LLM, AI, or machine learning behavior
  - Story requires MCP server/tool/resource work
  - Story involves prompts, agent behavior, or tool orchestration
  - Story changes files under {PRODUCT_ROOT}/{AI_LAYER}/
  - Story requires model selection, cost controls, or guardrails

PRECONDITIONS:
- Plan action signed off for all {FEATURE_IDS}
- {PRODUCT_ROOT}/planning-mds/architecture/SOLUTION-PATTERNS.md exists
- {PRODUCT_ROOT}/planning-mds/features/TRACKER-GOVERNANCE.md exists (seed from agents/templates/tracker-governance-template.md if missing)
- Application runtime containers reachable and healthy
- User stories have clear, testable acceptance criteria for all {FEATURE_IDS}
- User is available for approval gates

CONTEXT LOADING ORDER (navigate; do not eager-load):
1. agents/architect/SKILL.md                                  (Step 0 — orchestration kickoff)
2. {PRODUCT_ROOT}/planning-mds/BLUEPRINT.md
3. {PRODUCT_ROOT}/planning-mds/features/                      (feature folders and colocated stories for {FEATURE_IDS})
4. {PRODUCT_ROOT}/planning-mds/architecture/SOLUTION-PATTERNS.md
5. {PRODUCT_ROOT}/planning-mds/api/                           (contracts for parallel implementation agents)
6. agents/backend-developer/SKILL.md                          (Step 1a)
7. agents/frontend-developer/SKILL.md                         (Step 1b)
8. agents/quality-engineer/SKILL.md                           (Step 1c)
9. agents/devops/SKILL.md                                     (Step 1d)
10. agents/ai-engineer/SKILL.md                               (Step 1e — only when AI_SCOPE=true)
11. agents/code-reviewer/SKILL.md                             (Step 3)
12. agents/security/SKILL.md                                  (Step 5)
13. agents/product-manager/SKILL.md                           (Step 6.9 — explicit role switch required)

ON-DEMAND (open only when linked by the current step or required for drift repair):
- {PRODUCT_ROOT}/planning-mds/architecture/deployment-architecture.md
- {PRODUCT_ROOT}/planning-mds/security/                       (threat model if present)
- agents/devops/references/containerization-guide.md          (Step 1d Phase 2/3)
- agents/frontend-developer/references/ux-audit-ruleset.md    (Step 1b, Step 3)
- {PRODUCT_ROOT}/planning-mds/knowledge-graph/*.yaml          (when KG drift repair is required)

OWNERSHIP:
- architect owns: application-assembly-plan.md, ADRs, API contracts, schemas, authorization artifacts
- product-manager owns: STATUS.md closeout, trackers, archive moves, feature-mappings.yaml path/status updates
- other roles: implement their runtime layers; flag drift; do not redefine canonical shared semantics

RUNTIME BOUNDARY:
- Stack-specific compile/test/security commands must run inside application runtime containers
- Evidence paths (test results, lint output, SAST reports, dependency scans) must be recorded under {PRODUCT_ROOT}/planning-mds/operations/evidence/**
- Review gate decisions must reference evidence from application runtime executions, not narrative summaries

STEP 0 OUTPUT:
- {PRODUCT_ROOT}/planning-mds/architecture/application-assembly-plan.md   (use agents/templates/application-assembly-plan-template.md)

STEP 1 PARALLEL OUTPUTS (per agent, per feature):
- backend-developer:  domain entities, migrations, API endpoints, unit/integration tests, STATUS.md updates
- frontend-developer: components, forms, hooks, routing config, component tests, UX audit evidence, STATUS.md updates
- quality-engineer:   test plan, cross-tier integration/E2E tests, quality-gate reports, STATUS.md updates
- devops:             deployment-architecture.md, docker-compose.yml, Dockerfiles, .env.example, deployment scripts, STATUS.md updates
- ai-engineer:        {PRODUCT_ROOT}/{AI_LAYER}/ implementation, AI tests, MCP definitions if needed, STATUS.md updates   (AI_SCOPE=true only)

GATES (sequential, all mandatory):
G0    ASSEMBLY PLAN VALIDATION — assembly plan exists; scope split and agent handoffs are explicit
G1    SELF-REVIEW — each agent validates their own work; all tests pass in runtime containers
G2    CODE REVIEW APPROVAL — critical=0; high requires explicit mitigation token before proceeding
G3    SECURITY REVIEW APPROVAL — critical=0; high requires explicit mitigation token before proceeding
G3.75 SIGNOFF — every Required=Yes role: verdict=PASS, reviewer identity, review date, evidence path under {PRODUCT_ROOT}/planning-mds/operations/evidence/**
G3.9  PM CLOSEOUT — MUST switch role: read agents/product-manager/SKILL.md before executing closeout checklist
G3.95 TRACKER SYNC — validate-trackers.py exit 0

FORBIDDEN:
- Proceeding past any approval gate without an explicit user decision token
- Running G3.9 PM CLOSEOUT without first reading agents/product-manager/SKILL.md (explicit role switch)
- Marking any feature Done or Archived before G3.75 SIGNOFF passes for all required roles
- Treating lookup/KG mappings as authoritative over raw artifacts
- Running stack-specific commands outside application runtime containers
- Inventing or widening implementation scope beyond what the story acceptance criteria require
- Evidence paths in signoff ledger that point into agents/** rather than solution artifacts

STOP CONDITIONS:
- Application runtime containers fail to start and cannot be restored
- A critical code or security finding persists after one full review cycle
- Required signoff is missing reviewer identity, date, or evidence path
- Scope drifts outside the declared {FEATURE_IDS}
- validate-trackers.py exits non-zero and cannot be auto-repaired within scope

EXIT VALIDATION (run in order; all exit 0):
- Applicable backend/frontend/test commands for changed surfaces (inside runtime containers; evidence paths recorded)
- python3 agents/product-manager/scripts/validate-trackers.py
- python3 agents/product-manager/scripts/generate-story-index.py {PRODUCT_ROOT}/planning-mds/features/   (if stories changed)
- python3 {PRODUCT_ROOT}/scripts/kg/validate.py --regenerate-symbols --check-symbols   (if source files in bound paths changed)
- python3 {PRODUCT_ROOT}/scripts/kg/validate.py --check-drift
- python3 agents/scripts/validate_templates.py

CONFLICT RESOLUTION:
- application-assembly-plan.md vs story text → assembly plan wins; log reconciliation in STATUS.md
- code vs SOLUTION-PATTERNS.md → patterns win; deviation requires explicit justification recorded in STATUS.md
- raw artifact vs KG mapping → raw wins; repair KG in same change set
- shared-semantics change detected → halt and route to Architect; do not silently redefine
