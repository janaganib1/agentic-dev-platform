import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict

from agents.agent0_memory import run_agent0
from agents.agent1_orchestrator import run_agent1
from agents.agent2_architect import run_agent2
from agents.agent3_developer import run_agent3, generate_project_name
from agents.agent4_qa import run_agent4
from agents.agent5_runtime_fixer import run_agent5
from memory_manager import add_memory_entry, extract_tech_stack_from_requirements

load_dotenv()

# Define the state that flows between agents
class AgentState(TypedDict):
    requirement: str
    memory_context: dict
    project_brief: str
    technical_design: str
    generated_code: str
    qa_review: str
    qa_status: str
    retry_count: int
    runtime_retry_count: int       # NEW: tracks runtime fix retries
    human_approved: bool
    project_folder: str
    runtime_fix_context: str       # NEW: error context from agent5 for agent3 to fix

# Agent node functions
def memory_node(state: AgentState) -> AgentState:
    context = run_agent0(state["requirement"])
    return {**state, "memory_context": context}

def orchestrator_node(state: AgentState) -> AgentState:
    brief = run_agent1(state["requirement"], memory_context=state.get("memory_context"))
    return {**state, "project_brief": brief}

def architect_node(state: AgentState) -> AgentState:
    memory_context = state.get("memory_context", {})
    existing_files = memory_context.get("existing_files", {})

    existing_code_section = ""
    if existing_files and memory_context.get("mode") in ["enhance", "resume"]:
        existing_code_section = "\n\nEXISTING CODE TO BUILD ON:\n"
        for path, content in existing_files.items():
            existing_code_section += f"\n### {path}\n{content}\n"

    design = run_agent2(state["project_brief"] + existing_code_section)
    return {**state, "technical_design": design}

