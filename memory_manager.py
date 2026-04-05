"""
memory_manager.py
Handles reading and writing to memory.json for the agentic dev platform.
Each entry stores a past run with requirement, project folder, tech stack, files, and status.
"""

import json
import os
from datetime import datetime


MEMORY_FILE = "memory.json"


def load_memory() -> list:
    """Load all past runs from memory.json. Returns empty list if file doesn't exist."""
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_memory(entries: list) -> None:
    """Save the full memory list back to memory.json."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def add_memory_entry(
    requirement: str,
    project_name: str,
    project_folder: str,
    tech_stack: list,
    files_generated: list,
    qa_status: str
) -> None:
    """Add a new completed run to memory."""
    entries = load_memory()

    # Check if same project folder already exists — update instead of duplicate
    for entry in entries:
        if entry.get("project_folder") == project_folder:
            entry["requirement"] = requirement
            entry["tech_stack"] = tech_stack
            entry["files_generated"] = files_generated
            entry["qa_status"] = qa_status
            entry["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_memory(entries)
            return

    # New entry
    entries.append({
        "requirement": requirement,
        "project_name": project_name,
        "project_folder": project_folder,
        "tech_stack": tech_stack,
        "files_generated": files_generated,
        "qa_status": qa_status,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_memory(entries)


def get_existing_project_files(project_folder: str) -> dict:
    """
    Scan an existing project folder and return all file contents.
    Returns dict: { "src/main.py": "<content>", ... }
    """
    file_contents = {}
    if not os.path.exists(project_folder):
        return file_contents

    for root, dirs, files in os.walk(project_folder):
        # Skip __pycache__ and venv folders
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.git']]
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, project_folder)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    file_contents[relative_path] = f.read()
            except (IOError, UnicodeDecodeError):
                pass

    return file_contents


def extract_tech_stack_from_requirements(project_folder: str) -> list:
    """Extract tech stack from requirements.txt if it exists."""
    req_path = os.path.join(project_folder, "requirements.txt")
    if not os.path.exists(req_path):
        return []
    try:
        with open(req_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [line.strip().split("==")[0].split(">=")[0] for line in lines if line.strip() and not line.startswith("#")]
    except IOError:
        return []