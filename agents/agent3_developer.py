"""
agent3_developer.py
Developer Agent that:
1. Implements ANY requirement as a complete multi-file project
2. Follows strict code quality rules to ensure first-run success
3. Never cuts off files mid-function
4. Produces exactly what Agent 2 designed — no extras
5. (RouteOne mode) Generates Java/Spring Boot code written directly into C:\Local_Git\routeone
6. (Personal mode) Generates Python code written to output/ folder as before
"""

import os
import re
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# ─── File Parsing ─────────────────────────────────────────────────────────────

def parse_multi_file_response(response_text: str) -> dict:
    """Parse ### FILE: blocks from agent response into {path: content} dict."""
    files = {}
    parts = re.split(r'###\s*FILE:\s*', response_text)
    for part in parts[1:]:
        lines = part.strip().splitlines()
        if not lines:
            continue
        file_path = lines[0].strip()
        file_content = "\n".join(lines[1:]).strip()

        if file_content.startswith("```"):
            file_content = file_content.split("\n", 1)[1] if "\n" in file_content else ""
        if file_content.endswith("```"):
            file_content = file_content.rsplit("```", 1)[0]

        files[file_path] = file_content.strip()

    return files


# ─── File Writers ─────────────────────────────────────────────────────────────

def save_project_files(project_name: str, files: dict) -> str:
    """
    Personal mode: Save all generated files under output/<project_name>/
    Unchanged from original behaviour.
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


def save_routeone_files(files: dict) -> list[str]:
    """
    RouteOne mode: Write generated files directly into the local RouteOne repo.
    File paths from the agent are expected to be relative to REPO_PATH
    (e.g. partner-interfaces/routeone-partner/routeone-service/src/main/java/
          com/routeone/partner/controller/MyController.java)
    Returns list of written file paths for use by git_manager.
    """
    repo_path = os.getenv("REPO_PATH", "").strip()
    if not repo_path:
        print("⚠️  REPO_PATH not set — cannot write to RouteOne repo.")
        return []

    if not os.path.isdir(repo_path):
        print(f"⚠️  REPO_PATH does not exist: {repo_path}")
        return []

    written_paths = []
    for relative_path, content in files.items():
        # Normalise path separators (agent may return forward slashes on Windows)
        relative_path = relative_path.replace("/", os.sep).replace("\\", os.sep)
        full_path = os.path.join(repo_path, relative_path)

        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"   📄 Written to repo: {relative_path}")
            written_paths.append(full_path)
        except Exception as e:
            print(f"   ⚠️  Could not write {relative_path}: {e}")

    return written_paths


# ─── Helpers ──────────────────────────────────────────────────────────────────

def generate_project_name(text: str) -> str:
    """Generate clean project folder name from requirement text."""
    skip = {
        'given', 'using', 'with', 'from', 'that', 'this', 'will', 'have',
        'build', 'create', 'make', 'develop', 'simple', 'basic', 'just',
        'only', 'some', 'into', 'should', 'which', 'where', 'when', 'then'
    }
    words = re.sub(r'[^a-zA-Z0-9\s]', '', text[:80])
    words = [w.lower() for w in words.split() if len(w) >= 3 and w.lower() not in skip][:4]
    return '_'.join(words) if words else 'generated_project'


# ─── Prompts ──────────────────────────────────────────────────────────────────

PYTHON_DEVELOPER_PROMPT = """You are a senior Python developer.
You implement ANY kind of Python project — CLI tools, APIs, file processors,
web scrapers, data pipelines, utilities, automation scripts, and more.

You have received this technical design:
{technical_design}

════════════════════════════════════════
IMPLEMENTATION RULES — ALWAYS FOLLOW
════════════════════════════════════════

TECHNOLOGY RULES:
❌ NEVER use: win32com, pywin32, AppKit, or ANY OS-automation library
❌ NEVER use: docx2pdf (requires MS Word installed — use python-docx + reportlab instead)
❌ NEVER use: pydantic BaseSettings or pydantic-settings (use os.getenv() instead)
❌ NEVER use: click, typer, fire (use argparse)
❌ NEVER use: httpx, aiohttp (use requests)
❌ NEVER use: async/await unless design explicitly requires it
✅ ALWAYS use: os.getenv() + python-dotenv for ALL configuration
✅ ALWAYS use: argparse for CLI interfaces
✅ ALWAYS use: requests for HTTP calls
✅ ALWAYS use: the exact libraries specified in the technical design

