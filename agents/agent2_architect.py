import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run_agent2(project_brief: str) -> str:
    print("\n🤖 Agent 2 (Architect) is creating technical design...\n")
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a senior software architect.

You have received this project brief:
{project_brief}

Your job is to produce a SIMPLE technical design with:
1. Technology stack (libraries and tools to use)
2. A SINGLE file structure - no complex folders or multiple files
3. Key functions needed in that single file
4. Step by step implementation plan
5. Any technical risks or considerations

IMPORTANT RULES:
- Design for a SINGLE Python file only
- Keep it simple and practical
- Do not over-engineer
- Only use libraries that are already installed: python-docx, reportlab
- This will be implemented by a developer in ONE file

Be specific and practical.
CRITICAL: Keep the design extremely simple.
Maximum 5 functions total. No batch processing. No images. No tables.
Just basic text conversion only.
This will be handed to a developer agent to implement."""
            }
        ]
    )
    
    result = response.content[0].text
    print("✅ Agent 2 Output:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    return result

if __name__ == "__main__":
    sample_brief = """
    Project Goal: Build a Word to PDF converter
    Inputs: .docx files
    Outputs: PDF files
    Core Features: Convert, preserve formatting, handle errors
    """
    run_agent2(sample_brief)