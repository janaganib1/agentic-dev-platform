import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict

from agents.agent0_memory import run_agent0
from agents.agent05_story_splitter import run_agent05
from agents.agent1_orchestrator import run_agent1
from agents.agent2_architect import run_agent2, architect_approval_loop
from agents.agent3_developer import run_agent3, generate_project_name
from agents.agent4_qa import run_agent4
from agents.agent5_runtime_fixer import run_agent5
from agents.agent_github import run_github_agent
from git_manager import prepare_branch, commit_and_push
from memory_manager import add_memory_entry, extract_tech_stack_from_requirements

load_dotenv()

REPO_MODE = os.getenv("REPO_MODE", "personal").lower()


# ─── State Definition ────────────────────────────────────────────────────────

class AgentState(TypedDict):
    requirement: str
    current_story: dict
    memory_context: dict
    project_brief: str
    technical_design: str
    generated_code: str
    qa_review: str
    qa_status: str
    retry_count: int
    runtime_retry_count: int
    human_approved: bool
    project_folder: str
    runtime_fix_context: str
    auto_approve: bool


# ─── Agent Nodes ─────────────────────────────────────────────────────────────

def memory_node(state: AgentState) -> AgentState:
    existing = state.get("memory_context", {})
    if existing.get("mode"):
        print("\n🧠 Agent 0 (Memory) — skipping, using context from previous story.\n")
        return state
    context = run_agent0(state["requirement"])
    return {**state, "memory_context": context}


def orchestrator_node(state: AgentState) -> AgentState:
    story = state.get("current_story", {})
    story_req = story.get("requirement", state["requirement"])
    acceptance = story.get("acceptance_criteria", [])
    full_req = story_req
    if acceptance:
        full_req += f"\n\nAcceptance Criteria:\n" + "\n".join(f"- {c}" for c in acceptance)
    brief = run_agent1(full_req, memory_context=state.get("memory_context"))
    return {**state, "project_brief": brief}


def architect_node(state: AgentState) -> AgentState:
    memory_context = state.get("memory_context", {})
    existing_files = memory_context.get("existing_files", {})
    existing_code_section = ""
    if existing_files and memory_context.get("mode") in ["enhance", "resume"]:
        existing_code_section = "\n\nEXISTING CODE TO BUILD ON:\n"
        for path, content in existing_files.items():
            existing_code_section += f"\n### {path}\n{content}\n"
    project_brief = state["project_brief"] + existing_code_section

    # RouteOne mode — show plan to dev for approval before proceeding
    if REPO_MODE == "routeone" and not state.get("auto_approve"):
        design = architect_approval_loop(project_brief)
    else:
        design = run_agent2(project_brief)

    return {**state, "technical_design": design}


def developer_node(state: AgentState) -> AgentState:
    memory_context = state.get("memory_context", {})
    runtime_fix_context = state.get("runtime_fix_context", "")
    if runtime_fix_context:
        input_to_dev = f"""
The generated project had runtime errors that need to be fixed.

Runtime Error Details:
{runtime_fix_context}

Original Technical Design:
{state['technical_design']}

Please fix ALL the runtime errors mentioned above.
Make sure all imports are correct and all required packages are standard/available.
NEVER use pydantic BaseSettings — use python-dotenv with os.getenv() instead.
"""
    elif state.get("qa_review"):
        input_to_dev = f"""
Previous code had issues. QA Review:
{state['qa_review']}

Original Technical Design:
{state['technical_design']}

Please fix all the issues mentioned.
NEVER use pydantic BaseSettings — use python-dotenv with os.getenv() instead.
"""
    else:
        input_to_dev = state["technical_design"]

    existing_files = memory_context.get("existing_files", {})
    if existing_files and memory_context.get("mode") in ["enhance", "resume"]:
        existing_section = "\n\nEXISTING FILES (modify only what's needed):\n"
        for path, content in existing_files.items():
            existing_section += f"\n### {path}\n{content}\n"
        input_to_dev += existing_section

    code = run_agent3(input_to_dev, requirement=state["requirement"])

    # Use the same naming logic as agent3 to find actual folder
    project_folder = os.path.join("output", generate_project_name(state["requirement"]))

    return {
        **state,
        "generated_code": code,
        "project_folder": project_folder,
        "runtime_fix_context": "",
        "retry_count": state.get("retry_count", 0) + 1
    }


def qa_node(state: AgentState) -> AgentState:
    result = run_agent4(state["generated_code"])
    return {**state, "qa_status": result["status"], "qa_review": result["review"]}


