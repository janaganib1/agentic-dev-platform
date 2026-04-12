"""
agent0_memory.py
Smart Memory Agent that:
1. Loads past runs from memory.json for ANY domain
2. Uses Claude to semantically compare new requirement vs past runs
3. Handles story-based memory entries (groups by project)
4. Scans existing project folders to load current state
5. Asks user clarifying questions before proceeding
6. Returns memory context for the rest of the pipeline
"""

import os
import re
import json
import anthropic
from dotenv import load_dotenv
from memory_manager import load_memory, get_existing_project_files, extract_tech_stack_from_requirements

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def group_runs_by_project(past_runs: list) -> list:
    """
    Group story-based memory entries by project folder.
    Returns a deduplicated list of projects with latest info.
    """
    projects = {}
    for run in past_runs:
        folder = run.get("project_folder", "")
        if folder not in projects:
            projects[folder] = run
        else:
            # Keep the most recently updated entry
            existing_date = projects[folder].get("last_updated", "")
            current_date = run.get("last_updated", "")
            if current_date > existing_date:
                projects[folder] = run
    return list(projects.values())


def compare_requirement_with_memory(requirement: str, past_runs: list) -> dict:
    """
    Use Claude to semantically compare the new requirement against past runs.
    Works for ANY domain — files, APIs, data, utilities, etc.
    Returns decision dict with: decision, matched_entry, reasoning, clarifying_question
    """
    if not past_runs:
        return {
            "decision": "NEW",
            "matched_entry": None,
            "reasoning": "No past runs found in memory.",
            "clarifying_question": None
        }

    # Group by project to avoid confusing story-level entries
    projects = group_runs_by_project(past_runs)

    past_projects_text = ""
    for i, run in enumerate(projects):
        # Clean up requirement — remove story suffix if present
        req = run['requirement'].split(' — Story')[0].strip()
        past_projects_text += f"""
Project {i+1}:
- Requirement: {req}
- Project Name: {run['project_name']}
- Folder: {run['project_folder']}
- Tech Stack: {', '.join(run.get('tech_stack', []))}
- QA Status: {run['qa_status']}
- Last Updated: {run.get('last_updated', run.get('created_at', 'Unknown'))}
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a smart memory agent for a code generation platform.
You handle ANY kind of software project — file processors, APIs, scrapers,
CLI tools, data pipelines, utilities, games, and more.

New requirement submitted:
"{requirement}"

Past projects in memory:
{past_projects_text}

YOUR JOB:
Compare the new requirement semantically against past projects.
Think about: same domain? same functionality? enhancement of existing? completely different?

Respond in EXACTLY this JSON format, nothing else:

{{
  "decision": "NEW" | "RELATED" | "SAME",
  "matched_project_index": null | <number starting from 1>,
  "reasoning": "<brief explanation of why you made this decision>",
  "clarifying_question": null | "<friendly question to ask the user>"
}}

DECISION RULES:
- "NEW": Completely different domain or functionality from all past projects
- "RELATED": Extends, enhances, or adds to an existing past project
  Examples: "add caching to the weather app", "add CSV export to the converter"
- "SAME": Nearly identical requirement to a past project
  Examples: same feature, same tool, same domain with minor wording difference

FOR RELATED OR SAME — clarifying_question must:
- State the past project name and when it was last updated
- Mention the tech stack that was used
- Mention if QA passed or failed previously
- Ask clearly: enhance existing, start fresh, or resume?
- Be concise and friendly — max 3 sentences

IMPORTANT:
- Compare SEMANTICALLY not just keyword matching
- "fetch stock price" and "get cryptocurrency value" are RELATED (both financial data)
- "convert word to pdf" and "add CLI to word converter" are RELATED (same project)
- "word to pdf converter" and "bitcoin price fetcher" are NEW (different domains)
- If QA status was FAIL, mention it in the clarifying question

Return ONLY the JSON. No explanation outside the JSON."""
            }
        ]
    )

    result_text = response.content[0].text.strip()
    result_text = re.sub(r'^```json\s*', '', result_text)
    result_text = re.sub(r'\s*```$', '', result_text)

    try:
        result = json.loads(result_text)
        matched_entry = None
        idx = result.get("matched_project_index")
        if idx:
            idx = int(idx) - 1
            if 0 <= idx < len(projects):
                matched_entry = projects[idx]
        result["matched_entry"] = matched_entry
        return result
    except (json.JSONDecodeError, ValueError):
        return {
            "decision": "NEW",
            "matched_entry": None,
            "reasoning": "Could not parse memory comparison.",
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
    print("  [1] Enhance — build on top of the existing project")
    print("  [2] Fresh   — start completely from scratch")
    print("  [3] Resume  — continue incomplete work from last session")
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
    Build memory context to pass into the pipeline based on user choice.
    Loads existing files and tech stack for enhance/resume modes.
    """
    if user_choice == "fresh" or matched_entry is None:
        return {
            "mode": "fresh",
            "existing_project_folder": None,
            "existing_files": {},
            "tech_stack": [],
            "failed_libraries": [],
            "context_summary": "Starting fresh — no previous work loaded."
        }

    project_folder = matched_entry["project_folder"]
    existing_files = get_existing_project_files(project_folder)
    tech_stack = matched_entry.get("tech_stack", [])

    if not tech_stack:
        tech_stack = extract_tech_stack_from_requirements(project_folder)

    # Clean requirement display
    original_req = matched_entry['requirement'].split(' — Story')[0].strip()

    # Note any previously failed libraries to avoid
    failed_libraries = []
    if matched_entry.get("qa_status") == "FAIL":
        failed_libraries = ["check existing code for problematic imports"]

    if user_choice == "enhance":
        mode = "enhance"
        context_summary = f"""Enhancing existing project: {matched_entry['project_name']}
Project folder: {project_folder}
Tech stack to reuse: {', '.join(tech_stack) if tech_stack else 'see requirements.txt'}
Existing files: {', '.join(list(existing_files.keys())[:15])}
Original requirement: {original_req}
Previous QA status: {matched_entry['qa_status']}"""

    else:  # resume
        mode = "resume"
        context_summary = f"""Resuming project: {matched_entry['project_name']}
Project folder: {project_folder}
Tech stack: {', '.join(tech_stack) if tech_stack else 'see requirements.txt'}
Files from last session: {', '.join(list(existing_files.keys())[:15])}
Last QA status: {matched_entry['qa_status']}
Original requirement: {original_req}"""

    return {
        "mode": mode,
        "existing_project_folder": project_folder,
        "existing_files": existing_files,
        "tech_stack": tech_stack,
        "failed_libraries": failed_libraries,
        "context_summary": context_summary
    }


def run_agent0(requirement: str) -> dict:
    """
    Main entry point for the Memory Agent.
    Returns memory context dict for the rest of the pipeline.
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
            "failed_libraries": [],
            "context_summary": "No past runs found. Starting fresh."
        }

    # Group by project first
    projects = group_runs_by_project(past_runs)
    print(f"   Found {len(projects)} past project(s). Comparing with new requirement...\n")

    comparison = compare_requirement_with_memory(requirement, past_runs)
    decision = comparison["decision"]
    matched_entry = comparison["matched_entry"]

    print(f"   Decision  : {decision}")
    print(f"   Reasoning : {comparison['reasoning']}\n")

    if decision == "NEW" or matched_entry is None:
        return {
            "mode": "fresh",
            "existing_project_folder": None,
            "existing_files": {},
            "tech_stack": [],
            "failed_libraries": [],
            "context_summary": "New requirement — starting fresh."
        }

    user_choice = ask_user_clarification(
        comparison["clarifying_question"],
        matched_entry
    )

    context = build_memory_context(user_choice, matched_entry)
    print(f"\n✅ Memory context loaded: {context['mode']} mode")
    print(f"   {context['context_summary']}\n")

    return context


if __name__ == "__main__":
    req = input("\nEnter your requirement: ")
    ctx = run_agent0(req)
    print("\nMemory Context:")
    print(f"  Mode    : {ctx['mode']}")
    print(f"  Summary : {ctx['context_summary']}")