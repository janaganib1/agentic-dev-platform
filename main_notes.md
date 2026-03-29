# main.py - Pipeline Orchestrator Notes

## What main.py Does
Connects all 4 agents together into a single automated pipeline
using LangGraph to manage state, sequencing, and the QA feedback loop.

## Role
Pipeline Orchestrator — the nervous system connecting all agents

## How It Works
1. Takes your plain English requirement as input
2. Passes it through all 4 agents in sequence
3. Manages state between agents
4. Handles QA fail → retry loop (max 3 retries)
5. Stops for human approval before completing

## Pipeline Flow
```
You (Requirement)
        ↓
Agent 1 — Orchestrator (Project Brief)
        ↓
Agent 2 — Architect (Technical Design)
        ↓
Agent 3 — Developer (Generated Code)
        ↓
Agent 4 — QA Tester (Pass / Fail)
        ↓
  PASS ─┤├─ FAIL (back to Agent 3, max 3 retries)
        ↓
Human Approval → Pipeline Complete
```

## Key Components

### AgentState (TypedDict)
Holds all data flowing between agents:
- requirement — your input
- project_brief — Agent 1 output
- technical_design — Agent 2 output
- generated_code — Agent 3 output
- qa_review — Agent 4 review text
- qa_status — PASS or FAIL
- retry_count — tracks how many times Agent 3 was retried
- human_approved — True/False final approval

### LangGraph
- StateGraph manages the pipeline flow
- Nodes = each agent function
- Edges = connections between agents
- Conditional edges = QA pass/fail routing logic

### Retry Logic
- QA FAIL → back to Agent 3 with the review feedback
- Max 3 retries before forcing human approval
- retry_count increments on every Developer node execution

## Known Issue
- human_approval_node has an indentation bug on the if/else block
- Output file path is hardcoded as word_to_pdf.py — needs to be dynamic

## File
main.py (root of project)