from langchain.tools import tool
import os
import requests
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import uuid

# --- Helper to Get Google Service ---
def get_calendar_service():
    """Loads credentials from token.json and returns the Google Calendar service."""
    token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
    if not os.path.exists(token_path):
        return None
    
    with open(token_path, "r") as token_file:
        creds_data = json.load(token_file)
        creds = Credentials.from_authorized_user_info(creds_data)
        return build("calendar", "v3", credentials=creds)

def get_gmail_service():
    """Loads credentials from token.json and returns the Gmail service."""
    token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
    if not os.path.exists(token_path):
        return None
    
    with open(token_path, "r") as token_file:
        creds_data = json.load(token_file)
        creds = Credentials.from_authorized_user_info(creds_data)
        return build("gmail", "v1", credentials=creds)

def get_drive_service():
    """Loads credentials from token.json and returns the Google Drive service."""
    token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
    if not os.path.exists(token_path):
        return None
    
    with open(token_path, "r") as token_file:
        creds_data = json.load(token_file)
        creds = Credentials.from_authorized_user_info(creds_data)
        return build("drive", "v3", credentials=creds)

# 1. Google Calendar Tool
@tool
def schedule_meeting_tool(summary: str, start_time: str, end_time: str, attendees: list[str] = [], description: str = "") -> str:
    """Schedules a meeting in Google Calendar and automatically generates a Google Meet link."""
    service = get_calendar_service()
    if not service:
        # Fallback to realistic mock if token is missing, but notify the user
        import random
        import string
        random_id = '-'.join([''.join(random.choices(string.ascii_lowercase, k=n)) for n in [3, 4, 3]])
        meet_link = f"https://meet.google.com/{random_id}"
        return f"(MOCK) Please run 'python3 utils/generate_google_token.py' in the backend folder to activate real meetings. \nSuccessfully scheduled '{summary}' from {start_time} to {end_time}. Mock link: {meet_link}"

    try:
        # Ensure timezone offset is present for naive datetimes 
        if not start_time.endswith('Z') and '+' not in start_time and '-' not in start_time[-6:]:
            start_time += 'Z'
        if not end_time.endswith('Z') and '+' not in end_time and '-' not in end_time[-6:]:
            end_time += 'Z'

        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time},
            'end': {'dateTime': end_time},
            'attendees': [{'email': e} for e in attendees],
            'transparency': 'opaque',
            'conferenceData': {
                'createRequest': {
                    'requestId': str(uuid.uuid4()),
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }

        event = service.events().insert(
            calendarId='primary', 
            body=event, 
            sendUpdates='all',
            conferenceDataVersion=1
        ).execute()

        meet_link = event.get('hangoutLink', 'No link generated.')
        return f"Successfully scheduled '{summary}' from {start_time} to {end_time}. Real Google Meet link: {meet_link}"

    except HttpError as error:
        return f"An error occurred with Google Calendar API: {error}"

# 2. Gmail Tool
@tool
def send_email_tool(to_email: str, subject: str, body: str) -> str:
    """Sends an email via Gmail API."""
    import base64
    from email.message import EmailMessage
    
    service = get_gmail_service()
    if not service:
        return "Gmail credentials not found. Please run 'python3 utils/generate_google_token.py' in backend."
        
    try:
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to_email
        message['From'] = 'me'
        message['Subject'] = subject
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        service.users().messages().send(userId='me', body=create_message).execute()
        return f"Email sent to {to_email} with subject '{subject}'."
    except HttpError as error:
        return f"An error occurred with Gmail API: {error}"

# 3. Google Drive Tool
@tool
def search_drive_tool(query: str) -> str:
    """Searches for files in Google Drive by their name. Pass ONLY the raw file name or keyword (e.g. 'Aarav_resume.pdf'). Do NOT include search operators like 'title:' or 'name:'."""
    service = get_drive_service()
    if not service:
        return "Google Drive credentials not found. Please run 'python3 utils/generate_google_token.py'."
        
    try:
        results = service.files().list(
            q=f"name contains '{query}'", 
            pageSize=10, 
            fields="nextPageToken, files(id, name, webViewLink)"
        ).execute()
        files = results.get('files', [])
        
        if not files:
            return f"No matching files found for '{query}' in Google Drive."
            
        file_data = []
        for file in files:
            file_data.append(f"Name: {file.get('name')}\\nLink: {file.get('webViewLink', 'No link available')}\\n---")
            
        return "\\n".join(file_data)
    except HttpError as error:
        return f"An error occurred searching Google Drive: {error}"

# 3b. Read Google Drive File Content
@tool
def read_drive_file_tool(query: str) -> str:
    """Reads the textual content of a file from Google Drive (e.g., a PDF) given its name. Pass ONLY the raw file name or keyword (e.g. 'Aarav_resume.pdf'). Do NOT include search operators."""
    import io
    from googleapiclient.http import MediaIoBaseDownload
    
    service = get_drive_service()
    if not service:
        return "Google Drive credentials not found."
    
    try:
        results = service.files().list(
            q=f"name contains '{query}'", 
            pageSize=1, 
            fields="files(id, name, mimeType)"
        ).execute()
        files = results.get('files', [])
        
        if not files:
            return f"No matching files found for '{query}' to read."
            
        file_id = files[0]['id']
        mime_type = files[0].get('mimeType', '')
        
        if 'pdf' in mime_type.lower() or query.lower().endswith('.pdf'):
            try:
                from pypdf import PdfReader
            except ImportError:
                return "The pypdf library is not installed."
                
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                
            fh.seek(0)
            reader = PdfReader(fh)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text[:4000] # Return enough chars for a standard LLM window
        else:
            return f"Unsupported file type. MIME type: {mime_type}. Currently this tool only supports reading PDF files directly."
            
    except HttpError as error:
        return f"An error occurred reading from Google Drive: {error}"
    except Exception as e:
        return f"Error extracting content: {e}"

# 4. Notion Tool
@tool
def create_notion_page_tool(title: str, content: str) -> str:
    """Creates a note or page in Notion workspace."""
    from notion_client import Client
    notion_token = os.getenv("NOTION_API_KEY")
    if not notion_token:
        return "Notion API key not configured."
    
    try:
        notion = Client(auth=notion_token)
        # Find an accessible parent page or database
        results = notion.search(filter={"property": "object", "value": "page"}).get("results", [])
        if not results:
            results = notion.search(filter={"property": "object", "value": "database"}).get("results", [])
            
        if not results:
            return "Cannot create Notion page. Your Notion integration hasn't been granted access to any pages. Please open Notion, go to the parent page/workspace (like 'Aarav Chugh’s Space HQ'), click the 3-dots menu (top right) -> Add connections -> select your integration."
            
        parent = results[0]
        parent_id = parent["id"]
        parent_type = parent["object"]
        
        new_page = {
            "parent": {"type": f"{parent_type}_id", f"{parent_type}_id": parent_id},
            "properties": {},
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
                }
            ]
        }
        
        if parent_type == "database":
            new_page["properties"] = {"Name": {"title": [{"text": {"content": title}}]}}
        else:
            new_page["properties"] = {"title": {"title": [{"text": {"content": title}}]}}
            
        created = notion.pages.create(**new_page)
        page_url = created.get("url", "No URL returned")
        return f"Successfully created Notion content '{title}'. Link to view: {page_url}"
    except Exception as e:
        return f"Failed to create Notion page. Note that Database parent configurations may have different required properties. Error: {str(e)}"

