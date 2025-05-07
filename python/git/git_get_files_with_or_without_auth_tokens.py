import os
import requests
from urllib.parse import urlparse
import hashlib

# 🔧 Set your GitHub folder URL and token (optional)
GITHUB_URL = "https://github.com/ursa-mikail/mechanisms/tree/main/resource_profiling/go"
GITHUB_TOKEN = ""  # Optional: "ghp_..."

ALLOWED_EXT = [".py", ".go"]
DOWNLOAD_DIR = "downloaded"

HEADERS = {
    "Accept": "application/vnd.github.v3+json"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

def parse_github_url(github_url):
    parsed = urlparse(github_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError("URL must be in form github.com/{user}/{repo}")
    user, repo = parts[0], parts[1]
    branch = "main"
    path = ""
    if len(parts) >= 5 and parts[2] == "tree":
        branch = parts[3]
        path = "/".join(parts[4:])
    return f"{user}/{repo}", branch, path

def is_allowed(filename):
    return any(filename.endswith(ext) for ext in ALLOWED_EXT)

def fetch_recursive(api_url, relative_path=""):
    response = requests.get(api_url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
    items = response.json()
    for item in items:
        if item['type'] == 'file' and is_allowed(item['name']):
            print(f"📄 Downloading: {item['path']}")
            download_file(item['download_url'], item['path'])
        elif item['type'] == 'dir':
            fetch_recursive(item['url'])

def download_file(url, path):
    local_path = os.path.join(DOWNLOAD_DIR, path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    response = requests.get(url)
    with open(local_path, 'wb') as f:
        f.write(response.content)
    print(f"🔒 SHA256({os.path.basename(path)}): {sha256(local_path)}")

def sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def main():
    repo_path, branch, subpath = parse_github_url(GITHUB_URL)
    api_url = f"https://api.github.com/repos/{repo_path}/contents/{subpath}?ref={branch}"
    print("📥 Starting from:", api_url)
    fetch_recursive(api_url)

if __name__ == "__main__":
    main()

"""
📥 Starting from: https://api.github.com/repos/ursa-mikail/mechanisms/contents/resource_profiling/go?ref=main
📄 Downloading: resource_profiling/go/magic_bytes_hunting.go
🔒 SHA256(magic_bytes_hunting.go): aa77023dd6e2e142d723b85a83a3588cf9352f464be755353af76da5c4578d3c
📄 Downloading: resource_profiling/go/memory_dumping_simulation.go
🔒 SHA256(memory_dumping_simulation.go): 6271bcb6c896a94dd26a51e6bf50bd6d477a91eaa63583b8292a412d48c89fc3
📄 Downloading: resource_profiling/go/memory_limit_test.go
🔒 SHA256(memory_limit_test.go): 14050d2ef6591f1c4bfedcb80764764c2ab4a3c744b0e6d695f06a934c5b9704
"""