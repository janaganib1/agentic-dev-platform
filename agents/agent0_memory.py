"""
agent0_memory.py
Smart memory agent that:
1. Loads past runs from memory.json
2. Uses Claude to compare new requirement vs past runs
3. Scans existing project folders
4. Asks user clarifying questions before proceeding
5. Returns memory context for the rest of the pipeline
"""

import os
import anthropic
from dotenv import load_dotenv
from memory_manager import load_memory, get_existing_project_files, extract_tech_stack_from_requirements

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def compare_requirement_with_memory(requirement: str, past_runs: list) -> dict:
    """
    Use Claude to compare the new requirement against all past runs.
    Returns a decision dict with keys: decision, matched_entry, reasoning, clarifying_question
    """
    if not past_runs:
        return {
            "decision": "NEW",
            "matched_entry": None,
            "reasoning": "No past runs found in memory.",
            "clarifying_question": None
        }

    # Format past runs for Claude
    past_runs_text = ""
    for i, run in enumerate(past_runs):
        past_runs_text += f"""
Run {i+1}:
- Requirement: {run['requirement']}
- Project: {run['project_name']}
- Folder: {run['project_folder']}
- Tech Stack: {', '.join(run.get('tech_stack', []))}
- QA Status: {run['qa_status']}
- Last Updated: {run.get('last_updated', run.get('created_at', 'Unknown'))}
- Files: {', '.join(run.get('files_generated', []))}
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a smart memory agent for a code generation platform.

A user has submitted this new requirement:
"{requirement}"

Here are all past runs from memory:
{past_runs_text}

Your job is to analyze and respond in EXACTLY this JSON format, nothing else:

{{
  "decision": "NEW" | "RELATED" | "SAME",
  "matched_run_index": null | <number starting from 1>,
  "reasoning": "<brief explanation>",
  "clarifying_question": null | "<question to ask the user>"
}}

Decision rules:
- "NEW": The requirement is completely unrelated to any past run
- "RELATED": The requirement extends, enhances, or continues work from a past run
- "SAME": The requirement is identical or nearly identical to a past run

For RELATED or SAME, always include a clarifying_question that:
- Mentions the past project name and last updated date
- Lists key existing files
- Asks whether to enhance existing code, start fresh, or resume incomplete work
- Is friendly and clear

Return ONLY the JSON. No explanation outside the JSON."""
            }
        ]
    )

    import json
    import re
    result_text = response.content[0].text.strip()

    # Strip markdown if present
    result_text = re.sub(r'^```json\s*', '', result_text)
    result_text = re.sub(r'\s*```$', '', result_text)

    try:
        result = json.loads(result_text)
        matched_entry = None
        if result.get("matched_run_index"):
            idx = int(result["matched_run_index"]) - 1
            if 0 <= idx < len(past_runs):
                matched_entry = past_runs[idx]
        result["matched_entry"] = matched_entry
        return result
    except (json.JSONDecodeError, ValueError):
        return {
            "decision": "NEW",
            "matched_entry": None,
            "reasoning": "Could not parse memory comparison result.",
            "clarifying_question": None
        }


def ask_user_clarification(question: str, matched_entry: dict) -> str:
    """
    Show the user the clarifying question and get their choice.
    Returns: 'enhance', 'fresh', or 'resume'
    """
    print("\n" + "=" * 50)
    print("🧠 MEMORY AGENT — Past Work Found")
    print("=" * 50)
    print(f"\n{question}")
    print("\nWhat would you like to do?")
    print("  [1] Enhance existing code — build on top of the previous project")
    print("  [2] Start fresh — ignore previous work and generate new code")
    print("  [3] Resume — continue incomplete work from the last session")
    print()

    while True:
        choice = input("Enter 1, 2, or 3: ").strip()
        if choice == "1":
            return "enhance"
        elif choice == "2":
            return "fresh"
        elif choice == "3":
            return "resume"
        else:
            print("Please enter 1, 2, or 3.")


def build_memory_context(user_choice: str, matched_entry: dict) -> dict:
    """
    Based on user choice, build the memory context to pass into the pipeline.
    Returns a context dict with all info agents need.
    """
    if user_choice == "fresh" or matched_entry is None:
        return {
            "mode": "fresh",
            "existing_project_folder": None,
            "existing_files": {},
            "tech_stack": [],
            "context_summary": "Starting fresh — no previous work loaded."
        }

    project_folder = matched_entry["project_folder"]
    existing_files = get_existing_project_files(project_folder)
    tech_stack = matched_entry.get("tech_stack", [])

    # Try to get tech stack from requirements.txt if not in memory
    if not tech_stack:
        tech_stack = extract_tech_stack_from_requirements(project_folder)

    if user_choice == "enhance":
        mode = "enhance"
        context_summary = f"""Enhancing existing project: {matched_entry['project_name']}
Project folder: {project_folder}
Tech stack to reuse: {', '.join(tech_stack)}
Existing files loaded: {', '.join(existing_files.keys())}
Original requirement: {matched_entry['requirement']}"""

    else:  # resume
        mode = "resume"
        context_summary = f"""Resuming existing project: {matched_entry['project_name']}
Project folder: {project_folder}
Tech stack: {', '.join(tech_stack)}
Files from last session: {', '.join(existing_files.keys())}
Last QA status: {matched_entry['qa_status']}
Original requirement: {matched_entry['requirement']}"""

    return {
        "mode": mode,
        "existing_project_folder": project_folder,
        "existing_files": existing_files,
        "tech_stack": tech_stack,
        "context_summary": context_summary
    }


def run_agent0(requirement: str) -> dict:
    """
    Main entry point for the memory agent.
    Returns memory context dict to be passed into the pipeline state.
    """
    print("\n🧠 Agent 0 (Memory) is checking past runs...\n")

    past_runs = load_memory()

    if not past_runs:
        print("   No past runs found. Starting fresh.\n")
        return {
            "mode": "fresh",
            "existing_project_folder": None,
            "existing_files": {},
            "tech_stack": [],
            "context_summary": "No past runs found. Starting fresh."
        }

    print(f"   Found {len(past_runs)} past run(s). Comparing with new requirement...\n")

    # Use Claude to compare
    comparison = compare_requirement_with_memory(requirement, past_runs)
    decision = comparison["decision"]
    matched_entry = comparison["matched_entry"]

    print(f"   Decision: {decision}")
    print(f"   Reasoning: {comparison['reasoning']}\n")

    if decision == "NEW" or matched_entry is None:
        return {
            "mode": "fresh",
            "existing_project_folder": None,
            "existing_files": {},
            "tech_stack": [],
            "context_summary": "New requirement — starting fresh."
        }

    # Ask user what to do
    user_choice = ask_user_clarification(
        comparison["clarifying_question"],
        matched_entry
    )

    # Build and return context
    context = build_memory_context(user_choice, matched_entry)
    print(f"\n✅ Memory context loaded: {context['mode']} mode")
    print(f"   {context['context_summary']}\n")

    return context


if __name__ == "__main__":
    req = input("\nEnter your requirement: ")
    ctx = run_agent0(req)
    print("\nMemory Context:")
    print(f"  Mode: {ctx['mode']}")
    print(f"  Summary: {ctx['context_summary']}")