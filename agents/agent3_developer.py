"""
agent3_developer.py
Developer Agent that:
1. Implements ANY requirement as a complete multi-file Python project
2. Follows strict code quality rules to ensure first-run success
3. Never cuts off files mid-function
4. Produces exactly what Agent 2 designed — no extras
"""

import os
import re
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def parse_multi_file_response(response_text: str) -> dict:
    """
    Parses the agent response and extracts multiple files.
    Expected format:
        ### FILE: path/to/file.py
        <code here>
    Returns a dict: { "path/to/file.py": "<content>", ... }
    """
    files = {}
    parts = re.split(r'###\s*FILE:\s*', response_text)
    for part in parts[1:]:
        lines = part.strip().splitlines()
        if not lines:
            continue
        file_path = lines[0].strip()
        file_content = "\n".join(lines[1:]).strip()

        if file_content.startswith("```"):
            file_content = file_content.split("\n", 1)[1] if "\n" in file_content else ""
        if file_content.endswith("```"):
            file_content = file_content.rsplit("```", 1)[0]

        files[file_path] = file_content.strip()

    return files


def save_project_files(project_name: str, files: dict) -> str:
    """Save all generated files under output/<project_name>/"""
    project_root = os.path.join("output", project_name)
    os.makedirs(project_root, exist_ok=True)

    for relative_path, content in files.items():
        full_path = os.path.join(project_root, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   📄 Created: {full_path}")

    return project_root


def generate_project_name(text: str) -> str:
    """Generate clean project folder name from requirement text."""
    skip = {
        'given', 'using', 'with', 'from', 'that', 'this', 'will', 'have',
        'build', 'create', 'make', 'develop', 'simple', 'basic', 'just',
        'only', 'some', 'into', 'should', 'which', 'where', 'when', 'then'
    }
    words = re.sub(r'[^a-zA-Z0-9\s]', '', text[:80])
    words = [w.lower() for w in words.split() if len(w) >= 3 and w.lower() not in skip][:4]
    return '_'.join(words) if words else 'generated_project'


def run_agent3(technical_design: str, requirement: str = "") -> str:
    """
    Run the developer agent to generate a complete multi-file Python project.

    Args:
        technical_design: Technical design from Agent 2
        requirement: Original user requirement (used for project folder naming)
    """
    print("\n🤖 Agent 3 (Developer) is writing the code...\n")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=16000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a senior Python developer.
You implement ANY kind of Python project — CLI tools, APIs, file processors,
web scrapers, data pipelines, utilities, automation scripts, and more.

You have received this technical design:
{technical_design}

════════════════════════════════════════
IMPLEMENTATION RULES — ALWAYS FOLLOW
════════════════════════════════════════

TECHNOLOGY RULES:
❌ NEVER use: win32com, pywin32, AppKit, or ANY OS-automation library
❌ NEVER use: docx2pdf (requires MS Word installed — use python-docx + reportlab instead)
❌ NEVER use: pydantic BaseSettings or pydantic-settings (use os.getenv() instead)
❌ NEVER use: click, typer, fire (use argparse)
❌ NEVER use: httpx, aiohttp (use requests)
❌ NEVER use: async/await unless design explicitly requires it
✅ ALWAYS use: os.getenv() + python-dotenv for ALL configuration
✅ ALWAYS use: argparse for CLI interfaces
✅ ALWAYS use: requests for HTTP calls
✅ ALWAYS use: the exact libraries specified in the technical design

IMPORT RULES:
✅ Follow the import hierarchy from the technical design EXACTLY
✅ src/__init__.py must be EMPTY — no imports
✅ tests/__init__.py must be EMPTY — no imports
✅ config.py must have NO project imports — only standard library + dotenv
✅ Use relative imports (from .config import ...) inside src/ package
❌ NEVER create circular imports — if A imports B, B must not import A

CODE COMPLETENESS RULES:
✅ Every function must be COMPLETE — no pass, no TODO, no ... placeholders
✅ Every file must be COMPLETE — never cut off mid-function or mid-class
✅ If running low on space — simplify the code, NEVER truncate it
✅ main.py MUST have if __name__ == "__main__": block
✅ requirements.txt must list EVERY non-standard library that is imported
✅ .env.example must list EVERY environment variable used in code

TEST RULES:
✅ test_main.py must be COMPLETE and RUNNABLE
✅ Tests must be simple — happy path only
✅ Maximum 30 lines per test file
✅ Use pytest style (def test_xxx():)
✅ Mock external calls (API, file system) where needed
❌ NEVER write incomplete test functions
❌ NEVER write tests that require real API keys or real files to pass

SCOPE RULES:
✅ Implement EXACTLY what the design says — nothing more
❌ NEVER add caching, retry logic, rate limiting, or auth unless in design
❌ NEVER add extra validation beyond what is needed to run
❌ NEVER add logging configuration unless design specifies it
❌ NEVER add security hardening unless design specifies it

════════════════════════════════════════
PRE-OUTPUT CHECKLIST — VERIFY BEFORE RESPONDING
════════════════════════════════════════

Before writing your response, verify:
1. ✅ All imports at top of each file will resolve
2. ✅ requirements.txt lists every non-standard import
3. ✅ No file cuts off mid-function
4. ✅ src/__init__.py is empty
5. ✅ main.py has if __name__ == "__main__": block
6. ✅ Import hierarchy has no circular dependencies
7. ✅ No pydantic, no win32com, no click, no httpx anywhere
8. ✅ test file is complete and under 30 lines

════════════════════════════════════════
OUTPUT FORMAT — USE EXACTLY THIS FORMAT
════════════════════════════════════════

Use EXACTLY this format for each file — no exceptions:

### FILE: src/__init__.py
### FILE: src/config.py
### FILE: src/main.py
### FILE: tests/__init__.py
### FILE: tests/test_main.py
### FILE: requirements.txt
### FILE: README.md
### FILE: .env.example

Rules for each file:
- Start each with ### FILE: path/to/file
- Write complete file content immediately after
- No explanations between files
- Return ONLY the files — no text before or after"""
            }
        ]
    )

    result = response.content[0].text
    files = parse_multi_file_response(result)

    # Use requirement for project name if provided
    naming_source = requirement if requirement.strip() else technical_design
    project_name = generate_project_name(naming_source)

    if not files:
        print("⚠️  Could not parse multi-file response. Saving as single file.")
        output_path = f"output/{project_name}.py"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"✅ Saved to: {output_path}")
        return result

    project_root = save_project_files(project_name, files)

    print("\n✅ Agent 3 Output:")
    print("-" * 50)
    print(f"📁 Project folder: {project_root}")
    print(f"📦 Files generated: {len(files)}")
    print("-" * 50)

    combined = "\n\n".join(
        f"# === {path} ===\n{content}" for path, content in files.items()
    )
    return combined


if __name__ == "__main__":
    sample_design = """
    ## Goal
    Read a .docx file and convert text to PDF.

    ## Technology Stack
    - python-docx: read Word files
    - reportlab: generate PDF

    ## Import Hierarchy
    config.py → no project imports
    converter.py → imports config.py
    main.py → imports converter.py, config.py

    ## Files
    src/__init__.py, src/main.py, src/config.py, src/converter.py
    tests/__init__.py, tests/test_main.py
    requirements.txt, README.md, .env.example

    ## Run Command
    py -m src.main input.docx
    """
    run_agent3(sample_design, requirement="convert word document to pdf")