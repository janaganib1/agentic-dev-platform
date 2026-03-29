import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run_agent4(generated_code: str) -> dict:
    print("\n🤖 Agent 4 (QA Tester) is reviewing the code...\n")
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a senior QA engineer and code reviewer.

You have received this generated code to review:
{generated_code}

Your job is to:
1. Review the code for bugs and issues
2. Check error handling is proper
3. Check edge cases are handled
4. Verify the logic is correct
5. Check if imports are correct

Respond in this exact format:
STATUS: PASS or FAIL
ISSUES: (list any issues found, or "None" if no issues)
SUGGESTIONS: (list improvements needed)
SUMMARY: (one sentence summary)"""
            }
        ]
    )
    
    result = response.content[0].text
    
    # Determine pass or fail
    status = "PASS" if "STATUS: PASS" in result else "FAIL"
    
    print("✅ Agent 4 Output:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    print(f"\n🎯 Final Status: {status}")
    
    return {
        "status": status,
        "review": result
    }

if __name__ == "__main__":
    # Read the generated code from output folder
    code_path = "output/word_to_pdf.py"
    
    if os.path.exists(code_path):
        with open(code_path, "r") as f:
            generated_code = f.read()
        run_agent4(generated_code)
    else:
        print("❌ No generated code found. Run agent3_developer.py first.")