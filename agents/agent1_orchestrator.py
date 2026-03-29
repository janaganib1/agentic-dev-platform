import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run_agent1(requirement: str) -> str:
    print("\n🤖 Agent 1 (Orchestrator) is analyzing your requirement...\n")
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a software project orchestrator. 
                
A user has given you this requirement:
\"{requirement}\"

Your job is to produce a clear, structured project brief with:
1. Project goal (one sentence)
2. Inputs and outputs
3. Core features needed
4. Success criteria
5. Edge cases to handle

Be concise and precise. This will be handed to a technical architect next."""
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