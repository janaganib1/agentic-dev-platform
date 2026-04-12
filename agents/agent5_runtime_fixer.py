"""
agent5_runtime_fixer.py
Runtime Fixer Agent that:
1. Validates ANY generated Python project after human approval
2. Auto-installs missing dependencies
3. Checks compilation of all Python files
4. Attempts test run and fixes errors automatically
5. Uses Claude to analyze errors and decide fix strategy
6. Can run standalone to fix errors without re-running full pipeline
"""

import os
import re
import sys
import subprocess
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MAX_FIX_ATTEMPTS = 3


def run_command(cmd: list, cwd: str = None) -> tuple:
    """Run a shell command. Returns (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def install_requirements(project_folder: str) -> tuple:
    """Auto-install from requirements.txt. Returns (success, output)."""
    req_path = os.path.join(project_folder, "requirements.txt")
    if not os.path.exists(req_path):
        return True, "No requirements.txt found — skipping."

    print(f"\n📦 Installing dependencies from requirements.txt...")
    returncode, stdout, stderr = run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        cwd=project_folder
    )
    if returncode == 0:
        print("   ✅ Dependencies installed successfully.")
        return True, stdout
    else:
        print(f"   ⚠️ Some dependencies failed to install.")
        return False, stderr


def check_compilation(project_folder: str) -> tuple:
    """Check all .py files in src/ for syntax errors. Returns (success, errors)."""
    print("\n🔍 Checking compilation of all Python files...")
    src_folder = os.path.join(project_folder, "src")
    if not os.path.exists(src_folder):
        src_folder = project_folder

    errors = []
    for root, dirs, files in os.walk(src_folder):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv']]
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                returncode, stdout, stderr = run_command(
                    [sys.executable, "-m", "py_compile", full_path]
                )
                if returncode != 0:
                    errors.append(f"{full_path}:\n{stderr}")

    if errors:
        print(f"   ❌ Compilation errors in {len(errors)} file(s).")
        return False, "\n".join(errors)
    else:
        print("   ✅ All files compiled successfully.")
        return True, ""


def attempt_test_run(project_folder: str) -> tuple:
    """Try running the project with --help to check imports work."""
    print("\n🚀 Attempting test run...")
    returncode, stdout, stderr = run_command(
        [sys.executable, "-m", "src.main", "--help"],
        cwd=project_folder
    )

    combined = stderr + stdout
    # These indicate real import/module failures
    failure_indicators = [
        "ModuleNotFoundError",
        "ImportError",
        "pydantic",
        "cannot import",
        "No module named",
        "Traceback"
    ]
    for indicator in failure_indicators:
        if indicator.lower() in combined.lower():
            return False, stdout, stderr

    print("   ✅ Test run completed without import/module errors.")
    return True, stdout, stderr


def analyze_error_with_claude(error_text: str, project_folder: str) -> dict:
    """
    Use Claude to analyze ANY runtime error and decide fix strategy.
    Works for any domain — file processing, APIs, databases, etc.
    """
    file_summary = ""
    src_folder = os.path.join(project_folder, "src")
    if os.path.exists(src_folder):
        for f in os.listdir(src_folder):
            if f.endswith(".py"):
                file_summary += f"- src/{f}\n"

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a Python runtime error analyst.
You handle errors from ANY kind of Python project — file processors, APIs,
scrapers, CLI tools, data pipelines, utilities, and more.

Project folder: {project_folder}
Project files:
{file_summary}

Error encountered:
{error_text}

Analyze and respond in EXACTLY this JSON format, nothing else:

{{
  "action": "install_package" | "fix_code" | "ask_user" | "show_instructions",
  "packages_to_install": [],
  "fix_description": "<brief description of what needs fixing>",
  "fix_instructions": "<step by step instructions if action is show_instructions>",
  "question_for_user": null | "<specific question if action is ask_user>",
  "is_fixable_automatically": true | false
}}

ACTION RULES:
- "install_package": missing Python package — list exact pip install names
- "fix_code": code bug needing regeneration (wrong import, missing function, syntax)
- "ask_user": need info from user (missing API key, missing input file, missing env var)
- "show_instructions": manual steps needed (OS config, external service setup, etc.)

IMPORTANT:
- For OS-level dependencies (Word, LibreOffice, etc.) → use show_instructions
  AND suggest a pure-Python alternative library in fix_instructions
- For pydantic BaseSettings errors → use fix_code, mention use os.getenv() instead
- For win32com errors → use fix_code, mention use python-docx + reportlab instead
- Be specific about package names (e.g. "python-dotenv" not "dotenv")

Return ONLY the JSON."""
            }
        ]
    )

    import json
    result_text = response.content[0].text.strip()
    result_text = re.sub(r'^```json\s*', '', result_text)
    result_text = re.sub(r'\s*```$', '', result_text)

    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {
            "action": "show_instructions",
            "packages_to_install": [],
            "fix_description": "Could not analyze error automatically.",
            "fix_instructions": f"Please review this error manually:\n{error_text}",
            "question_for_user": None,
            "is_fixable_automatically": False
        }


def install_missing_package(packages: list) -> bool:
    """Install one or more missing packages."""
    for package in packages:
        print(f"\n📦 Auto-installing: {package}")
        returncode, stdout, stderr = run_command(
            [sys.executable, "-m", "pip", "install", package]
        )
        if returncode == 0:
            print(f"   ✅ {package} installed.")
        else:
            print(f"   ❌ Failed to install {package}: {stderr}")
            return False
    return True


