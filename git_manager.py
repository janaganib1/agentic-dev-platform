import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

# ─── Config from .env ────────────────────────────────────────────────────────

REPO_MODE   = os.getenv("REPO_MODE", "personal").lower()   # personal | routeone
REPO_PATH   = os.getenv("REPO_PATH", "")                   # C:\Local_Git\routeone
BASE_BRANCH = os.getenv("BASE_BRANCH", "main")             # main | QA
AUTO_PUSH   = os.getenv("AUTO_PUSH", "false").lower() == "true"  # false = local commit only


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _run_git(command: list, cwd: str) -> tuple:
    """
    Run a git command in the given directory.
    Returns (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)


def _branch_exists_locally(branch_name: str, cwd: str) -> bool:
    """Check if a branch already exists locally."""
    success, output = _run_git(
        ["git", "branch", "--list", branch_name],
        cwd=cwd
    )
    return success and branch_name in output


# ─── Main Functions ───────────────────────────────────────────────────────────

def prepare_branch(ticket_id: str) -> dict:
    """
    Prepares the feature branch before the Architect agent runs.

    Personal mode:
      - No local repo to manage — output goes to output/ folder
      - Nothing to do here, returns success immediately

    RouteOne mode:
      - If branch feature/R1OD-XXX exists locally → switch to it
      - If not → checkout BASE_BRANCH, pull latest, create new branch
    """
    branch_name = f"feature/{ticket_id.lower()}"

    print(f"\n{'=' * 50}")
    print(f"🌿 Git Manager — preparing branch for {ticket_id}")
    print(f"{'=' * 50}")
    print(f"   Mode        : {REPO_MODE}")
    print(f"   Base branch : {BASE_BRANCH}")
    print(f"   Branch      : {branch_name}")
    print(f"   Auto push   : {'enabled' if AUTO_PUSH else 'disabled (local commit only)'}")

    # Personal mode — no local repo management needed
    if REPO_MODE == "personal":
        print(f"\n✅ Personal mode — no branch prep needed. Output goes to output/ folder.")
        return {"success": True, "branch": branch_name, "mode": "personal"}

    # RouteOne mode — manage local repo
    if not REPO_PATH or not os.path.exists(REPO_PATH):
        msg = f"REPO_PATH '{REPO_PATH}' not found. Check your .env file."
        print(f"\n❌ {msg}")
        return {"success": False, "error": msg}

    cwd = REPO_PATH

    # Check if branch already exists locally
    if _branch_exists_locally(branch_name, cwd):
        print(f"\n🔄 Branch '{branch_name}' already exists locally — switching to it.")
        success, output = _run_git(["git", "checkout", branch_name], cwd=cwd)
        if not success:
            print(f"\n❌ Failed to switch to branch: {output}")
            return {"success": False, "error": output}
        print(f"✅ Switched to existing branch: {branch_name}")
        return {"success": True, "branch": branch_name, "mode": "routeone", "action": "resumed"}

    # Branch does not exist — create from BASE_BRANCH
    print(f"\n📥 Branch not found. Creating from '{BASE_BRANCH}'...")

    # Step 1: Switch to base branch
    success, output = _run_git(["git", "checkout", BASE_BRANCH], cwd=cwd)
    if not success:
        print(f"\n❌ Failed to checkout {BASE_BRANCH}: {output}")
        return {"success": False, "error": output}
    print(f"✅ Switched to {BASE_BRANCH}")

    # Step 2: Pull latest
    success, output = _run_git(["git", "pull", "origin", BASE_BRANCH], cwd=cwd)
    if not success:
        print(f"\n⚠️  Pull failed (continuing anyway): {output}")
    else:
        print(f"✅ Pulled latest from {BASE_BRANCH}")

    # Step 3: Create new feature branch
    success, output = _run_git(["git", "checkout", "-b", branch_name], cwd=cwd)
    if not success:
        print(f"\n❌ Failed to create branch: {output}")
        return {"success": False, "error": output}

    print(f"✅ Created new branch: {branch_name}")
    return {"success": True, "branch": branch_name, "mode": "routeone", "action": "created"}


def commit_and_push(ticket_id: str, commit_message: str = None) -> dict:
    """
    Commits (and optionally pushes) generated code after the pipeline completes.

    Personal mode:
      - Nothing to do here — agent_github.py handles the push via GitHub API
      - Returns success immediately

    RouteOne mode:
      - Stage all changes in REPO_PATH
      - Commit with a meaningful message (always)
      - Push branch to Bitbucket only if AUTO_PUSH=true in .env
      - If AUTO_PUSH=false, stops after local commit and prints instructions
    """
    branch_name = f"feature/{ticket_id.lower()}"
    message = commit_message or f"{ticket_id}: AI generated implementation"

    print(f"\n{'=' * 50}")
    print(f"📤 Git Manager — committing for {ticket_id}")
    print(f"{'=' * 50}")

    # Personal mode — agent_github.py handles this
    if REPO_MODE == "personal":
        print(f"\n✅ Personal mode — push handled by GitHub agent.")
        return {"success": True, "mode": "personal"}

    # RouteOne mode
    if not REPO_PATH or not os.path.exists(REPO_PATH):
        msg = f"REPO_PATH '{REPO_PATH}' not found. Check your .env file."
        print(f"\n❌ {msg}")
        return {"success": False, "error": msg}

    cwd = REPO_PATH

    # Step 1: Stage all changes
    success, output = _run_git(["git", "add", "."], cwd=cwd)
    if not success:
        print(f"\n❌ git add failed: {output}")
        return {"success": False, "error": output}
    print(f"✅ Staged all changes")

    # Step 2: Commit
    success, output = _run_git(["git", "commit", "-m", message], cwd=cwd)
    if not success:
        if "nothing to commit" in output:
            print(f"\n⚠️  Nothing to commit — no changes detected.")
            return {"success": True, "mode": "routeone", "note": "nothing to commit"}
        print(f"\n❌ git commit failed: {output}")
        return {"success": False, "error": output}
    print(f"✅ Committed: {message}")

    # Step 3: Push — only if AUTO_PUSH=true
    if not AUTO_PUSH:
        print(f"\n⏸️  AUTO_PUSH=false — skipping push to Bitbucket.")
        print(f"   Branch '{branch_name}' committed locally in: {REPO_PATH}")
        print(f"   To push manually when ready:")
        print(f"   cd {REPO_PATH}")
        print(f"   git push origin {branch_name}")
        return {
            "success": True,
            "branch": branch_name,
            "mode": "routeone",
            "committed": message,
            "pushed": False,
            "note": "LOCAL COMMIT ONLY — set AUTO_PUSH=true in .env to enable push"
        }

    # AUTO_PUSH=true — push to Bitbucket
    success, output = _run_git(["git", "push", "origin", branch_name], cwd=cwd)
    if not success:
        print(f"\n❌ git push failed: {output}")
        return {"success": False, "error": output}

    print(f"✅ Pushed branch to Bitbucket: {branch_name}")
    return {
        "success": True,
        "branch": branch_name,
        "mode": "routeone",
        "committed": message,
        "pushed": True
    }


# ─── CLI Test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: py git_manager.py <prepare|commit> <ticket_id>")
        print("Example: py git_manager.py prepare R1OD-002")
        print("Example: py git_manager.py commit R1OD-002")
        sys.exit(1)

    action    = sys.argv[1]
    ticket_id = sys.argv[2]

    if action == "prepare":
        result = prepare_branch(ticket_id)
    elif action == "commit":
        result = commit_and_push(ticket_id)
    else:
        print(f"Unknown action: {action}. Use 'prepare' or 'commit'.")
        sys.exit(1)

    print(f"\nResult: {result}")