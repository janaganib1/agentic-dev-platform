import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

from agents.agent1_orchestrator import run_agent1
from agents.agent2_architect import run_agent2
from agents.agent3_developer import run_agent3
from agents.agent4_qa import run_agent4

load_dotenv()

# Define the state that flows between agents
class AgentState(TypedDict):
    requirement: str
    project_brief: str
    technical_design: str
    generated_code: str
    qa_review: str
    qa_status: str
    retry_count: int
    human_approved: bool

# Agent node functions
def orchestrator_node(state: AgentState) -> AgentState:
    brief = run_agent1(state["requirement"])
    return {**state, "project_brief": brief}

def architect_node(state: AgentState) -> AgentState:
    design = run_agent2(state["project_brief"])
    return {**state, "technical_design": design}

def developer_node(state: AgentState) -> AgentState:
    # If QA failed, pass the review feedback to developer
    if state.get("qa_review"):
        input_to_dev = f"""
Previous code had issues. QA Review:
{state['qa_review']}

Original Technical Design:
{state['technical_design']}

Please fix all the issues mentioned.
"""
    else:
        input_to_dev = state["technical_design"]
    
    code = run_agent3(input_to_dev)
    return {**state, "generated_code": code, "retry_count": state.get("retry_count", 0) + 1}

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
    print("\nQA has PASSED. Please review the generated code.")
    print(f"Code saved at: output/word_to_pdf.py")
    print("\nDo you approve this implementation?")
    approval = input("Type 'yes' to approve or 'no' to reject: ")
    approved = approval.lower() == "yes"
    if approved:
        print("\n✅ Approved! Pipeline complete.")
    else:
        print("\n❌ Rejected. Stopping pipeline.")
    return {**state, "human_approved": approved}

# Routing logic
def route_after_qa(state: AgentState) -> str:
    if state["qa_status"] == "PASS":
        return "human_approval"
    elif state.get("retry_count", 0) >= 2:
        print("\n⚠️ Max retries reached. Moving to human approval anyway.")
        return "human_approval"
    else:
        print(f"\n🔄 QA Failed. Sending back to developer (Attempt {state.get('retry_count', 0) + 1})")
        return "developer"

# Build the graph
def build_pipeline():
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("architect", architect_node)
    graph.add_node("developer", developer_node)
    graph.add_node("qa", qa_node)
    graph.add_node("human_approval", human_approval_node)
    
    # Add edges
    graph.set_entry_point("orchestrator")
    graph.add_edge("orchestrator", "architect")
    graph.add_edge("architect", "developer")
    graph.add_edge("developer", "qa")
    graph.add_conditional_edges("qa", route_after_qa, {
        "developer": "developer",
        "human_approval": "human_approval"
    })
    graph.add_edge("human_approval", END)
    
    return graph.compile()

# Run the pipeline
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🚀 AGENTIC DEV PLATFORM")
    print("=" * 50)
    
    requirement = input("\nEnter your requirement: ")
    
    initial_state: AgentState = {
        "requirement": requirement,
        "project_brief": "",
        "technical_design": "",
        "generated_code": "",
        "qa_review": "",
        "qa_status": "",
        "retry_count": 0,
        "human_approved": False
    }
    
    pipeline = build_pipeline()
    final_state = pipeline.invoke(initial_state)
    
    print("\n" + "=" * 50)
    print("🏁 PIPELINE COMPLETE")
    print("=" * 50)
    if final_state["human_approved"]:
        print("✅ Code approved and ready to use!")
        print("📁 Find your code at: output/word_to_pdf.py")
    else:
        print("❌ Code was not approved.")