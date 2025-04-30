import os
import json
import shutil
import pexpect
from datetime import datetime
import time

import secrets

N = 16  # number of bytes
hex_string = secrets.token_hex(N)

# Setup GitHub credentials
username = "ursa-mikail"
token = "YOUR_TOKEN_HERE"  # Replace with your GitHub token (ciphered: U2FsdGVkX1+7TtLL8EZXcO+sDvRQ830mnmRH+1bPozCC3DDFIc4hyk/kAlvk6OBrlMhC6s/DVrAJypjnA/6zdQ==)

repo_owner = "ursa-mikail"
repo_name = "templates"
json_filename = "hash_data_00.json"

# Authenticated Git URL
repo_url = f"https://{username}:{token}@github.com/{repo_owner}/{repo_name}.git"
local_repo = f"/tmp/{repo_name}"
json_path = os.path.join(local_repo, json_filename)

# Generate timestamps
now = datetime.now()
timestamp_str = now.strftime("%Y-%m-%d_%H%M:%S")
timestamp_linux = int(time.time())

# Hashes to push
hashes = {
    "user1": "babe00ca5e0065d61d8327deb882cf99",
    "user2": hex_string,
    "timestamp": timestamp_str,
    "timestamp_linux": timestamp_linux
}

# Clean any existing repo
if os.path.exists(local_repo):
    shutil.rmtree(local_repo)

# Clone with authentication
child = pexpect.spawn(f"git clone {repo_url} {local_repo}", encoding='utf-8')
child.expect(pexpect.EOF)

# Write the JSON file into the repo
os.makedirs(local_repo, exist_ok=True)
with open(json_path, "w") as f:
    json.dump(hashes, f, indent=4)

# Stage and commit the JSON file
os.chdir(local_repo)
#pexpect.run("git config user.email 'bot@example.com'")
#pexpect.run("git config user.name 'Auto Commit Bot'")
pexpect.run("git add .")
pexpect.run(f"git commit -m 'Add --- {json_filename}'")
pexpect.run("git push")
print(f"✅ JSON: {json_filename} pushed successfully.")

# Now delete the file and push that change too
os.remove(json_path)
pexpect.run("git add .")
pexpect.run(f"git commit -m 'Delete {json_filename}'")
pexpect.run("git push")

print(f"✅ JSON: {json_filename} pushed and deleted successfully.")