def run_agent5(project_folder: str, generated_code: str = "") -> dict:
    """
    Main entry point for the Runtime Fixer agent.
    Validates and fixes any generated Python project.

    Returns:
        dict with keys: success, needs_code_fix, fix_context, instructions
    """
    print("\n" + "=" * 50)
    print("🤖 Agent 5 (Runtime Fixer) is validating the project...")
    print("=" * 50)

    if not os.path.exists(project_folder):
        print(f"❌ Project folder not found: {project_folder}")
        return {
            "success": False,
            "needs_code_fix": False,
            "fix_context": "",
            "instructions": f"Project folder not found: {project_folder}"
        }

    # Step 1: Install requirements
    install_requirements(project_folder)

    # Step 2: Check compilation
    compile_success, compile_errors = check_compilation(project_folder)
    if not compile_success:
        print(f"\n❌ Compilation errors detected. Analyzing...")
        analysis = analyze_error_with_claude(compile_errors, project_folder)
        if analysis["action"] == "fix_code":
            return {
                "success": False,
                "needs_code_fix": True,
                "fix_context": f"Compilation errors:\n{compile_errors}\n\nFix: {analysis['fix_description']}",
                "instructions": ""
            }

    # Step 3: Attempt test run with retry loop
    attempt = 0
    last_error = ""

    while attempt < MAX_FIX_ATTEMPTS:
        attempt += 1
        print(f"\n   Attempt {attempt}/{MAX_FIX_ATTEMPTS}...")

        run_success, stdout, stderr = attempt_test_run(project_folder)

        if run_success:
            print("\n✅ Agent 5: Project validated successfully!")
            print("\n📋 HOW TO RUN YOUR PROJECT:")
            print("-" * 50)
            print(f"1. cd {project_folder}")
            print(f"2. Check README.md for required environment variables")
            print(f"3. Copy .env.example to .env and fill in values")
            print(f"4. pip install -r requirements.txt")
            print(f"5. py -m src.main <your_arguments>")
            print("-" * 50)
            return {
                "success": True,
                "needs_code_fix": False,
                "fix_context": "",
                "instructions": f"Project ready. Run: cd {project_folder} && py -m src.main <args>"
            }

        last_error = stderr + stdout
        print(f"\n⚠️  Error detected. Analyzing...")
        analysis = analyze_error_with_claude(last_error, project_folder)

        print(f"   Action : {analysis['action']}")
        print(f"   Fix    : {analysis['fix_description']}")

        if analysis["action"] == "install_package" and analysis["packages_to_install"]:
            installed = install_missing_package(analysis["packages_to_install"])
            if installed:
                continue

        elif analysis["action"] == "fix_code":
            return {
                "success": False,
                "needs_code_fix": True,
                "fix_context": f"Runtime error:\n{last_error}\n\nFix needed: {analysis['fix_description']}",
                "instructions": ""
            }

        elif analysis["action"] == "ask_user":
            print(f"\n❓ {analysis['question_for_user']}")
            user_input = input("Your answer (or press Enter to skip): ").strip()
            if user_input:
                last_error += f"\nUser provided: {user_input}"
            continue

        elif analysis["action"] == "show_instructions":
            print(f"\n📋 Manual steps required:")
            print(analysis["fix_instructions"])
            return {
                "success": False,
                "needs_code_fix": False,
                "fix_context": "",
                "instructions": analysis["fix_instructions"]
            }

    print(f"\n⚠️  Could not auto-fix after {MAX_FIX_ATTEMPTS} attempts.")
    print("📋 Please review the error manually:")
    print(last_error)

    return {
        "success": False,
        "needs_code_fix": False,
        "fix_context": last_error,
        "instructions": f"Manual fix required. Last error:\n{last_error}"
    }


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🔧 AGENT 5 — STANDALONE RUNTIME FIXER")
    print("=" * 50)

    folder = input("\nEnter project folder path (e.g. output/my_project): ").strip()
    if not folder:
        print("❌ No folder provided. Exiting.")
        exit(1)

    print("\nPaste the error message you got (or press Enter to auto-detect):")
    error_input = input("> ").strip()

    print("\nAny special instructions? (or press Enter to skip):")
    instructions = input("> ").strip()

    if error_input:
        print(f"\n🔍 Analyzing provided error...")
        analysis = analyze_error_with_claude(
            error_input + (f"\n\nSpecial instructions: {instructions}" if instructions else ""),
            folder
        )
        print(f"\n   Action : {analysis['action']}")
        print(f"   Fix    : {analysis['fix_description']}")

        if analysis["action"] == "install_package" and analysis["packages_to_install"]:
            install_missing_package(analysis["packages_to_install"])
            print("\n✅ Packages installed. Try running your project again.")

        elif analysis["action"] == "fix_code":
            print(f"\n📋 Code fix needed: {analysis['fix_description']}")
            print("⚠️  Re-run through the full pipeline with this error context.")
            print(f"   Or manually fix: {analysis.get('fix_instructions', 'See error above')}")

        elif analysis["action"] == "ask_user":
            print(f"\n❓ {analysis['question_for_user']}")

        elif analysis["action"] == "show_instructions":
            print(f"\n📋 Manual steps:")
            print(analysis["fix_instructions"])
    else:
        result = run_agent5(folder)
        if result["success"]:
            print("\n✅ Project is running fine — no issues found!")
        elif result["instructions"]:
            print(f"\n📋 {result['instructions']}")