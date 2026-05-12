# Prompt Engineering Portfolio

**Author:** Prameela Kottalanka
**Date:** 2026-05-11

---

## Prompt 1 — Framework Gap Analysis

```
You are a senior AI systems architect specializing in agent-driven development frameworks.

## Context
I have a GitHub repository called `nebula-agents` at:
https://github.com/PrameelaKottalanka/nebula-agents

This is a tool-agnostic, orchestrator-agnostic agent-driven development framework.
It defines 11 specialist agents organized into three phases:

**Planning Phase:**
- product-manager — Requirements, stories, acceptance criteria
- architect — Design, data model, API contracts, patterns

**Implementation Phase:**
- backend-developer — Backend APIs, domain logic
- frontend-developer — UI components, forms, client state
- ai-engineer — LLMs, agents, MCP, AI workflows
- quality-engineer — Unit, integration, E2E tests
- devops — Containers, compose, deployment

**Quality & Documentation:**
- code-reviewer — Code quality, standards, patterns
- security — OWASP, auth/authz, vulnerabilities
- technical-writer — API docs, README, runbooks
- blogger — Dev logs, technical articles

Each agent lives under `agents/<role>/SKILL.md` and is composed via action flows
in `agents/actions/*.md`. Prompt templates live in `agents/templates/prompts/`.

## Your Task
Fetch and read the following files from the repository, then perform a deep gap
analysis across all 11 agents:

### Files to read (via web fetch):
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/actions/README.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/CONSUMER-CONTRACT.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/BOUNDARY-POLICY.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/lifecycle-stage.yaml
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/actions/build.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/actions/plan.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/actions/feature.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/actions/review.md
- For each of the 11 agents, fetch:
  https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/<role>/SKILL.md

## Gap Analysis Dimensions

For EACH of the 11 agents, evaluate against ALL of the following dimensions:

### 1. SKILL.md Completeness
- Does the agent have a SKILL.md defined?
- Does it clearly define: role purpose, responsibilities, inputs, outputs,
  constraints, and handoff contracts to other agents?
- Is anything vague, missing, or contradictory?

### 2. Action Flow Coverage
- Which of the 9 actions (init, plan, build, feature, review, validate, test,
  document, blog) does this agent participate in?
- Are there actions where this agent SHOULD be involved but is NOT referenced?
- Are there actions where this agent is referenced but has no corresponding
  SKILL.md guidance for that context?

### 3. Inter-Agent Handoff Gaps
- What does this agent consume from upstream agents?
- What does this agent produce for downstream agents?
- Are there missing handoff contracts — i.e., agent A expects something from
  agent B, but agent B's SKILL.md doesn't define that output?
- Map the full handoff chain and flag every broken link.

### 4. Prompt Template Gaps
- Does each agent have both an automation-safe AND operator-friendly prompt
  template under `agents/templates/prompts/`?
- Are the templates aligned with the agent's SKILL.md responsibilities?
- Are there agents with no templates at all?

### 5. Validation & Gate Coverage
- Which agents have lifecycle gates in `lifecycle-stage.yaml`?
- Which agents produce outputs that are never validated?
- Are there agents whose work cannot be verified because no validator exists?

### 6. Boundary & Genericness Enforcement
- Does each agent correctly stay within the framework boundary
  (no domain-specific logic leaking into framework roles)?
- Are there agents whose SKILL.md references product-specific concerns
  that should live in the product repo instead?

### 7. Role Overlap & Redundancy
- Are there responsibilities duplicated across two or more agents?
- Are there gaps between agents — responsibilities that no agent owns?
- Is the `ai-engineer` agent clearly differentiated from `backend-developer`
  for LLM/MCP scope?
- Is `code-reviewer` scope distinct from `quality-engineer`?

### 8. Conditional Agent Activation
- The `ai-engineer` only runs when stories include AI/LLM/MCP scope.
  Is this condition clearly defined and enforceable?
- Are there other agents that should be conditionally activated but have
  no activation criteria defined?

## Output Format

Return a structured report in this exact format:

---

### SECTION 1: Agent Inventory & Health Scorecard
A table with columns:
| Agent | SKILL.md Exists | Templates Exist | Gate Defined | Actions Covered | Health Score (1-5) |

---

### SECTION 2: Per-Agent Gap Report
For each of the 11 agents, a sub-section with:
- **Gaps Found** (bulleted, specific, with file references)
- **Severity** (Critical / High / Medium / Low)
- **Recommended Fix** (exact file to create/edit and what to add)

---

### SECTION 3: Inter-Agent Handoff Map
A diagram or table showing:
- Which agent hands off to which
- Where handoff contracts are defined
- Where they are MISSING (mark as ⚠️ GAP)

---

### SECTION 4: Cross-Cutting Gaps
Gaps that span multiple agents or the framework as a whole:
- Missing action coverage
- Agents with no validation path
- Role boundary violations
- Activation criteria gaps

---

### SECTION 5: Prioritised Fix Plan
Ordered list of fixes:
1. [CRITICAL] Fix X in agents/<role>/SKILL.md — because it blocks Y
2. [HIGH] Create template for Z — because ...
...

## Constraints
- Cite exact file paths for every gap you identify
- Do not invent gaps — only report what is missing or contradictory based on
  the files you read
- If a file is missing entirely, flag it as MISSING rather than speculating
  about its contents
- Treat the README.md and CONSUMER-CONTRACT.md as the authoritative
  framework intent
- If a fetch fails, note it and continue with what is available
```

---

## Prompt 2 — Fix Recommendation & Implementation

```
You have just completed a detailed gap analysis across all 11 agents in the
nebula-agents framework. I now need your help deciding what to work on next.

## My Background
<my_skills>
I am a C# dotnet/python full stack developer with 14 years experience. I am
comfortable with markdown, basic CI/CD, react, azure and have used LLMs/Coding
assistant before but never built a multi agent framework.
</my_skills>

## My Goal
<my_goal>
I want to make a meaningful contribution to this repo that demonstrates AI
prompting skills and agent design thinking.
</my_goal>

## Task

Using the gap analysis you produced, do the following:

### STEP 1: Rank ALL gaps by fixability
Score every gap you identified on three axes:

| Gap ID | Gap Summary | Effort (1=low, 5=high) | Skill Match (given my background) | Impact (1=low, 5=high) | Fix Score |

Fix Score = (Impact × Skill Match) ÷ Effort
Higher Fix Score = better candidate for me to work on.

### STEP 2: Recommend the SINGLE BEST gap for me to fix
Pick the highest Fix Score gap and explain:
- **What exactly is missing** (cite the file path)
- **Why it matters** to the framework (what breaks without it)
- **Why I can fix it** given my skills
- **What a good fix looks like** — describe the ideal end state

### STEP 3: Give me the exact fix
Produce the complete file content I need to create or edit to close this gap.

Requirements for the fix:
- Must follow the existing conventions in the repo
  (match the tone, structure, and format of existing SKILL.md files or
  templates — do not invent a new format)
- Must stay within the framework boundary — no product-specific or
  domain-specific content
- Must be self-contained — another developer should be able to read it
  with no additional context
- If creating a SKILL.md: include role purpose, responsibilities,
  inputs, outputs, constraints, and handoff contracts
- If creating a prompt template: provide both the automation-safe variant
  (structured, machine-readable) and the operator-friendly variant
  (natural language, human-readable)

### STEP 4: Tell me how to validate my fix
Give me:
1. The exact command(s) to run to verify my fix passes framework gates
2. A checklist I can self-review against before submitting
3. What a reviewer would look for when assessing my contribution

### STEP 5: Suggest the next 2 gaps to fix after this one
Ordered by Fix Score, with a one-line rationale for each.

## Output Format

Return sections clearly labelled STEP 1 through STEP 5.
For STEP 3, wrap the file content in a code block with the exact
target file path as the label.
For STEP 4, use a numbered checklist.
```