def developer_node(state: AgentState) -> AgentState:
    memory_context = state.get("memory_context", {})
    runtime_fix_context = state.get("runtime_fix_context", "")

    if runtime_fix_context:
        # Runtime fixer sent code back for fixing
        input_to_dev = f"""
The generated project had runtime errors that need to be fixed.

Runtime Error Details:
{runtime_fix_context}

Original Technical Design:
{state['technical_design']}

Please fix ALL the runtime errors mentioned above.
Make sure all imports are correct and all required packages are standard/available.
Avoid using pydantic BaseSettings — use python-dotenv os.getenv() instead.
"""
    elif state.get("qa_review"):
        input_to_dev = f"""
Previous code had issues. QA Review:
{state['qa_review']}

Original Technical Design:
{state['technical_design']}

Please fix all the issues mentioned.
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

    if memory_context.get("mode") in ["enhance", "resume"] and memory_context.get("existing_project_folder"):
        project_folder = memory_context["existing_project_folder"]
    else:
        project_name = generate_project_name(state["requirement"])
        project_folder = os.path.join("output", project_name)

    return {
        **state,
        "generated_code": code,
        "project_folder": project_folder,
        "runtime_fix_context": "",  # Clear after use
        "retry_count": state.get("retry_count", 0) + 1
    }

def qa_node(state: AgentState) -> AgentState:
    result = run_agent4(state["generated_code"])
    return {
        **state,
        "qa_status": result["status"],
        "qa_review": result["review"]
    }

def human_approval_node(state: AgentState) -> AgentState:
    print("\n" + "=" * 50)
    print("👤 HUMAN APPROVAL REQUIRED")
    print("=" * 50)

    if state["qa_status"] == "PASS":
        print("\nQA has PASSED. Please review the generated code.")
    else:
        print("\n⚠️ Max retries reached. QA did not fully pass. Please review carefully.")

    print(f"📁 Project folder: {state.get('project_folder', 'output/')}")
    print("\nDo you approve this implementation?")
    approval = input("Type 'yes' to approve or 'no' to reject: ")
    approved = approval.lower() == "yes"

    if approved:
        print("\n✅ Approved! Pipeline complete.")
    else:
        print("\n❌ Rejected. Stopping pipeline.")

    return {**state, "human_approved": approved}

def runtime_fixer_node(state: AgentState) -> AgentState:
    """Agent 5 runs after human approval to validate and fix runtime errors."""
    result = run_agent5(
        project_folder=state["project_folder"],
        generated_code=state["generated_code"]
    )
    return {
        **state,
        "runtime_fix_context": result.get("fix_context", ""),
        "runtime_retry_count": state.get("runtime_retry_count", 0) + 1
    }

# Routing logic
def route_after_qa(state: AgentState) -> str:
    if state["qa_status"] == "PASS":
        return "human_approval"
    elif state.get("retry_count", 0) >= 3:
        print("\n⚠️ Max retries reached. Moving to human approval anyway.")
        return "human_approval"
    else:
        print(f"\n🔄 QA Failed. Sending back to developer (Attempt {state.get('retry_count', 0) + 1})")
        return "developer"

def route_after_runtime_fix(state: AgentState) -> str:
    """Route after Agent 5 runs."""
    fix_context = state.get("runtime_fix_context", "")
    runtime_retries = state.get("runtime_retry_count", 0)

    if not fix_context:
        # No errors — done!
        return "done"
    elif runtime_retries >= 3:
        print("\n⚠️ Max runtime fix attempts reached. Please fix manually.")
        return "done"
    else:
        print(f"\n🔄 Runtime error found. Sending back to developer to fix (Attempt {runtime_retries})")
        return "developer"

# Build the graph
def build_pipeline():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("memory", memory_node)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("architect", architect_node)
    graph.add_node("developer", developer_node)
    graph.add_node("qa", qa_node)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("runtime_fixer", runtime_fixer_node)

    # Edges
    graph.set_entry_point("memory")
    graph.add_edge("memory", "orchestrator")
    graph.add_edge("orchestrator", "architect")
    graph.add_edge("architect", "developer")
    graph.add_edge("developer", "qa")
    graph.add_conditional_edges("qa", route_after_qa, {
        "developer": "developer",
        "human_approval": "human_approval"
    })
    # After human approval — only run runtime fixer if approved
    graph.add_conditional_edges("human_approval",
        lambda s: "runtime_fixer" if s["human_approved"] else "done",
        {
            "runtime_fixer": "runtime_fixer",
            "done": END
        }
    )
    graph.add_conditional_edges("runtime_fixer", route_after_runtime_fix, {
        "developer": "developer",
        "done": END
    })

    return graph.compile()

# Run the pipeline
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🚀 AGENTIC DEV PLATFORM")
    print("=" * 50)

    requirement = input("\nEnter your requirement: ")

    initial_state: AgentState = {
        "requirement": requirement,
        "memory_context": {},
        "project_brief": "",
        "technical_design": "",
        "generated_code": "",
        "qa_review": "",
        "qa_status": "",
        "retry_count": 0,
        "runtime_retry_count": 0,
        "human_approved": False,
        "project_folder": "",
        "runtime_fix_context": ""
    }

    pipeline = build_pipeline()
    final_state = pipeline.invoke(initial_state)

    # Save to memory after successful approval
    if final_state["human_approved"]:
        project_folder = final_state.get("project_folder", "")
        tech_stack = extract_tech_stack_from_requirements(project_folder)
        files_generated = list(final_state.get("memory_context", {}).get("existing_files", {}).keys())

        add_memory_entry(
            requirement=final_state["requirement"],
            project_name=os.path.basename(project_folder),
            project_folder=project_folder,
            tech_stack=tech_stack,
            files_generated=files_generated,
            qa_status=final_state["qa_status"]
        )
        print(f"\n💾 Run saved to memory.")

    print("\n" + "=" * 50)
    print("🏁 PIPELINE COMPLETE")
    print("=" * 50)
    if final_state["human_approved"]:
        print("✅ Code approved and ready to use!")
        print(f"📁 Find your project at: {final_state.get('project_folder', 'output/')}")
    else:
        print("❌ Code was not approved.")