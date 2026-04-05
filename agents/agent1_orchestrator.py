import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def run_agent1(requirement: str, memory_context: dict = None) -> str:
    print("\n🤖 Agent 1 (Orchestrator) is analyzing your requirement...\n")

    # Build memory section for the prompt
    memory_section = ""
    if memory_context and memory_context.get("mode") != "fresh":
        mode = memory_context["mode"]
        tech_stack = memory_context.get("tech_stack", [])
        existing_files = memory_context.get("existing_files", {})
        context_summary = memory_context.get("context_summary", "")

        memory_section = f"""
MEMORY CONTEXT:
Mode: {mode.upper()} — {"enhancing existing project" if mode == "enhance" else "resuming previous session"}
{context_summary}

Existing tech stack to REUSE: {', '.join(tech_stack) if tech_stack else 'None detected'}
Existing files available: {', '.join(existing_files.keys()) if existing_files else 'None'}

IMPORTANT:
- Do NOT redesign from scratch — build on top of the existing project
- Reuse the existing tech stack: {', '.join(tech_stack) if tech_stack else 'as previously used'}
- Identify only what needs to be ADDED or CHANGED
- Reference existing files where relevant
"""
    else:
        memory_section = "\nMEMORY CONTEXT: No past runs found — designing from scratch.\n"

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": f"""You are a software project orchestrator.

A user has given you this requirement:
"{requirement}"

{memory_section}

Your job is to produce a clear, structured project brief with:
1. Project goal (one sentence)
2. Inputs and outputs
3. Core features needed (new or changed only if enhancing)
4. Success criteria
5. Edge cases to handle
6. Tech stack recommendation (reuse existing if available)

Be concise and precise. Keep the scope MINIMAL for a first working version.
Focus only on the most essential features.
This will be handed to a technical architect next."""
            }
        ]
    )

    result = response.content[0].text
    print("✅ Agent 1 Output:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    return result


if __name__ == "__main__":
    requirement = input("\nEnter your requirement: ")
    run_agent1(requirement)