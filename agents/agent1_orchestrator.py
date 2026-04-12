"""
agent1_orchestrator.py
Orchestrator Agent that:
1. Receives a story requirement (one functional layer)
2. Produces a clear, minimal project brief
3. Works for ANY domain or requirement type
4. Never adds scope beyond what the story says
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def run_agent1(requirement: str, memory_context: dict = None) -> str:
    print("\n🤖 Agent 1 (Orchestrator) is analyzing the requirement...\n")

    # Build memory section
    memory_section = ""
    if memory_context and memory_context.get("mode") != "fresh":
        mode = memory_context["mode"]
        tech_stack = memory_context.get("tech_stack", [])
        existing_files = memory_context.get("existing_files", {})
        context_summary = memory_context.get("context_summary", "")

        memory_section = f"""
MEMORY CONTEXT — {mode.upper()} MODE:
{context_summary}

Existing tech stack to REUSE: {', '.join(tech_stack) if tech_stack else 'detect from existing code'}
Existing files: {', '.join(list(existing_files.keys())[:10]) if existing_files else 'none'}

IMPORTANT:
- Do NOT redesign from scratch
- Identify ONLY what needs to be added or changed for this story
- Reuse existing tech stack
- Reference existing files where relevant
"""
    else:
        memory_section = "\nMEMORY CONTEXT: No past work found — starting fresh.\n"

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": f"""You are a software project orchestrator.
You handle ANY kind of software requirement — CLI tools, APIs, file processors,
web scrapers, data pipelines, utilities, games, automation scripts, and more.

The current story requirement is:
"{requirement}"

{memory_section}

YOUR JOB:
Produce a clear, minimal project brief. Keep scope STRICTLY limited to
what the story says. Do not add features, validations, or enhancements
that are not explicitly mentioned.

OUTPUT FORMAT:
## Goal
One sentence — what this story builds.

## Inputs
What goes in (files, arguments, API calls, user input, etc.)

## Outputs  
What comes out (files, printed output, API response, return value, etc.)

## Core Logic
What the code must do — step by step, implementation-focused.
Maximum 5 steps. No extras.

## Success
One sentence — how to verify it works.

## Tech Stack Hint
Suggest the simplest possible libraries for this requirement.
Prefer standard library. If third-party needed, name the pip package.
NEVER suggest: win32com, pywin32, pydantic BaseSettings, click, httpx.
For config: always python-dotenv + os.getenv().
For HTTP: always requests.
For CLI: always argparse.

RULES:
- Scope is ONLY what the story says — nothing more
- If story says "no validation" — do not include validation
- If story says "simple" — keep it simple
- Do not add logging, retry logic, caching, or auth unless asked
- Do not redesign what already exists — only add what is new"""
            }
        ]
    )

    result = response.content[0].text
    print("✅ Agent 1 Output:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    return result


if __name__ == "__main__":
    requirement = input("\nEnter your requirement: ")
    run_agent1(requirement)