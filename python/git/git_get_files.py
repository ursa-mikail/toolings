import os
import subprocess
import requests

# --- Config ---
BASE_API = "https://api.github.com/repos/ursa-mikail/mechanisms/contents"
TOKEN = "<token>" # U2FsdGVkX1+xUPW3UqD4qDlUcny1/tdQ++aY/PrufHlM1WO+pMUZWn8pgzGxlMjieVnDcyP8n7Rp9pjif3tWoA==
DEST_DIR = "downloaded_files"
DOWNLOAD_EXTENSIONS = ['.py', '.go']

headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

os.makedirs(DEST_DIR, exist_ok=True)

def fetch_and_download(api_url, rel_path=""):
    print(f"Fetching: {api_url}")
    r = requests.get(api_url, headers=headers)
    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text}")
        return

    items = r.json()
    if not isinstance(items, list):
        return

    for item in items:
        name = item['name']
        path = os.path.join(rel_path, name)
        print(f"Checking: {path} ({item['type']})")

        if item['type'] == 'file' and any(name.endswith(ext) for ext in DOWNLOAD_EXTENSIONS):
            os.makedirs(os.path.join(DEST_DIR, rel_path), exist_ok=True)
            output_path = os.path.join(DEST_DIR, path)
            download_url = item['download_url']
            print(f"Downloading {path}...")

            subprocess.run([
                "curl", "-L", "-H", f"Authorization: token {TOKEN}",
                "-o", output_path, download_url
            ], check=True)

        elif item['type'] == 'dir':
            fetch_and_download(item['url'], path)

# Start recursive download from repo root
fetch_and_download(BASE_API)
