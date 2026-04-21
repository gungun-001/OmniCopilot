import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv('/Users/aaravchugh8607/Desktop/omni_copilot/backend/.env')
notion = Client(auth=os.environ['NOTION_API_KEY'])

# Search all pages/databases
results = notion.search().get('results', [])
if not results:
    print("Integration has no access to any pages/databases.")
for item in results:
    kind = item.get('object')
    props = item.get('properties', {})
    
    # Try to extract a title
    title = "Untitled"
    if kind == "page":
        # Usually title is in a property called 'title' or 'Name' or whatever has type 'title'
        for prop_name, prop_data in props.items():
            if prop_data.get('type') == 'title':
                title_arr = prop_data.get('title', [])
                if title_arr:
                    title = title_arr[0].get('plain_text', 'Untitled')
                break
    elif kind == "database":
        title_arr = item.get('title', [])
        if title_arr:
            title = title_arr[0].get('plain_text', 'Untitled')
            
    print(f"Type: {kind}, ID: {item.get('id')}, Title: {title}")
