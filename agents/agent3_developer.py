import os
import re
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def parse_multi_file_response(response_text: str) -> dict:
    """
    Parses the agent response and extracts multiple files.
    Expected format:
        ### FILE: path/to/file.py
        <code here>
        ### FILE: path/to/another.py
        <code here>
    Returns a dict: { "path/to/file.py": "<content>", ... }
    """
    files = {}
    parts = re.split(r'###\s*FILE:\s*', response_text)
    for part in parts[1:]:  # Skip first empty split
        lines = part.strip().splitlines()
        if not lines:
            continue
        file_path = lines[0].strip()
        file_content = "\n".join(lines[1:]).strip()

        # Strip markdown code fences if present
        if file_content.startswith("```"):
            file_content = file_content.split("\n", 1)[1] if "\n" in file_content else ""
        if file_content.endswith("```"):
            file_content = file_content.rsplit("```", 1)[0]

        files[file_path] = file_content.strip()

    return files


def save_project_files(project_name: str, files: dict) -> str:
    """
    Saves all generated files under output/<project_name>/.
    Creates subdirectories as needed.
    Returns the root project output path.
    """
    project_root = os.path.join("output", project_name)
    os.makedirs(project_root, exist_ok=True)

    for relative_path, content in files.items():
        full_path = os.path.join(project_root, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   📄 Created: {full_path}")

    return project_root


def generate_project_name(text: str) -> str:
    """Generates a clean project folder name from the requirement."""
    # Use first 80 chars only, keep words 3+ chars, max 4 words
    words = re.sub(r'[^a-zA-Z0-9\s]', '', text[:80])
    # Skip common filler words
    skip = {'given', 'using', 'with', 'from', 'that', 'this', 'will', 'have', 'build', 'create', 'make'}
    words = [w.lower() for w in words.split() if len(w) >= 3 and w.lower() not in skip][:4]
    return '_'.join(words) if words else 'generated_project'


def run_agent3(technical_design: str, requirement: str = "") -> str:
    """
    Run the developer agent to generate a multi-file Python project.

    Args:
        technical_design: The technical design from Agent 2
        requirement: The original user requirement (used for project folder naming)
    """
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

Your job is to implement the solution as a COMPLETE MULTI-FILE Python project.

Rules:
1. Split code into logical modules (e.g. main.py, utils.py, config.py, models.py)
2. Include a tests/ folder with at least one test file
3. Include a requirements.txt listing all dependencies
4. Include a README.md with:
   - Project description
   - ALL required environment variables with exact names and how to set them (e.g. in .env file)
   - ALL runtime parameters with example run commands
   - Example .env file content
   - Setup steps
5. Include __init__.py in every package folder
6. Use proper error handling throughout
7. Add comments explaining key logic
8. Every file must be complete and ready to run

Output format — use EXACTLY this format for each file, no exceptions:

### FILE: src/__init__.py
<file content here>

### FILE: src/main.py
<file content here>

### FILE: src/utils.py
<file content here>

### FILE: tests/__init__.py
<file content here>

### FILE: tests/test_main.py
<file content here>

### FILE: requirements.txt
<file content here>

### FILE: README.md
<file content here>

Return ONLY the files in the format above. No explanations outside the files."""
            }
        ]
    )

    result = response.content[0].text

    # Parse all files from the response
    files = parse_multi_file_response(result)

    # Use requirement for project name if provided, fallback to technical design
    naming_source = requirement if requirement.strip() else technical_design
    project_name = generate_project_name(naming_source)

    if not files:
        # Fallback: save as single file if parsing fails
        print("⚠️  Could not parse multi-file response. Saving as single file.")
        output_path = f"output/{project_name}.py"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"✅ Saved to: {output_path}")
        return result

    # Save all files under a project folder
    project_root = save_project_files(project_name, files)

    print("\n✅ Agent 3 Output:")
    print("-" * 50)
    print(f"📁 Project folder: {project_root}")
    print(f"📦 Files generated: {len(files)}")
    print("-" * 50)

    # Return all file contents combined (for QA agent to review)
    combined = "\n\n".join(
        f"# === {path} ===\n{content}" for path, content in files.items()
    )
    return combined


if __name__ == "__main__":
    sample_design = """
    Technology Stack: requests, python-dotenv

    Project Structure:
    - src/main.py (entry point)
    - src/weather.py (API logic)
    - src/utils.py (helpers)
    - tests/test_weather.py (unit tests)
    - requirements.txt
    - README.md

    Environment Variables:
    - OPENWEATHER_API_KEY: your OpenWeatherMap API key

    Runtime Parameters:
    - zip_code: passed as command line argument

    Key Functions:
    - get_forecast(zip_code)
    - format_output(data)
    """
    run_agent3(sample_design, requirement="fetch hourly weather forecast by zip code")