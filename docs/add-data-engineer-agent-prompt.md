You are a senior AI systems architect who deeply understands multi-agent 
development frameworks.

## Context
I am adding a new agent called `data-engineer` to the nebula-agents framework 
at https://github.com/PrameelaKottalanka/nebula-agents

This framework is tool-agnostic and orchestrator-agnostic. It currently has 
11 agents organised into three phases:

**Planning Phase:** product-manager, architect  
**Implementation Phase:** backend-developer, frontend-developer, ai-engineer, 
quality-engineer, devops  
**Quality & Documentation:** code-reviewer, security, technical-writer, blogger

## Step 1 — Read These Files First
Before generating anything, fetch and read these files to understand existing 
conventions EXACTLY — match their tone, structure, heading style, and depth:

- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/README.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/CONSUMER-CONTRACT.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/BOUNDARY-POLICY.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/lifecycle-stage.yaml
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/actions/build.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/actions/plan.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/actions/feature.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/actions/review.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/backend-developer/SKILL.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/ai-engineer/SKILL.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/architect/SKILL.md
- https://raw.githubusercontent.com/PrameelaKottalanka/nebula-agents/main/agents/templates/prompts/backend-developer.md

## Step 2 — Understand the data-engineer Role
The `data-engineer` agent is responsible for everything related to data 
infrastructure, pipelines, and data contracts within a project. Specifically:

**Core Responsibilities:**
- Designing and implementing data pipelines (ETL/ELT)
- Defining data models, schemas, and database migrations
- Establishing data contracts between services and consumers
- Setting up data warehouses, lakes, and marts
- Implementing data quality checks and validation rules
- Managing data versioning, lineage, and observability
- Writing seed data, fixture data, and test data factories
- Defining event schemas for event-driven data flows
- Collaborating with architect on data model decisions
- Collaborating with backend-developer on ORM models and query optimisation
- Collaborating with ai-engineer on training data pipelines and feature stores
- Collaborating with quality-engineer on data quality test coverage
- Collaborating with devops on pipeline orchestration and scheduling

**Activation Criteria:**
This agent activates when a story involves any of:
- Database schema changes or new migrations
- Data pipeline creation or modification
- Reporting, analytics, or BI requirements
- Event sourcing or CQRS data patterns
- AI/ML training data preparation
- Data contract definitions between services
- Bulk data imports or exports

**Does NOT own:**
- Application business logic (backend-developer owns this)
- Infrastructure provisioning (devops owns this)
- AI model training or inference (ai-engineer owns this)
- UI data display (frontend-developer owns this)

## Step 3 — Generate All Four Deliverables

### DELIVERABLE 1: agents/data-engineer/SKILL.md
Create a complete SKILL.md file that includes:
- Role purpose (2-3 sentences, generic, framework-level — no product specifics)
- Phase placement (which phase does this agent belong to?)
- Activation criteria (when does this agent run vs. sit out?)
- Responsibilities (bulleted, clear ownership statements)
- Inputs (what does this agent consume, from which agents)
- Outputs (what does this agent produce, for which agents)
- Handoff contracts (explicit: "I hand X to Y in format Z")
- Constraints and boundary rules (what this agent must never do)
- Quality standards (what good output from this agent looks like)
- Tools and technologies (generic categories, not product-specific)

### DELIVERABLE 2: agents/templates/prompts/data-engineer.md
Create TWO prompt variants inside this file:

**Variant A — Automation-Safe Prompt**
Structured, machine-readable, designed to be injected into an orchestrator 
or CI/CD pipeline with zero human editing. Must include:
- Structured input block (story, context, upstream outputs)
- Explicit output schema (what to produce, in what format)
- Validation rules Claude must self-check before responding
- Boundary guard (a rule that stops the agent doing backend or devops work)

**Variant B — Operator-Friendly Prompt**
Natural language, human-readable, designed for a developer to paste into 
Claude manually. Must include:
- A plain English role introduction
- What to read before starting
- What to produce
- How to handle ambiguity
- When to stop and ask vs. proceed

### DELIVERABLE 3: Action Flow Updates
For each of the following action files, specify EXACTLY what line(s) to add 
to include data-engineer participation:

- agents/actions/plan.md — when does data-engineer join planning?
- agents/actions/build.md — what does data-engineer do during build?
- agents/actions/feature.md — what is data-engineer's role in feature work?
- agents/actions/review.md — what does data-engineer review?

For each action file, provide:
- The exact text to insert
- Where to insert it (after which existing line or section)
- Why this agent participates at this point in the flow

### DELIVERABLE 4: lifecycle-stage.yaml Update
Provide the exact YAML block to add to lifecycle-stage.yaml for the 
data-engineer agent, including:
- Stage name and phase
- Entry conditions (what must be true before this agent runs)
- Exit conditions (what must be true before handoff)
- Validation gates (what outputs are checked and how)
- Failure behaviour (what happens if a gate fails)

Match the exact YAML structure and indentation style of the existing file.

## Output Format

Return all four deliverables in this exact structure:

---
## DELIVERABLE 1
📁 `agents/data-engineer/SKILL.md`
[full file content in a code block]

---
## DELIVERABLE 2
📁 `agents/templates/prompts/data-engineer.md`
[full file content in a code block]

---
## DELIVERABLE 3
📁 Action Flow Updates
For each action file, a sub-section with:
- File: `agents/actions/<name>.md`
- Insert after: [exact line reference]
- Content: [exact text to add in a code block]
- Reason: [one sentence explanation]

---
## DELIVERABLE 4
📁 `lifecycle-stage.yaml` update
[exact YAML block to add, in a code block]

---
## DELIVERABLE 5: Integration Summary
A table showing:
| Agent | Receives from data-engineer | Sends to data-engineer |
For all 11 existing agents — mark "None" where no relationship exists.

## Hard Constraints
- Every file must match the existing repo's conventions exactly — 
  do not invent new formats, headings, or structures
- No product-specific or domain-specific content anywhere — 
  this is a generic framework agent
- Every handoff must be bidirectional — if data-engineer sends to 
  backend-developer, backend-developer's expected inputs must be referenced
- If any fetched file is unavailable, note it and infer conventions 
  from the files that ARE available
- Do not output explanations between deliverables — 
  only the structured content blocks
