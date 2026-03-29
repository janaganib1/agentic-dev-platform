# Agent 3 - Developer Notes

## What Agent 3 Does
Takes the technical design from Agent 2 and writes 
actual working Python code to implement the solution.

## Role
Senior Python Developer

## Input
Technical design from Agent 2 (stack, file structure, 
functions, implementation plan)

## Output
- Complete working Python code
- Code saved automatically to `output/` folder
- Comments included inside code for clarity

## How It Works
- Reads ANTHROPIC_API_KEY from .env
- Sends technical design to Claude (claude-sonnet) via Anthropic API
- Claude responds in the role of a Senior Developer
- Generated code is saved to output/word_to_pdf.py

## Key Difference from Other Agents
- max_tokens set to 4096 (higher than others)
- This is because code output is much longer than text output
- Saves output to a file, not just prints to screen

## Pipeline Position
```
Agent 2 (Technical Design) → Agent 3 (Code) → Agent 4
```

## Output Location
output/word_to_pdf.py

## File
agents/agent3_developer.py