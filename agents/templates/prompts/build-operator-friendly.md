Before starting, resolve `{PRODUCT_ROOT}` per `agents/docs/AGENT-USE.md` → Session Setup and echo its absolute path on your first turn; every command below assumes that resolution.

Run `agents/actions/build.md` for `{FEATURE_IDS}` with `AI_SCOPE={true | false}` and `RUN_ID={uuid4 generated at session start}`. Set `AI_SCOPE=true` if any story mentions LLM, AI, or machine-learning behavior; requires MCP server/tool/resource work; involves prompts, agent behavior, or tool orchestration; changes files under `{PRODUCT_ROOT}/{AI_LAYER}/`; or requires model selection, cost controls, or guardrails.

Start only when the plan action is already signed off for all `{FEATURE_IDS}`, `{PRODUCT_ROOT}/planning-mds/architecture/SOLUTION-PATTERNS.md` exists, `{PRODUCT_ROOT}/planning-mds/features/TRACKER-GOVERNANCE.md` exists (seed from `agents/templates/tracker-governance-template.md` if missing), application runtime containers are reachable and healthy, user stories have clear testable acceptance criteria, and the user is available for approval gates.

Load context in this order and navigate instead of eager-loading:
1. `agents/architect/SKILL.md` (Step 0 — orchestration kickoff)
2. `{PRODUCT_ROOT}/planning-mds/BLUEPRINT.md`
3. `{PRODUCT_ROOT}/planning-mds/features/` (feature folders and colocated stories for `{FEATURE_IDS}`)
4. `{PRODUCT_ROOT}/planning-mds/architecture/SOLUTION-PATTERNS.md`
5. `{PRODUCT_ROOT}/planning-mds/api/` (contracts for parallel implementation agents)
6. `agents/backend-developer/SKILL.md` (Step 1a)
7. `agents/frontend-developer/SKILL.md` (Step 1b)
8. `agents/quality-engineer/SKILL.md` (Step 1c)
9. `agents/devops/SKILL.md` (Step 1d)
10. `agents/ai-engineer/SKILL.md` (Step 1e — only when `AI_SCOPE=true`)
11. `agents/code-reviewer/SKILL.md` (Step 3)
12. `agents/security/SKILL.md` (Step 5)
13. `agents/product-manager/SKILL.md` (Step 6.9 — explicit role switch required)

Open these only when the current step links them or drift repair requires them: `{PRODUCT_ROOT}/planning-mds/architecture/deployment-architecture.md`, `{PRODUCT_ROOT}/planning-mds/security/` (threat model if present), `agents/devops/references/containerization-guide.md` (Step 1d Phase 2/3), `agents/frontend-developer/references/ux-audit-ruleset.md` (Step 1b, Step 3), and `{PRODUCT_ROOT}/planning-mds/knowledge-graph/*.yaml` when KG drift repair is required.

Keep ownership strict:
- `architect owns` application-assembly-plan.md, ADRs, API contracts, schemas, and authorization artifacts
- `product-manager owns` STATUS.md closeout, trackers, archive moves, and feature-mappings.yaml path/status updates
- `other roles` implement their runtime layers; flag drift; do not redefine canonical shared semantics

All stack-specific compile, test, and security commands must run inside application runtime containers. Record every evidence path (test results, lint output, SAST reports, dependency scans) under `{PRODUCT_ROOT}/planning-mds/operations/evidence/**`. Review gate decisions must reference evidence from application runtime executions, not narrative summaries.

Step 0 produces `{PRODUCT_ROOT}/planning-mds/architecture/application-assembly-plan.md` (use `agents/templates/application-assembly-plan-template.md`). Step 1 parallel outputs per agent per feature are: domain entities, migrations, API endpoints, unit/integration tests, and STATUS.md updates (backend); components, forms, hooks, routing config, component tests, UX audit evidence, and STATUS.md updates (frontend); test plan, cross-tier integration/E2E tests, quality-gate reports, and STATUS.md updates (quality-engineer); deployment-architecture.md, docker-compose.yml, Dockerfiles, .env.example, deployment scripts, and STATUS.md updates (devops); and `{PRODUCT_ROOT}/{AI_LAYER}/` implementation, AI tests, MCP definitions if needed, and STATUS.md updates (ai-engineer, `AI_SCOPE=true` only).

Follow these gates exactly:
- `G0    ASSEMBLY PLAN VALIDATION` — assembly plan exists; scope split and agent handoffs are explicit
- `G1    SELF-REVIEW` — each agent validates their own work; all tests pass in runtime containers
- `G2    CODE REVIEW APPROVAL` — critical=0; high requires explicit mitigation token before proceeding
- `G3    SECURITY REVIEW APPROVAL` — critical=0; high requires explicit mitigation token before proceeding
- `G3.75 SIGNOFF` — every Required=Yes role: verdict=PASS, reviewer identity, review date, evidence path under `{PRODUCT_ROOT}/planning-mds/operations/evidence/**`
- `G3.9  PM CLOSEOUT` — MUST switch role: read `agents/product-manager/SKILL.md` before executing closeout checklist
- `G3.95 TRACKER SYNC` — `validate-trackers.py` exit 0

Don't proceed past any approval gate without an explicit user decision token. Don't run G3.9 PM CLOSEOUT without first reading `agents/product-manager/SKILL.md`. Don't mark any feature Done or Archived before G3.75 SIGNOFF passes for all required roles. Don't treat lookup/KG mappings as authoritative over raw artifacts. Don't run stack-specific commands outside application runtime containers. Don't invent or widen implementation scope beyond what the story acceptance criteria require. Don't record evidence paths in the signoff ledger that point into `agents/**` rather than solution artifacts.

Stop immediately if application runtime containers fail to start and cannot be restored, if a critical code or security finding persists after one full review cycle, if required signoff is missing reviewer identity, date, or evidence path, if scope drifts outside the declared `{FEATURE_IDS}`, or if `validate-trackers.py` exits non-zero and cannot be auto-repaired within scope.

Close the run by executing these in order:
- `Applicable backend/frontend/test commands for changed surfaces (inside runtime containers; evidence paths recorded)`
- `python3 agents/product-manager/scripts/validate-trackers.py`
- `python3 agents/product-manager/scripts/generate-story-index.py {PRODUCT_ROOT}/planning-mds/features/   (if stories changed)`
- `python3 {PRODUCT_ROOT}/scripts/kg/validate.py --regenerate-symbols --check-symbols   (if source files in bound paths changed)`
- `python3 {PRODUCT_ROOT}/scripts/kg/validate.py --check-drift`
- `python3 agents/scripts/validate_templates.py`

Resolve conflicts like this:
- `application-assembly-plan.md vs story text → assembly plan wins; log reconciliation in STATUS.md`
- `code vs SOLUTION-PATTERNS.md → patterns win; deviation requires explicit justification recorded in STATUS.md`
- `raw artifact vs KG mapping → raw wins; repair KG in same change set`
- `shared-semantics change detected → halt and route to Architect; do not silently redefine`