# 5. Slack Tool
@tool
def send_slack_message_tool(channel: str, message: str) -> str:
    """Sends a message to a specific Slack channel or user."""
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        return "Slack tool is not configured. Add SLACK_BOT_TOKEN to .env."
    try:
        client = WebClient(token=slack_token)
        client.chat_postMessage(channel=channel, text=message)
        return f"Message sent to {channel} on Slack."
    except SlackApiError as e:
        return f"Slack error: {e.response['error']}"
    except Exception as e:
        return f"Slack error: {str(e)}"

# 6. Discord Tool
@tool
def send_discord_message_tool(message: str) -> str:
    """Sends a message to a Discord channel via Webhook."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url or webhook_url == "your_discord_webhook_url":
        return "Discord webhook URL not configured. Add DISCORD_WEBHOOK_URL to .env (get it from Discord Server Settings > Integrations > Webhooks)."
    try:
        response = requests.post(webhook_url, json={"content": message}, timeout=10)
        if response.status_code in (200, 204):
            return "Message sent to Discord successfully."
        return f"Discord returned status {response.status_code}: {response.text}"
    except requests.exceptions.Timeout:
        return "Discord request timed out (10s)."
    except Exception as e:
        return f"Discord error: {str(e)}"

# 7. Google Meet Tool
@tool
def create_google_meet_tool(topic: str, duration_mins: int = 30) -> str:
    """Creates a Google Meet meeting link."""
    from datetime import datetime, timedelta
    
    service = get_calendar_service()
    if not service:
        import random
        import string
        random_id = '-'.join([''.join(random.choices(string.ascii_lowercase, k=n)) for n in [3, 4, 3]])
        meet_link = f"https://meet.google.com/{random_id}"
        return f"(MOCK) Please run 'python3 utils/generate_google_token.py' to activate real meetings. \nGoogle Meet '{topic}' for {duration_mins} mins created. Mock link: {meet_link}"

    try:
        now = datetime.utcnow()
        start = now.isoformat() + 'Z'
        end = (now + timedelta(minutes=duration_mins)).isoformat() + 'Z'
        
        event = {
            'summary': topic,
            'start': {'dateTime': start},
            'end': {'dateTime': end},
            'conferenceData': {
                'createRequest': {
                    'requestId': str(uuid.uuid4()),
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }

        event = service.events().insert(
            calendarId='primary', 
            body=event, 
            conferenceDataVersion=1
        ).execute()

        meet_link = event.get('hangoutLink', 'No link generated.')
        return f"Google Meet '{topic}' for {duration_mins} mins created. Link: {meet_link}"

    except HttpError as error:
        return f"An error occurred with Google Calendar API: {error}"

# 8. GitHub Tool
@tool
def fetch_github_file_tool(repo: str, file_path: str) -> str:
    """Reads the content of a file from a public GitHub repository (e.g. 'owner/repo')."""
    try:
        # Try 'main' branch first, then fall back to 'master'
        for branch in ["main", "master"]:
            url = f"https://raw.githubusercontent.com/{repo}/{branch}/{file_path}"
            try:
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    return res.text[:500] + "... (truncated)"
            except requests.exceptions.Timeout:
                continue # Try next branch if one times out
        return f"File '{file_path}' not found in '{repo}' on main or master branch, or the repository is private / timed out."
    except Exception as e:
        return str(e)

# 8b. List Latest GitHub Repo Tool
@tool
def get_latest_github_repo_tool() -> str:
    """Gets the name and file structure of the authenticated user's most recently updated GitHub repository."""
    from github import Github
    github_token = os.getenv("GITHUB_ACCESS_TOKEN")
    if not github_token:
        return "GitHub Access Token not configured in .env."
    try:
        g = Github(github_token)
        user = g.get_user()
        repos = list(user.get_repos(type="owner", sort="updated", direction="desc"))
        if not repos:
            return "No repositories found for this GitHub account."

        # Find the latest repo that isn't empty
        latest = None
        for repo in repos:
            try:
                repo.get_contents("")  # Will raise if empty
                latest = repo
                break
            except Exception:
                continue

        if not latest:
            return "All repositories appear to be empty."

        contents = latest.get_contents("")
        file_names = []
        for content_file in contents[:15]:
            if content_file.type == 'dir':
                file_names.append(f"📁 {content_file.name}/")
            else:
                file_names.append(f"📄 {content_file.name}")
        
        files_str = "\n".join(file_names)
        return f"Latest updated repository: {latest.full_name}\nDescription: {latest.description}\nLast Updated: {latest.updated_at}\n\nFiles in root:\n{files_str}"
    except Exception as e:
        return f"An error occurred fetching the GitHub repository: {str(e)}"

