"""
agent05_story_splitter.py
Story Splitter Agent that:
1. Analyzes ANY requirement and classifies it as SIMPLE, MEDIUM, or EPIC
2. Breaks it into focused, sequential, runnable stories
3. Each story follows a consistent functional layer pattern
4. Returns ordered list of stories for the pipeline to execute
"""

import os
import re
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def classify_and_split(requirement: str) -> dict:
    """
    Use Claude to classify the requirement and split into stories.
    Returns dict with complexity, stories list, and project name.
    """
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""You are an agile story splitter for a code generation platform.
You handle ANY kind of software requirement — CLI tools, APIs, data processors,
file converters, web scrapers, automation scripts, games, utilities, and more.

A user has submitted this requirement:
"{requirement}"

YOUR JOB:
1. Classify complexity: SIMPLE, MEDIUM, or EPIC
2. Split into focused, sequential, independently runnable stories
3. Each story builds on the previous one
4. Each story must be completable in a single focused coding session

CLASSIFICATION RULES:
- SIMPLE: Single function or script, 1-2 stories max
  Examples: fetch an API, convert a file, generate a report, rename files
- MEDIUM: 2-4 stories, needs a few cooperating modules
  Examples: CLI app, data pipeline, scraper with output, REST client
- EPIC: 5-10 stories, full application with multiple subsystems
  Examples: REST API server, full CRUD app, multi-service integration

STORY LAYERING — always follow this order regardless of domain:
  Story 1 → Core logic layer: the engine that does the main work
  Story 2 → Input/output layer: how data enters and exits
  Story 3 → Interface layer: CLI, API endpoint, or UI
  Story 4 → Enhancement layer: formatting, filtering, config (if needed)
  Story 5 → Integration layer: external services, databases (if needed)

STORY RULES:
- Each story must produce runnable code when complete
- Each story focuses on ONE functional layer only
- Story requirement must be ONE clear, specific coding instruction
- Acceptance criteria must be concrete and immediately testable
- NEVER add validation, security hardening, retry logic, caching,
  rate limiting, authentication, or performance optimization
  UNLESS the user explicitly asked for them
- NEVER split a SIMPLE requirement into more than 2 stories
- Keep story titles short (3-5 words max)

GENERIC ACCEPTANCE CRITERIA PATTERNS (use these as templates):
- "Running py -m src.main <args> produces expected output"
- "Core function returns correct result for valid input"
- "Output file is created in correct location"
- "API response is parsed and displayed correctly"
- "CLI accepts required arguments and runs without error"

Respond in EXACTLY this JSON format, nothing else:

{{
  "complexity": "SIMPLE" | "MEDIUM" | "EPIC",
  "project_name": "<snake_case_4_words_max>",
  "project_summary": "<one sentence describing full project>",
  "total_stories": <number>,
  "stories": [
    {{
      "story_number": 1,
      "title": "<short 3-5 word title>",
      "requirement": "<single sentence coding instruction for this story only>",
      "layer": "core" | "io" | "interface" | "enhancement" | "integration",
      "depends_on": [],
      "acceptance_criteria": ["<concrete testable criteria>"],
      "complexity": "simple" | "medium"
    }}
  ]
}}

Return ONLY the JSON. No explanation outside the JSON."""
            }
        ]
    )

    result_text = response.content[0].text.strip()
    result_text = re.sub(r'^```json\s*', '', result_text)
    result_text = re.sub(r'\s*```$', '', result_text)

    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {
            "complexity": "SIMPLE",
            "project_name": _generate_project_name(requirement),
            "project_summary": requirement,
            "total_stories": 1,
            "stories": [
                {
                    "story_number": 1,
                    "title": "Full implementation",
                    "requirement": requirement,
                    "layer": "core",
                    "depends_on": [],
                    "acceptance_criteria": ["Requirement is fully implemented and runs"],
                    "complexity": "simple"
                }
            ]
        }


def _generate_project_name(text: str) -> str:
    """Generate clean project name from text."""
    skip = {
        'given', 'using', 'with', 'from', 'that', 'this', 'will', 'have',
        'build', 'create', 'make', 'develop', 'simple', 'basic', 'just',
        'only', 'some', 'into', 'should', 'which', 'where', 'when', 'then'
    }
    words = re.sub(r'[^a-zA-Z0-9\s]', '', text[:80])
    words = [w.lower() for w in words.split() if len(w) >= 3 and w.lower() not in skip][:4]
    return '_'.join(words) if words else 'generated_project'


def print_story_plan(split_result: dict) -> None:
    """Print the story plan to the console."""
    complexity = split_result["complexity"]
    stories = split_result["stories"]

    emoji = {"SIMPLE": "🟢", "MEDIUM": "🟡", "EPIC": "🔴"}.get(complexity, "⚪")

    print(f"\n{'=' * 50}")
    print(f"📋 STORY PLAN — {emoji} {complexity}")
    print(f"{'=' * 50}")
    print(f"Project : {split_result['project_name']}")
    print(f"Summary : {split_result['project_summary']}")
    print(f"Stories : {len(stories)}")
    print()

    for story in stories:
        layer = story.get('layer', '').upper()
        print(f"  Story {story['story_number']} [{layer}]: {story['title']}")
        req = story['requirement']
        print(f"    → {req[:90]}{'...' if len(req) > 90 else ''}")
        for c in story['acceptance_criteria'][:2]:
            print(f"    ✓ {c}")
        print()

    print(f"{'=' * 50}")
    print(f"🚀 Starting automated execution of {len(stories)} story/stories...")
    print(f"{'=' * 50}\n")


def run_agent05(requirement: str) -> dict:
    """
    Main entry point for the Story Splitter agent.
    Returns the full split result with stories list.
    """
    print("\n📋 Agent 0.5 (Story Splitter) is analyzing requirement...\n")
    split_result = classify_and_split(requirement)
    print_story_plan(split_result)
    return split_result


if __name__ == "__main__":
    req = input("\nEnter your requirement: ")
    result = run_agent05(req)
    print(f"\nComplexity : {result['complexity']}")
    print(f"Stories    : {result['total_stories']}")
    for s in result['stories']:
        print(f"  {s['story_number']}. [{s.get('layer','').upper()}] {s['title']}")