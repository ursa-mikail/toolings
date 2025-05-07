import os
import requests
import hashlib
import zipfile
import certifi

# Constants
REPO_API = "https://api.github.com/repos/ursa-mikail/mechanisms/contents/resource_profiling/go"
RAW_BASE = "https://raw.githubusercontent.com/ursa-mikail/mechanisms/main/resource_profiling/go"
DOWNLOAD_DIR = "downloaded_go_files"
ZIP_FILE = "go_files.zip"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Step 1: Get filenames via GitHub API
"""
def get_filenames_from_api():
    resp = requests.get(REPO_API)
    resp.raise_for_status()
    return [item['name'] for item in resp.json() if item['type'] == 'file']
"""
def get_filenames_from_api():
    try:
        response = requests.get(REPO_API, verify=certifi.where())
        response.raise_for_status()
        return [item['name'] for item in response.json() if item['type'] == 'file']
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to retrieve file list: {e}")
        return []

# Step 2: Download and hash each file
"""
def download_and_hash_files(filenames):
    sha256s = {}
    for filename in filenames:
        raw_url = f"{RAW_BASE}/{filename}"
        local_path = os.path.join(DOWNLOAD_DIR, filename)
        resp = requests.get(raw_url)
        if resp.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(resp.content)
            sha = hashlib.sha256(resp.content).hexdigest()
            sha256s[filename] = sha
            print(f"Downloaded {filename}, SHA-256: {sha}")
        else:
            print(f"Failed to download {filename}")
    return sha256s
"""
def download_and_hash_files(filenames):
    hashes = {}
    for filename in filenames:
        url = f"{RAW_BASE}/{filename}"
        dest_path = os.path.join(DOWNLOAD_DIR, filename)
        try:
            resp = requests.get(url, verify=certifi.where())
            resp.raise_for_status()
            with open(dest_path, "wb") as f:
                f.write(resp.content)
            file_hash = hashlib.sha256(resp.content).hexdigest()
            hashes[filename] = file_hash
            print(f"Downloaded {filename}, SHA-256: {file_hash}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Could not download {filename}: {e}")
    return hashes

# Step 3: Zip files and hash zip
def zip_and_hash(directory, zip_name):
    with zipfile.ZipFile(zip_name, "w") as zf:
        for file in os.listdir(directory):
            full_path = os.path.join(directory, file)
            zf.write(full_path, arcname=file)
    with open(zip_name, "rb") as f:
        zip_hash = hashlib.sha256(f.read()).hexdigest()
    print(f"\nZipped into {zip_name}, SHA-256: {zip_hash}")
    return zip_hash

# Execute
filenames = get_filenames_from_api()
file_hashes = download_and_hash_files(filenames)
zip_hash = zip_and_hash(DOWNLOAD_DIR, ZIP_FILE)

"""
Downloaded magic_bytes_hunting.go, SHA-256: aa77023dd6e2e142d723b85a83a3588cf9352f464be755353af76da5c4578d3c
Downloaded memory_dumping_simulation.go, SHA-256: 6271bcb6c896a94dd26a51e6bf50bd6d477a91eaa63583b8292a412d48c89fc3
Downloaded memory_limit_test.go, SHA-256: 14050d2ef6591f1c4bfedcb80764764c2ab4a3c744b0e6d695f06a934c5b9704

Zipped into go_files.zip, SHA-256: dc34c74aa2ff6dd2dbd6ab7a2527c850196190af845b59aa29573840ba0f8b58
"""