# Agent 4 - QA Tester Notes

## What Agent 4 Does
Reviews the generated code from Agent 3, identifies bugs,
logic errors, and missing validations. Returns PASS or FAIL.

## Role
Senior QA Engineer and Code Reviewer

## Input
Generated Python code from Agent 3 (reads from output/word_to_pdf.py)

## Output
Structured review report containing:
- STATUS: PASS or FAIL
- ISSUES: List of bugs and problems found
- SUGGESTIONS: List of improvements needed
- SUMMARY: One sentence overall summary

## How It Works
- Reads generated code from output/word_to_pdf.py
- Sends code to Claude (claude-sonnet) via Anthropic API
- Claude responds in the role of a Senior QA Engineer
- Returns status as a dictionary {status, review}

## Key Behavior
- If STATUS = PASS → pipeline moves to human approval
- If STATUS = FAIL → pipeline loops back to Agent 3 to fix issues
- This is the feedback loop that makes the system self-correcting

## Pipeline Position
```
Agent 3 (Code) → Agent 4 (QA Review)
                      |
              PASS ───┴─── FAIL
               ↓               ↓
        Human Approval    Back to Agent 3
```

## File
agents/agent4_qa.py