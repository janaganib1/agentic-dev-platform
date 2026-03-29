# Agent 2 - Architect Notes

## What Agent 2 Does
Takes the structured project brief from Agent 1 and produces 
a full technical design for the Developer agent to implement.

## Role
Senior Software Architect

## Input
Project brief from Agent 1 (goal, inputs, outputs, features)

## Output
Full technical design including:
1. Technology stack (libraries and tools)
2. File structure (folders and files to create)
3. Key functions and modules needed
4. Step by step implementation plan
5. Technical risks and considerations

## How It Works
Same pattern as Agent 1:
- Reads ANTHROPIC_API_KEY from .env
- Sends project brief to Claude (claude-sonnet) via Anthropic API
- Claude responds in the role of a Senior Architect
- Returns structured technical design

## Pipeline Position
```
You → Agent 1 (Project Brief) → Agent 2 (Technical Design) → Agent 3
```

## Key Difference from Agent 1
The prompt instructs Claude to act as an Architect, 
not an Orchestrator. The role in the prompt is what 
changes the behavior and output of each agent.

## File
agents/agent2_architect.py