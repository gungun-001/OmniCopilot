import sys
import io
sys.path.insert(0, '/Users/aaravchugh8607/Desktop/omni_copilot/backend/tools')
from all_tools import get_drive_service
from googleapiclient.http import MediaIoBaseDownload
from pypdf import PdfReader

service = get_drive_service()
# Get the file ID for Aarav_final_Resume.pdf
results = service.files().list(q="name contains 'Aarav_final_Resume.pdf'", pageSize=1, fields="files(id, name)").execute()
files = results.get('files', [])
if not files:
    print("File not found.")
    sys.exit()

file_id = files[0]['id']
print(f"Found file ID: {file_id}")

request = service.files().get_media(fileId=file_id)
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
done = False
while done is False:
    status, done = downloader.next_chunk()
    print(f"Download {int(status.progress() * 100)}%.")

fh.seek(0)
reader = PdfReader(fh)
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

print("Extracted text length:", len(text))
print("Preview:", text[:200])