def human_approval_node(state: AgentState) -> AgentState:
    # Skip interactive approval when running via webhook (auto_approve flag)
    if state.get("auto_approve"):
        print("\n🤖 Auto-approved via webhook trigger.")
        return {**state, "human_approved": True}

    story = state.get("current_story", {})
    story_title = story.get("title", "Implementation")
    print("\n" + "=" * 50)
    print("👤 HUMAN APPROVAL REQUIRED")
    print("=" * 50)
    print(f"\nStory: {story_title}")
    if state["qa_status"] == "PASS":
        print("QA has PASSED. Please review the generated code.")
    else:
        print("⚠️ Max retries reached. QA did not fully pass. Please review carefully.")
    print(f"📁 Project folder: {state.get('project_folder', 'output/')}")
    print("\nDo you approve this implementation?")
    approval = input("Type 'yes' to approve or 'no' to reject: ")
    approved = approval.lower() == "yes"
    print("\n✅ Approved!" if approved else "\n❌ Rejected.")
    return {**state, "human_approved": approved}


def runtime_fixer_node(state: AgentState) -> AgentState:
    result = run_agent5(
        project_folder=state["project_folder"],
        generated_code=state["generated_code"]
    )
    return {
        **state,
        "runtime_fix_context": result.get("fix_context", ""),
        "runtime_retry_count": state.get("runtime_retry_count", 0) + 1
    }


# ─── Routing ─────────────────────────────────────────────────────────────────

def route_after_qa(state: AgentState) -> str:
    if state["qa_status"] == "PASS":
        return "human_approval"
    elif state.get("retry_count", 0) >= 3:
        print("\n⚠️ Max retries reached. Moving to human approval anyway.")
        return "human_approval"
    else:
        print(f"\n🔄 QA Failed. Sending back to developer (Attempt {state.get('retry_count', 0) + 1})")
        return "developer"


def route_after_human(state: AgentState) -> str:
    return "runtime_fixer" if state["human_approved"] else "done"


def route_after_runtime_fix(state: AgentState) -> str:
    fix_context = state.get("runtime_fix_context", "")
    runtime_retries = state.get("runtime_retry_count", 0)
    if not fix_context:
        return "done"
    elif runtime_retries >= 3:
        print("\n⚠️ Max runtime fix attempts reached.")
        return "done"
    else:
        print(f"\n🔄 Runtime error found. Sending back to developer (Attempt {runtime_retries})")
        return "developer"


# ─── Pipeline Builder ─────────────────────────────────────────────────────────

def build_pipeline():
    graph = StateGraph(AgentState)
    graph.add_node("memory", memory_node)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("architect", architect_node)
    graph.add_node("developer", developer_node)
    graph.add_node("qa", qa_node)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("runtime_fixer", runtime_fixer_node)
    graph.set_entry_point("memory")
    graph.add_edge("memory", "orchestrator")
    graph.add_edge("orchestrator", "architect")
    graph.add_edge("architect", "developer")
    graph.add_edge("developer", "qa")
    graph.add_conditional_edges("qa", route_after_qa, {
        "developer": "developer",
        "human_approval": "human_approval"
    })
    graph.add_conditional_edges("human_approval", route_after_human, {
        "runtime_fixer": "runtime_fixer",
        "done": END
    })
    graph.add_conditional_edges("runtime_fixer", route_after_runtime_fix, {
        "developer": "developer",
        "done": END
    })
    return graph.compile()


# ─── Summary Generator ────────────────────────────────────────────────────────

def generate_project_summary(requirement, split_result, story_results, project_folder):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    complexity = split_result.get("complexity", "UNKNOWN")
    project_name = split_result.get("project_name", "project")
    project_summary = split_result.get("project_summary", requirement)
    completed = [r for r in story_results if r["approved"]]
    failed = [r for r in story_results if not r["approved"]]
    lines = [
        f"# Project Summary: {project_name}", "",
        f"**Generated:** {now}",
        f"**Complexity:** {complexity}",
        f"**Original Requirement:** {requirement}",
        f"**Project Summary:** {project_summary}",
        f"**Project Folder:** `{project_folder}`", "", "---", "",
        f"## Stories Completed: {len(completed)}/{len(story_results)}", "",
    ]
    for result in story_results:
        story = result["story"]
        status = "✅ DONE" if result["approved"] else "❌ REJECTED"
        qa = result.get("qa_status", "UNKNOWN")
        lines += [
            f"### Story {story['story_number']}: {story['title']} — {status}", "",
            f"**Requirement:** {story['requirement']}", "", "**Acceptance Criteria:**",
        ]
        for c in story.get("acceptance_criteria", []):
            lines.append(f"- {c}")
        lines += ["", f"**QA Status:** {qa}", f"**Tech Stack:** {result.get('tech_stack', 'See requirements.txt')}", "", "---", ""]
    if failed:
        lines += ["## ⚠️ Stories Not Completed", ""]
        for result in failed:
            story = result["story"]
            lines.append(f"- Story {story['story_number']}: {story['title']} — REJECTED by user")
        lines.append("")
    lines += [
        "## How to Run", "", "```bash",
        f"cd {project_folder}",
        "pip install -r requirements.txt",
        "py -m src.main <your_arguments>",
        "```", "", "## Notes for Jira", "",
        f"- Total stories implemented: {len(completed)}",
        f"- All stories are in folder: `{project_folder}`",
        "- Each story's code is in `src/` subfolder",
        "- Tests are in `tests/` subfolder", "",
    ]
    return "\n".join(lines)


