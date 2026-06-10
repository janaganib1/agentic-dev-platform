"""
agent2_architect.py
Architect Agent that:
1. Designs the SIMPLEST architecture that meets the requirement
2. Enforces generic technology and architecture rules for ANY domain
3. Explicitly defines import hierarchy to prevent circular imports
4. Outputs exact pip packages, run commands, and env vars
5. (RouteOne mode) Reads R1OD_Agentic_platform.md for team-specific context
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# ─── Platform Context Loader ─────────────────────────────────────────────────

def load_platform_context() -> str:
    """
    Loads the R1OD_Agentic_platform.md file for RouteOne mode.
    Search order:
      1. AGENT_MD_PATH env var (explicit path set in .env)
      2. Fallback: R1OD_Agentic_platform.md in the platform root (same dir as main.py)
    Returns the file contents as a string, or an empty string if not found.
    """
    # Primary: explicit path from env
    agent_md_path = os.getenv("AGENT_MD_PATH", "").strip()
    if agent_md_path and os.path.isfile(agent_md_path):
        try:
            with open(agent_md_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            print(f"📄 Loaded platform context from: {agent_md_path}")
            return content
        except Exception as e:
            print(f"⚠️  Could not read AGENT_MD_PATH ({agent_md_path}): {e}")

    # Fallback: platform root (directory containing this file → ../R1OD_Agentic_platform.md)
    fallback_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "R1OD_Agentic_platform.md"
    )
    if os.path.isfile(fallback_path):
        try:
            with open(fallback_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            print(f"📄 Loaded platform context from fallback: {fallback_path}")
            return content
        except Exception as e:
            print(f"⚠️  Could not read fallback context ({fallback_path}): {e}")

    print("⚠️  R1OD_Agentic_platform.md not found — proceeding without platform context.")
    return ""


def _build_platform_context_block(platform_context: str) -> str:
    """Wraps the platform context in a clearly labeled prompt block."""
    if not platform_context:
        return ""
    return f"""
════════════════════════════════════════
ROUTEONE TEAM PLATFORM CONTEXT
════════════════════════════════════════
The following is your team's internal platform guide.
Follow ALL conventions, patterns, and tech stack rules described here.
They override generic defaults where there is a conflict.

{platform_context}
════════════════════════════════════════
END OF PLATFORM CONTEXT
════════════════════════════════════════
"""


# ─── Core Agent ──────────────────────────────────────────────────────────────

def run_agent2(project_brief: str, platform_context: str = "") -> str:
    print("\n🤖 Agent 2 (Architect) is creating technical design...\n")

    platform_block = _build_platform_context_block(platform_context)

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
{platform_block}
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


# ─── Approval Loop (RouteOne mode only) ──────────────────────────────────────

def revise_plan(original_plan: str, feedback: str, project_brief: str, platform_context: str = "") -> str:
    """Ask the Architect to revise the change plan based on dev feedback."""
    print("\n🔄 Architect is revising the plan based on your feedback...\n")

    platform_block = _build_platform_context_block(platform_context)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a senior software architect.

You previously produced this change plan:
{original_plan}

The developer has reviewed it and provided this feedback:
{feedback}

Original project brief for context:
{project_brief}
{platform_block}
Please revise the change plan based on the feedback.
Keep the same structured format as before.
Only change what the feedback asks for — do not alter unrelated parts."""
            }
        ]
    )
    return response.content[0].text


def architect_approval_loop(project_brief: str) -> str:
    """
    RouteOne mode only.
    Runs the Architect agent and shows the change plan to the dev in CLI.
    Dev can approve or provide feedback for revision.
    Loops until dev approves.
    Returns the final approved technical design.
    """
    # Load platform context once — reused across all revisions
    platform_context = load_platform_context()

    # Step 1: Generate initial plan
    design = run_agent2(project_brief, platform_context=platform_context)
    revision_count = 0
    max_revisions = 5

    while revision_count < max_revisions:
        # Step 2: Show approval prompt
        print("\n" + "=" * 60)
        print("🏗️  ARCHITECT CHANGE PLAN — REVIEW REQUIRED")
        print("=" * 60)
        print("\nType 'approve' to proceed to code generation.")
        print("Or type your feedback to request a revision.")
        print("-" * 60)

        user_input = input("\nYour response: ").strip()

        # Step 3: Check if approved
        if user_input.lower() in ["approve", "approved", "yes", "y", "ok", "lgtm"]:
            print("\n✅ Plan approved — proceeding to Developer agent.")
            return design

        # Step 4: Handle empty input
        if not user_input:
            print("\n⚠️  No input received. Please type 'approve' or provide feedback.")
            continue

        # Step 5: Revise based on feedback
        revision_count += 1
        print(f"\n📝 Revision {revision_count}/{max_revisions}...")
        design = revise_plan(
            original_plan=design,
            feedback=user_input,
            project_brief=project_brief,
            platform_context=platform_context
        )

        # Show revised plan
        print("\n" + "=" * 60)
        print(f"🔄 REVISED CHANGE PLAN (Revision {revision_count})")
        print("=" * 60)
        print(design)
        print("=" * 60)

    # Max revisions reached
    print(f"\n⚠️  Maximum revisions ({max_revisions}) reached. Proceeding with latest plan.")
    return design


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