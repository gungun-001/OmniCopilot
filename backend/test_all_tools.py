"""
Comprehensive test script for all Omni Copilot tools.
Run with: python3 test_all_tools.py
"""
import os, sys, json
from dotenv import load_dotenv
load_dotenv()

results = {}

def run_test(name, fn):
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {name}")
    print('='*60)
    try:
        result = fn()
        status = "✅ PASS" if result and "error" not in str(result).lower() and "not found" not in str(result).lower() and "not configured" not in str(result).lower() else "⚠️  WARN"
        print(f"Result: {result}")
        print(f"Status: {status}")
        results[name] = {"status": status, "output": str(result)[:200]}
    except Exception as e:
        print(f"ERROR: {e}")
        results[name] = {"status": "❌ FAIL", "output": str(e)[:200]}

# ---- 1. Google Calendar: Read Events ----
def test_read_calendar():
    from tools.all_tools import read_calendar_events_tool
    return read_calendar_events_tool.invoke({"max_results": 3})

# ---- 2. Google Calendar: Schedule Meeting ----
def test_schedule_meeting():
    from tools.all_tools import schedule_meeting_tool
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    start = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S+05:30")
    end   = (now + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S+05:30")
    return schedule_meeting_tool.invoke({
        "summary": "Omni Copilot Tool Test Meeting",
        "start_time": start,
        "end_time": end,
        "attendees": [],
        "description": "Automated test meeting created by test_all_tools.py"
    })

# ---- 3. Gmail: Read Emails ----
def test_read_emails():
    from tools.all_tools import read_emails_tool
    return read_emails_tool.invoke({"max_results": 3})

# ---- 4. Gmail: Send Email ----
def test_send_email():
    from tools.all_tools import send_email_tool
    # Read the actual gmail address from token
    from tools.all_tools import get_gmail_service
    service = get_gmail_service()
    if not service:
        return "Gmail service not available"
    profile = service.users().getProfile(userId='me').execute()
    email = profile.get('emailAddress', 'test@gmail.com')
    return send_email_tool.invoke({
        "to_email": email,
        "subject": "Omni Copilot Tool Test",
        "body": "This is an automated test email from test_all_tools.py to verify Gmail tool is working."
    })

# ---- 5. Google Drive: Search ----
def test_search_drive():
    from tools.all_tools import search_drive_tool
    return search_drive_tool.invoke({"query": "resume"})

# ---- 6. Google Drive: Read File ----
def test_read_drive_file():
    from tools.all_tools import read_drive_file_tool
    return read_drive_file_tool.invoke({"query": "resume"})

# ---- 7. Notion: Create Page ----
def test_notion():
    from tools.all_tools import create_notion_page_tool
    return create_notion_page_tool.invoke({
        "title": "Omni Copilot Test Note",
        "content": "This is a test note created by test_all_tools.py to verify Notion integration."
    })

# ---- 8. Slack: Send Message ----
def test_slack():
    from tools.all_tools import send_slack_message_tool
    return send_slack_message_tool.invoke({"channel": "#general", "message": "Test from Omni Copilot"})

# ---- 9. Discord: Send Message ----
def test_discord():
    from tools.all_tools import send_discord_message_tool
    return send_discord_message_tool.invoke({"message": "Test from Omni Copilot"})

# ---- 10. Google Meet: Create Meeting ----
def test_google_meet():
    from tools.all_tools import create_google_meet_tool
    return create_google_meet_tool.invoke({"topic": "Test Meeting", "duration_mins": 30})

# ---- 11. GitHub: Fetch File ----
def test_github_fetch_file():
    from tools.all_tools import fetch_github_file_tool
    return fetch_github_file_tool.invoke({"repo": "octocat/Hello-World", "file_path": "README"})

# ---- 12. GitHub: Latest Repo ----
def test_github_latest_repo():
    from tools.all_tools import get_latest_github_repo_tool
    return get_latest_github_repo_tool.invoke({})

# ---- 13. GitHub: All Repos ----
def test_github_all_repos():
    from tools.all_tools import get_github_repos
    result = get_github_repos.invoke({})
    try:
        repos = json.loads(result)
        return f"Found {len(repos)} repos. Latest: {repos[0]['name'] if repos else 'None'}"
    except:
        return result

# ---- RUN ALL TESTS ----
run_test("1. Read Calendar Events", test_read_calendar)
run_test("2. Schedule Meeting",      test_schedule_meeting)
run_test("3. Read Emails",           test_read_emails)
run_test("4. Send Email",            test_send_email)
run_test("5. Search Google Drive",   test_search_drive)
run_test("6. Read Drive File (PDF)", test_read_drive_file)
run_test("7. Create Notion Page",    test_notion)
run_test("8. Send Slack Message",    test_slack)
run_test("9. Send Discord Message",  test_discord)
run_test("10. Create Google Meet",   test_google_meet)
run_test("11. GitHub Fetch File",    test_github_fetch_file)
run_test("12. GitHub Latest Repo",   test_github_latest_repo)
run_test("13. GitHub All Repos",     test_github_all_repos)

# ---- SUMMARY ----
print("\n" + "="*60)
print("📊 SUMMARY")
print("="*60)
for test, data in results.items():
    print(f"{data['status']}  {test}")

pass_count = sum(1 for d in results.values() if "PASS" in d["status"])
warn_count = sum(1 for d in results.values() if "WARN" in d["status"])
fail_count = sum(1 for d in results.values() if "FAIL" in d["status"])
print(f"\nTotal: {len(results)} | ✅ {pass_count} Passed | ⚠️  {warn_count} Warnings | ❌ {fail_count} Failed")