def save_summary(summary_md, project_folder):
    os.makedirs(project_folder, exist_ok=True)
    summary_path = os.path.join(project_folder, "SUMMARY.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_md)
    return summary_path


# ─── Shared Pipeline Runner (used by CLI and webhook) ─────────────────────────

def run_full_pipeline(requirement: str, ticket_id: str = None, auto_approve: bool = False) -> dict:
    """
    Core pipeline runner — shared between CLI and webhook trigger.
    - auto_approve=False: interactive CLI mode (prompts for approval)
    - auto_approve=True:  webhook mode (auto-approves, pushes to GitHub)
    """
    print(f"\n{'=' * 50}")
    print(f"🚀 AGENTIC DEV PLATFORM")
    print(f"{'=' * 50}")

    # Step 0: Prepare git branch
    if ticket_id:
        prepare_branch(ticket_id)

    # Step 1: Split into stories
    split_result = run_agent05(requirement)
    stories = split_result["stories"]
    project_name = split_result["project_name"]
    project_folder = os.path.join("output", project_name)

    pipeline = build_pipeline()
    story_results = []
    memory_context = {}
    actual_project_folder = project_folder

    # Step 2: Execute each story
    for i, story in enumerate(stories):
        print(f"\n{'=' * 50}")
        print(f"▶️  EXECUTING STORY {story['story_number']}/{len(stories)}: {story['title']}")
        print(f"{'=' * 50}")

        if i > 0 and memory_context:
            print(f"🔗 Continuing with existing project context from Story {i}...\n")

        initial_state: AgentState = {
            "requirement": requirement,
            "current_story": story,
            "memory_context": memory_context if i > 0 else {},
            "project_brief": "",
            "technical_design": "",
            "generated_code": "",
            "qa_review": "",
            "qa_status": "",
            "retry_count": 0,
            "runtime_retry_count": 0,
            "human_approved": False,
            "auto_approve": auto_approve,
            "project_folder": project_folder,
            "runtime_fix_context": ""
        }

        final_state = pipeline.invoke(initial_state)

        tech_stack = extract_tech_stack_from_requirements(
            final_state.get("project_folder", project_folder)
        )
        story_results.append({
            "story": story,
            "approved": final_state["human_approved"],
            "qa_status": final_state["qa_status"],
            "tech_stack": ", ".join(tech_stack) if tech_stack else "See requirements.txt"
        })

        if final_state["human_approved"]:
            actual_project_folder = final_state.get("project_folder", project_folder)
            memory_context = {
                "mode": "enhance",
                "existing_project_folder": actual_project_folder,
                "existing_files": {},
                "tech_stack": tech_stack,
                "context_summary": f"Story {story['story_number']} complete: {story['title']}",
                "same_ticket": True
            }
            add_memory_entry(
                requirement=f"{requirement} — Story {story['story_number']}: {story['title']}",
                project_name=project_name,
                project_folder=final_state.get("project_folder", project_folder),
                tech_stack=tech_stack,
                files_generated=[],
                qa_status=final_state["qa_status"]
            )
            print(f"\n💾 Story {story['story_number']} saved to memory.")
        else:
            print(f"\n⏭️  Story {story['story_number']} rejected. Stopping pipeline.")
            break

    # Step 3: Generate and save summary
    print(f"\n{'=' * 50}")
    print("📝 Generating project summary...")
    summary_md = generate_project_summary(
        requirement=requirement,
        split_result=split_result,
        story_results=story_results,
        project_folder=actual_project_folder
    )
    summary_path = save_summary(summary_md, actual_project_folder)

    completed = [r for r in story_results if r["approved"]]

    # Step 4: Push to GitHub (only in webhook/auto_approve mode)
    github_result = {}
    if auto_approve and completed and ticket_id:
        print(f"\n{'=' * 50}")
        print("🐙 Pushing to GitHub...")
        github_result = run_github_agent(
            ticket_id=ticket_id,
            local_folder=actual_project_folder
        )
        commit_and_push(ticket_id)

    print(f"\n{'=' * 50}")
    print("🏁 PIPELINE COMPLETE")
    print(f"{'=' * 50}")
    print(f"✅ Stories completed: {len(completed)}/{len(stories)}")
    print(f"📁 Project folder: {actual_project_folder}")
    print(f"📋 Summary saved: {summary_path}")

    return {
        "stories_completed": len(completed),
        "stories_total": len(stories),
        "project_folder": actual_project_folder,
        "summary_path": summary_path,
        "github": github_result
    }


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    requirement = input("\nEnter your requirement: ")
    run_full_pipeline(requirement=requirement, auto_approve=False)