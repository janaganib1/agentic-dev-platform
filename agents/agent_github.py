import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO  = os.getenv("GITHUB_REPO")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

BASE_URL = f"https://api.github.com/repos/{GITHUB_REPO}"


def get_default_branch_sha() -> str:
    """Get the SHA of the latest commit on the default branch (main)."""
    response = requests.get(f"{BASE_URL}/git/ref/heads/main", headers=HEADERS)
    response.raise_for_status()
    return response.json()["object"]["sha"]


def create_branch(branch_name: str, sha: str) -> bool:
    """Create a new feature branch from the given SHA."""
    payload = {
        "ref": f"refs/heads/{branch_name}",
        "sha": sha
    }
    response = requests.post(f"{BASE_URL}/git/refs", json=payload, headers=HEADERS)
    if response.status_code == 422:
        print(f"⚠️  Branch '{branch_name}' already exists — using existing branch.")
        return True
    response.raise_for_status()
    print(f"✅ Branch created: {branch_name}")
    return True


def push_file(branch_name: str, file_path: str, content: str, commit_message: str) -> bool:
    """Push a single file to the given branch."""
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    # Check if file already exists (needed for update vs create)
    sha = None
    check = requests.get(
        f"{BASE_URL}/contents/{file_path}",
        headers=HEADERS,
        params={"ref": branch_name}
    )
    if check.status_code == 200:
        sha = check.json().get("sha")

    payload = {
        "message": commit_message,
        "content": encoded,
        "branch": branch_name
    }
    if sha:
        payload["sha"] = sha

    response = requests.put(
        f"{BASE_URL}/contents/{file_path}",
        json=payload,
        headers=HEADERS
    )
    response.raise_for_status()
    return True


def push_folder_to_branch(branch_name: str, local_folder: str, ticket_id: str) -> list:
    """Walk a local folder and push all files to the GitHub branch."""
    pushed_files = []

    for root, dirs, files in os.walk(local_folder):
        # Skip __pycache__ and .env files
        dirs[:] = [d for d in dirs if d not in ["__pycache__", ".git", "venv"]]

        for filename in files:
            if filename.endswith(".pyc") or filename == ".env":
                continue

            local_path = os.path.join(root, filename)

            # Build relative path for GitHub
            relative_path = os.path.relpath(local_path, local_folder)
            github_path = f"{ticket_id}/{relative_path.replace(os.sep, '/')}"

            try:
                with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                push_file(
                    branch_name=branch_name,
                    file_path=github_path,
                    content=content,
                    commit_message=f"feat({ticket_id}): add {filename}"
                )
                pushed_files.append(github_path)
                print(f"  📄 Pushed: {github_path}")

            except Exception as e:
                print(f"  ⚠️  Skipped {filename}: {e}")

    return pushed_files


def run_github_agent(ticket_id: str, local_folder: str) -> dict:
    """Main entry — create branch and push all generated code."""
    print(f"\n{'='*50}")
    print(f"🐙 GitHub Agent — pushing {ticket_id}")
    print(f"{'='*50}")

    branch_name = f"feature/{ticket_id.lower()}"

    try:
        # Step 1: Get main branch SHA
        sha = get_default_branch_sha()

        # Step 2: Create feature branch
        create_branch(branch_name, sha)

        # Step 3: Push all files
        print(f"\n📦 Pushing files from: {local_folder}")
        pushed_files = push_folder_to_branch(branch_name, local_folder, ticket_id)

        print(f"\n✅ GitHub push complete!")
        print(f"🔗 Branch: https://github.com/{GITHUB_REPO}/tree/{branch_name}")
        print(f"📁 Files pushed: {len(pushed_files)}")

        return {
            "success": True,
            "branch": branch_name,
            "files_pushed": pushed_files,
            "branch_url": f"https://github.com/{GITHUB_REPO}/tree/{branch_name}"
        }

    except Exception as e:
        print(f"\n❌ GitHub agent failed: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python agents/agent_github.py <ticket_id> <local_folder>")
        print("Example: python agents/agent_github.py AG-1 output/weather_application_zip_code")
        sys.exit(1)

    ticket_id    = sys.argv[1]
    local_folder = sys.argv[2]
    run_github_agent(ticket_id, local_folder)