IMPORT RULES:
✅ Follow the import hierarchy from the technical design EXACTLY
✅ src/__init__.py must be EMPTY — no imports
✅ tests/__init__.py must be EMPTY — no imports
✅ config.py must have NO project imports — only standard library + dotenv
✅ Use relative imports (from .config import ...) inside src/ package
❌ NEVER create circular imports — if A imports B, B must not import A

CODE COMPLETENESS RULES:
✅ Every function must be COMPLETE — no pass, no TODO, no ... placeholders
✅ Every file must be COMPLETE — never cut off mid-function or mid-class
✅ If running low on space — simplify the code, NEVER truncate it
✅ main.py MUST have if __name__ == "__main__": block
✅ requirements.txt must list EVERY non-standard library that is imported
✅ .env.example must list EVERY environment variable used in code

TEST RULES:
✅ test_main.py must be COMPLETE and RUNNABLE
✅ Tests must be simple — happy path only
✅ Maximum 30 lines per test file
✅ Use pytest style (def test_xxx():)
✅ Mock external calls (API, file system) where needed
❌ NEVER write incomplete test functions
❌ NEVER write tests that require real API keys or real files to pass

SCOPE RULES:
✅ Implement EXACTLY what the design says — nothing more
❌ NEVER add caching, retry logic, rate limiting, or auth unless in design
❌ NEVER add extra validation beyond what is needed to run
❌ NEVER add logging configuration unless design specifies it
❌ NEVER add security hardening unless design specifies it

════════════════════════════════════════
OUTPUT FORMAT — USE EXACTLY THIS FORMAT
════════════════════════════════════════

Use EXACTLY this format for each file — no exceptions:

### FILE: src/__init__.py
### FILE: src/config.py
### FILE: src/main.py
### FILE: tests/__init__.py
### FILE: tests/test_main.py
### FILE: requirements.txt
### FILE: README.md
### FILE: .env.example

Rules for each file:
- Start each with ### FILE: path/to/file
- Write complete file content immediately after
- No explanations between files
- Return ONLY the files — no text before or after"""


ROUTEONE_DEVELOPER_PROMPT = """You are a senior Java developer specialising in Spring Boot microservices.
You are working on the RouteOne Partner API (PAPI) monorepo.

You have received this technical change plan from the Architect:
{technical_design}

════════════════════════════════════════
ROUTEONE JAVA IMPLEMENTATION RULES
════════════════════════════════════════

TECHNOLOGY RULES:
✅ Java 17, Spring Boot (match existing service version — SB2 or SB4 as per design)
✅ Maven only — NEVER Gradle
✅ Spring Data JPA for all new database access (NO new stored procedures)
✅ WebClient for all inter-service HTTP calls — NEVER RestTemplate or Feign
✅ Constructor injection ALWAYS — NEVER @Autowired on fields
✅ JSR-380 annotations (@NotNull, @Valid, @Size) for input validation
✅ Swagger/OpenAPI 3.0 annotations on ALL new/modified public endpoints
✅ JUnit 5 + Mockito + MockMvc for tests — extend AbstractControllerTest for controllers
✅ LaunchDarkly feature flags for ALL production changes (unless bug fix)

CODE QUALITY RULES:
✅ Every file must be COMPLETE — no TODO, no placeholder, no truncated methods
✅ Follow existing package structure exactly as shown in the codebase context
✅ Use existing Translator pattern for DTO conversion between API layers
✅ Use existing error codes from RouteOneErrorCode — create new ones only if none fit
✅ NO Lombok on JPA entity classes — use explicit getters/setters
✅ Extract magic strings/numbers to named constants
✅ Use Optional<T> for potentially null returns

TEST RULES:
✅ Minimum 90% branch coverage for all new/modified code
✅ Test ALL branches: happy path, null inputs, validation failures, feature flag ON and OFF
✅ Controller tests: extend AbstractControllerTest, use @WebMvcTest + MockMvc
✅ Service tests: use @ExtendWith(MockitoExtension.class) + @InjectMocks
✅ Every if/else branch needs its own test method
✅ Use @DisplayName with descriptive names on all test classes and methods
✅ Use test data from -makers module where available

SCOPE RULES:
✅ Implement EXACTLY what the design says — nothing more
✅ ONLY touch files mentioned in the Architect's change plan
✅ Make MINIMAL changes — do not refactor unrelated code
✅ Do NOT reorganise imports, reformat whitespace, or rename anything not in scope
✅ If a feature flag name is in the Jira story — use it exactly
✅ Update BOTH -service and -service-sb4 modules if both exist (as per design)

