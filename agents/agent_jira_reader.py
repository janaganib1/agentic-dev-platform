import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL    = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def get_jira_story(ticket_id: str) -> dict:
    """Fetch a Jira story by ticket ID and return structured data."""

    url  = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code != 200:
        print(f"❌ Failed to fetch {ticket_id}: {response.status_code} - {response.text}")
        return {}

    data = response.json()
    fields = data.get("fields", {})

    # Extract description text from Atlassian Document Format (ADF)
    description = ""
    desc_field = fields.get("description")
    if desc_field and isinstance(desc_field, dict):
        for block in desc_field.get("content", []):
            for inline in block.get("content", []):
                if inline.get("type") == "text":
                    description += inline.get("text", "") + " "

    story = {
        "ticket_id"   : ticket_id,
        "summary"     : fields.get("summary", ""),
        "status"      : fields.get("status", {}).get("name", ""),
        "priority"    : fields.get("priority", {}).get("name", ""),
        "assignee"    : (fields.get("assignee") or {}).get("displayName", "Unassigned"),
        "description" : description.strip(),
        "labels"      : fields.get("labels", []),
        "story_points": fields.get("story_points") or fields.get("customfield_10016"),
    }

    return story


def run_jira_reader(ticket_id: str) -> dict:
    print(f"\n{'='*50}")
    print(f"📋 Jira Reader Agent — fetching {ticket_id}")
    print(f"{'='*50}")

    story = get_jira_story(ticket_id)

    if not story:
        return {}

    print(f"✅ Ticket     : {story['ticket_id']}")
    print(f"📝 Summary    : {story['summary']}")
    print(f"🔄 Status     : {story['status']}")
    print(f"⚡ Priority   : {story['priority']}")
    print(f"👤 Assignee   : {story['assignee']}")
    print(f"🏷  Labels     : {', '.join(story['labels']) if story['labels'] else 'None'}")
    print(f"📖 Description: {story['description'][:300]}{'...' if len(story['description']) > 300 else ''}")

    return story


if __name__ == "__main__":
    import sys
    ticket = sys.argv[1] if len(sys.argv) > 1 else "PCKNFNDT-2"
    run_jira_reader(ticket)