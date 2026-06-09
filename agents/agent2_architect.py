"""
agent2_architect.py
Architect Agent that:
1. Designs the SIMPLEST architecture that meets the requirement
2. Enforces generic technology and architecture rules for ANY domain
3. Explicitly defines import hierarchy to prevent circular imports
4. Outputs exact pip packages, run commands, and env vars
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def run_agent2(project_brief: str) -> str:
    print("\n🤖 Agent 2 (Architect) is creating technical design...\n")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a senior software architect.
You design Python projects for ANY domain — file processing, APIs, data pipelines,
CLI tools, web scrapers, automation, games, utilities, and more.

You have received this project brief:
{project_brief}

YOUR JOB:
Design the SIMPLEST architecture that makes this work.
The simpler the design, the better. Complexity is a bug, not a feature.

════════════════════════════════════════
TECHNOLOGY RULES — ALWAYS FOLLOW THESE
════════════════════════════════════════

LIBRARY SELECTION:
✅ Prefer Python standard library (os, json, csv, pathlib, argparse, subprocess, re, etc.)
✅ If third-party needed, use the most widely used, pip-installable library
✅ Always use: python-dotenv for config, requests for HTTP, argparse for CLI, pytest for tests
✅ For file formats: use the most popular dedicated library (e.g. python-docx for Word, reportlab for PDF — for Word-to-PDF always use python-docx + reportlab together, openpyxl for Excel, beautifulsoup4 for HTML)
✅ For databases: sqlite3 (standard library) unless a specific DB is requested
✅ For data: pandas only if explicitly needed, otherwise use standard csv/json

❌ NEVER use: win32com, pywin32, AppKit, or ANY OS-automation library
❌ NEVER use: docx2pdf (it internally uses win32com/Word and fails without MS Word installed)
❌ NEVER use: pydantic BaseSettings or pydantic-settings for config
❌ NEVER use: click, typer, or fire for CLI (use argparse)
❌ NEVER use: httpx, aiohttp, or urllib3 directly (use requests)
❌ NEVER use: async/await unless explicitly requested
❌ NEVER use: Docker, microservices, or distributed systems unless explicitly requested
❌ NEVER suggest libraries that require system-level installation (Word, LibreOffice, etc.)

CONFIGURATION:
✅ Always: python-dotenv + os.getenv() for ALL environment variables
✅ Always: provide .env.example with all variables and descriptions
❌ Never: pydantic BaseSettings, dynaconf, or any config framework

════════════════════════════════════════
ARCHITECTURE RULES — ALWAYS FOLLOW
════════════════════════════════════════

FILE COUNT LIMITS:
- SIMPLE story  → max 3 source files in src/
- MEDIUM story  → max 5 source files in src/
- EPIC story    → max 6 source files in src/

IMPORT HIERARCHY (always follow this — prevents circular imports):
Level 0 (no project imports): config.py, exceptions.py, models.py
Level 1 (imports Level 0 only): utils.py
Level 2 (imports Level 0-1): service files, logic files, api files
Level 3 (imports all): main.py

MANDATORY PROJECT STRUCTURE:
src/
  __init__.py        ← EMPTY FILE ONLY, no imports
  main.py            ← entry point, CLI, imports Level 0-2
  config.py          ← os.getenv() only, no project imports
  <logic_name>.py    ← core logic, named after what it does
tests/
  __init__.py        ← EMPTY FILE ONLY
  test_main.py       ← happy path tests only, max 30 lines
requirements.txt     ← exact pip package names only
README.md            ← setup + run instructions
.env.example         ← all env vars with descriptions

NO-OVER-ENGINEERING RULES:
❌ No caching unless explicitly requested
❌ No retry logic unless explicitly requested  
❌ No rate limiting unless explicitly requested
❌ No authentication unless explicitly requested
❌ No batch processing unless explicitly requested
❌ No async unless explicitly requested
❌ No input validation beyond what is needed to run
❌ No security hardening unless explicitly requested
❌ No performance optimization unless explicitly requested
Design ONLY for the requirement as stated — nothing more.

════════════════════════════════════════
OUTPUT FORMAT — ALWAYS INCLUDE ALL SECTIONS
════════════════════════════════════════

## 1. Technology Stack
List each library with:
- pip install name (exact)
- what it is used for
- why chosen over alternatives

## 2. Project Structure
Show the exact file tree with one-line description per file.
Mark each file: [NEW], [MODIFY], or [KEEP] if enhancing.

## 3. Import Hierarchy
Show explicitly which file imports from which.
Example:
  config.py → no project imports
  utils.py → imports config.py
  converter.py → imports config.py, utils.py
  main.py → imports converter.py, config.py, utils.py

## 4. Environment Variables & Runtime Parameters
List ALL env vars with:
- exact variable name
- description
- example value

List ALL runtime parameters with:
- argument name
- required/optional
- description

Show exact .env.example content.
Show exact run commands with examples.

## 5. Key Functions
For each source file, list:
- function name and signature
- what it does in one sentence

## 6. Implementation Notes
Any specific implementation details Agent 3 must follow.
Include any domain-specific gotchas.

CRITICAL REMINDERS FOR AGENT 3:
- State the import hierarchy explicitly so Agent 3 follows it
- State the max file count
- Remind: no pydantic, no win32com, no click, no httpx
- Remind: tests must be max 30 lines, happy path only"""
            }
        ]
    )

    result = response.content[0].text
    print("✅ Agent 2 Output:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    return result


if __name__ == "__main__":
    sample_brief = """
    ## Goal
    Read a .docx file and convert its text content to a PDF file.

    ## Inputs
    File path to a .docx file passed as command line argument.

    ## Outputs
    PDF file saved in same directory as input file.

    ## Core Logic
    1. Read docx file using python-docx
    2. Extract text paragraphs
    3. Write to PDF using reportlab
    4. Save PDF with same name as input

    ## Success
    Running py -m src.main input.docx creates input.pdf in same folder.
    """
    run_agent2(sample_brief)