════════════════════════════════════════
OUTPUT FORMAT — USE EXACTLY THIS FORMAT
════════════════════════════════════════

Use EXACTLY this format for each file — no exceptions:

### FILE: <path relative to repo root>

Example paths:
### FILE: partner-interfaces/routeone-partner/routeone-service/src/main/java/com/routeone/partner/controller/RouteOneDealDataController.java
### FILE: partner-interfaces/routeone-partner/routeone-api/src/main/java/com/routeone/partner/api/dealdata/UpdateDealRequest.java
### FILE: partner-interfaces/routeone-partner/routeone-service/src/test/java/com/routeone/partner/controller/RouteOneDealDataControllerTest.java

Rules for each file:
- Start each with ### FILE: <exact path relative to repo root>
- Write COMPLETE file content immediately after (full Java file including package declaration and all imports)
- No explanations between files
- Return ONLY the files — no text before or after
- Paths must match the existing repo structure shown in the codebase context above"""


# ─── Core Agent ──────────────────────────────────────────────────────────────

def run_agent3(technical_design: str, requirement: str = "", project_folder: str = "") -> str:
    """
    Run the developer agent to generate a complete project.

    Personal mode: generates Python, saves to output/<project_name>/
    RouteOne mode:  generates Java/Spring Boot, writes directly to REPO_PATH

    Args:
        technical_design: Technical design / change plan from Agent 2
        requirement:      Original user requirement (used for folder naming in personal mode)
        project_folder:   Explicit project folder override (personal mode)
    """
    repo_mode = os.getenv("REPO_MODE", "personal").lower()
    is_routeone = repo_mode == "routeone"

    print("\n🤖 Agent 3 (Developer) is writing the code...\n")
    if is_routeone:
        print("   🏢 Mode: RouteOne — generating Java/Spring Boot code into local repo\n")
    else:
        print("   🧪 Mode: Personal — generating Python project into output/\n")

    # Select prompt based on mode
    if is_routeone:
        prompt = ROUTEONE_DEVELOPER_PROMPT.format(technical_design=technical_design)
    else:
        prompt = PYTHON_DEVELOPER_PROMPT.format(technical_design=technical_design)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result = response.content[0].text
    files = parse_multi_file_response(result)

    if not files:
        print("⚠️  Could not parse multi-file response.")
        if is_routeone:
            # Save raw output to a fallback file so nothing is lost
            fallback = os.path.join(os.getcwd(), "routeone_agent_output.txt")
            with open(fallback, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"   Raw output saved to: {fallback}")
        else:
            naming_source = requirement if requirement.strip() else technical_design
            project_name = generate_project_name(naming_source)
            output_path = f"output/{project_name}.py"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"✅ Saved to: {output_path}")
        return result

    # ── Write files ───────────────────────────────────────────────────────────
    if is_routeone:
        written_paths = save_routeone_files(files)
        print("\n✅ Agent 3 Output:")
        print("-" * 50)
        print(f"🏢 Files written to repo: {len(written_paths)}")
        for p in written_paths:
            repo_path = os.getenv("REPO_PATH", "")
            rel = os.path.relpath(p, repo_path) if repo_path else p
            print(f"   📄 {rel}")
        print("-" * 50)
    else:
        # Personal mode — existing behaviour unchanged
        if project_folder:
            project_name = os.path.basename(project_folder)
        else:
            naming_source = requirement if requirement.strip() else technical_design
            project_name = generate_project_name(naming_source)

        project_root = save_project_files(project_name, files)
        print("\n✅ Agent 3 Output:")
        print("-" * 50)
        print(f"📁 Project folder: {project_root}")
        print(f"📦 Files generated: {len(files)}")
        print("-" * 50)

    combined = "\n\n".join(
        f"# === {path} ===\n{content}" for path, content in files.items()
    )
    return combined


if __name__ == "__main__":
    sample_design = """
    ## Goal
    Read a .docx file and convert text to PDF.

    ## Technology Stack
    - python-docx: read Word files
    - reportlab: generate PDF

    ## Files
    src/__init__.py, src/main.py, src/config.py, src/converter.py
    tests/__init__.py, tests/test_main.py
    requirements.txt, README.md, .env.example

    ## Run Command
    py -m src.main input.docx
    """
    run_agent3(sample_design, requirement="convert word document to pdf")