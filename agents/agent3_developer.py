import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run_agent3(technical_design: str) -> str:
    print("\n🤖 Agent 3 (Developer) is writing the code...\n")
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8096,
        messages=[
            {
                "role": "user",
                "content": f"""You are a senior Python developer.

You have received this technical design:
{technical_design}

Your job is to implement the solution in a SINGLE Python file:
1. Write complete, working Python code in ONE file only
2. Use python-docx for reading Word files
3. Use reportlab for generating PDF files
4. Include proper error handling
5. Include comments explaining the code
6. Make it ready to run immediately
7. DO NOT create multiple files or complex folder structures
8. Keep it simple - one file, all functions included
9. Write main() function FIRST before other functions
10. Make sure the code is complete - do not cut off
11. If running out of space, skip comments and docstrings
12. The if __name__ == "__main__": block is mandatory

Return ONLY the code. No explanations outside the code.
Use comments inside the code to explain."""
            }
        ]
    )
    
    result = response.content[0].text
    
    # Strip markdown code fences if present
    if result.startswith("```"):
        result = result.split("\n", 1)[1]
    if result.endswith("```"):
        result = result.rsplit("```", 1)[0]
    
   # Generate filename from the technical design (first 5 words, sanitized)
    first_line = technical_design.strip().split('\n')[0]
    words = ''.join(c if c.isalnum() or c == ' ' else '' for c in first_line)
    filename = '_'.join(words.lower().split()[:5]) + '.py'
    output_path = f"output/{filename}"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)
    
    print("✅ Agent 3 Output:")
    print("-" * 50)
    print(f"Code generated and saved to: {output_path}")
    print("-" * 50)
    return result

if __name__ == "__main__":
    sample_design = """
    Technology Stack: python-docx, reportlab
    
    File Structure:
    - word_to_pdf.py (main converter file)
    
    Key Functions:
    - convert_word_to_pdf(input_path, output_path)
    - validate_input_file(file_path)
    - handle_errors(exception)
    
    Implementation:
    - Read .docx file
    - Extract text and basic formatting
    - Generate PDF using reportlab
    - Handle common errors
    """
    run_agent3(sample_design)