# 8c. List All GitHub Repos Tool
@tool
def get_github_repos() -> str:
    """Fetches all repositories of the authenticated GitHub user using API token. Use this for any GitHub-related queries like listing repos, latest repo, project info."""
    from github import Github
    github_token = os.getenv("GITHUB_ACCESS_TOKEN")
    if not github_token:
        return "GitHub Access Token not configured in .env."
    try:
        g = Github(github_token)
        user = g.get_user()
        repos = []
        # Fetching simplified repo info
        for repo in user.get_repos(type="owner", sort="updated", direction="desc"):
            repos.append({
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description or "No description",
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                "created_at": repo.created_at.isoformat() if repo.created_at else None
            })
        if not repos:
            return "No repositories found for this GitHub account."
        return json.dumps(repos, indent=2)
    except Exception as e:
        return f"An error occurred fetching the GitHub repositories: {str(e)}"

# 9. Read Emails Tool
@tool
def read_emails_tool(max_results: int = 5, query: str = "") -> str:
    """Reads recent emails from Gmail. Can filter by a search query."""
    service = get_gmail_service()
    if not service:
         return "Gmail credentials not found. Please run 'python3 utils/generate_google_token.py'."
         
    try:
        results = service.users().messages().list(userId='me', maxResults=max_results, q=query).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return "No emails found."
            
        email_data = []
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            
            # Extract headers (Subject, From, Date)
            headers = msg_data.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            # Extract snippet
            snippet = msg_data.get('snippet', '')
            
            email_data.append(f"From: {sender}\\nDate: {date}\\nSubject: {subject}\\nSnippet: {snippet}\\n---")
            
        return "\\n".join(email_data)
    except HttpError as error:
        return f"An error occurred reading emails: {error}"

# 10. Read Calendar Events Tool
@tool
def read_calendar_events_tool(max_results: int = 10, time_min: str = "") -> str:
    """Reads upcoming events from Google Calendar. time_min should be ISO format (e.g. 2026-04-09T00:00:00Z). If none, defaults to now."""
    service = get_calendar_service()
    if not service:
        return "Google Calendar credentials not found. Please run 'python3 utils/generate_google_token.py'."
        
    try:
        from datetime import datetime
        if not time_min:
            time_min = datetime.utcnow().isoformat() + 'Z'
            
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=time_min,
            maxResults=max_results, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "No upcoming events found."
            
        event_data = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            summary = event.get('summary', 'No Title')
            event_data.append(f"Event: {summary}\\nStart: {start}\\nEnd: {end}\\n---")
            
        return "\\n".join(event_data)
    except HttpError as error:
        return f"An error occurred reading calendar events: {error}"

OMNI_TOOLS = [
    schedule_meeting_tool,
    send_email_tool,
    search_drive_tool,
    read_drive_file_tool,
    create_notion_page_tool,
    send_slack_message_tool,
    send_discord_message_tool,
    create_google_meet_tool,
    fetch_github_file_tool,
    get_latest_github_repo_tool,
    get_github_repos,
    read_emails_tool,
    read_calendar_events_tool
]
