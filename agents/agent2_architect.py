import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run_agent2(project_brief: str) -> str:
    print("\n🤖 Agent 2 (Architect) is creating technical design...\n")
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a senior software architect.

You have received this project brief:
{project_brief}

Your job is to produce a technical design with:

1. **Technology Stack** — libraries and tools to use (choose the best fit, not limited to any specific set)

2. **Project Structure** — multi-file layout, for example:
   - src/__init__.py
   - src/main.py (entry point)
   - src/config.py (configuration and env vars)
   - src/utils.py (helper functions)
   - src/models.py (data models if needed)
   - tests/test_main.py
   - requirements.txt
   - README.md

3. **Environment Variables & Input Parameters** — list ALL required:
   - Environment variables (API keys, secrets) — specify exact variable name and how to set it
   - Runtime parameters (e.g. zip code, file path) — specify how to pass at runtime
   - Example .env file content
   - Example run command

4. **Key Functions** — what each module does and main functions needed

5. **Implementation Plan** — step by step

6. **Technical Risks** — any considerations

IMPORTANT RULES:
- Design for a clean MULTI-FILE Python project
- Use the best libraries for the job
- Be specific about env vars and runtime params — the developer must include clear setup instructions in README.md
- Keep it practical and production-ready

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
    Project Goal: Given a zip code fetch hourly weather forecast using OpenWeatherMap API
    Inputs: zip code (runtime parameter)
    Outputs: formatted hourly forecast display
    Core Features: fetch forecast, display temperature, humidity, wind, rain chance
    """
    run_agent2(sample_brief)