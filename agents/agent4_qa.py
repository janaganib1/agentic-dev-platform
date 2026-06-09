"""
agent4_qa.py
QA Agent that:
1. Reviews generated code ONLY for runtime blockers
2. Works for ANY domain or requirement type
3. NEVER fails for style, tests, type hints, or suggestions
4. Thinks like a Python runtime, not a code reviewer
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def run_agent4(generated_code: str) -> dict:
    print("\n🤖 Agent 4 (QA) is reviewing the code for runtime blockers...\n")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a Python runtime validator.
You check generated code for ANY domain — file processors, APIs, scrapers,
CLI tools, data pipelines, utilities, and more.

You have received this generated code:
{generated_code}

════════════════════════════════════════
YOUR ONLY JOB
════════════════════════════════════════

Think like the Python interpreter.
Ask ONE question: "Will this code crash when someone runs it?"

PASS if the code will run successfully for valid inputs.
FAIL only if the code will crash or fail to start.

════════════════════════════════════════
FAIL ONLY FOR THESE RUNTIME BLOCKERS
════════════════════════════════════════

1. SyntaxError — code has invalid Python syntax
2. ImportError on startup — imports a package not in requirements.txt
3. NameError on startup — uses variable/function that does not exist
4. Circular import — A imports B and B imports A
5. Missing critical function — a function that is called does not exist
6. Truncated file — a function or class is cut off and incomplete
7. Forbidden library used — win32com, pywin32, pydantic BaseSettings
8. src/__init__.py is not empty — has imports that cause startup failure

════════════════════════════════════════
ALWAYS PASS — IGNORE THESE COMPLETELY
════════════════════════════════════════

❌ DO NOT fail for any of these:
- Incomplete or missing tests
- Missing type hints or annotations
- Missing docstrings or comments
- Code style issues (naming, formatting, line length)
- Security suggestions (path traversal, injection, etc.)
- Performance suggestions (caching, retry, batching)
- Missing edge case handling
- Missing logging or verbose output
- Missing __all__ declarations
- Missing input validation beyond what is needed to run
- Race conditions or thread safety
- Missing error messages for edge cases
- Test coverage percentage
- Missing integration tests
- Any suggestion that starts with "Consider adding..."
- Any issue that only appears with invalid inputs

════════════════════════════════════════
OUTPUT FORMAT — USE EXACTLY THIS
════════════════════════════════════════

STATUS: PASS or FAIL

BLOCKERS: (list ONLY actual runtime blockers, or "None" if no blockers)
- <blocker 1>: <which file, which line, exactly what will crash>
- <blocker 2>: ...

VERDICT: <one sentence — will this run or not, and why>

RULES FOR YOUR RESPONSE:
- If STATUS is PASS, BLOCKERS must be "None"
- Only list issues that will cause an actual crash or import failure
- Do NOT list suggestions, improvements, or nice-to-haves
- Do NOT fail because tests are incomplete
- Do NOT fail because type hints are missing
- Do NOT fail because there are security concerns
- Be decisive — if it will run, say PASS"""
            }
        ]
    )

    result = response.content[0].text
    status = "PASS" if "STATUS: PASS" in result else "FAIL"

    print("✅ Agent 4 Output:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    print(f"\n🎯 QA Status: {status}")

    return {
        "status": status,
        "review": result
    }


if __name__ == "__main__":
    sample_code = """
# === src/main.py ===
import argparse
import os
from dotenv import load_dotenv
from .converter import convert

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Input file')
    args = parser.parse_args()
    convert(args.input)

if __name__ == "__main__":
    main()

# === src/converter.py ===
def convert(input_path):
    print(f"Converting {input_path}")
    return True

# === requirements.txt ===
python-dotenv==1.0.0
"""
    run_agent4(sample_code)
