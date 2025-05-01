import os
import hashlib
import shutil
from git import Repo

# --- Setup ---
username = "ursa-mikail"
token = "YOUR_TOKEN_HERE"  # Replace with your GitHub token (ciphered: U2FsdGVkX1+7TtLL8EZXcO+sDvRQ830mnmRH+1bPozCC3DDFIc4hyk/kAlvk6OBrlMhC6s/DVrAJypjnA/6zdQ==)
# set tokens at: https://github.com/settings/tokens
repo_owner = "ursa-mikail"
repo_name = "toolings"
branch = "main"
file_type = ".py"

# GitHub repo URL (token-authenticated)
repo_url = f"https://{username}:{token}@github.com/{repo_owner}/{repo_name}.git"
local_repo = f"/tmp/{repo_name}"

# --- Clone repo ---
if os.path.exists(local_repo):
    shutil.rmtree(local_repo)
print(f"Cloning {repo_url}...")
Repo.clone_from(repo_url, local_repo, branch=branch)
print("Clone completed.")

# --- Hash .py files ---
def hash_file(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

hashes = {}

for root, _, files in os.walk(local_repo):
    for fname in files:
        if fname.endswith(file_type):
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, local_repo)
            hashes[rel_path] = hash_file(fpath)

# --- Output results ---
print(f"\nSHA-256 Hashes of {file_type} files:")
for path, h in hashes.items():
    print(f"{path}: {h}")

"""
Cloning https://ursa-mikail:<token>@github.com/ursa-mikail/toolings.git...
Clone completed.

SHA-256 Hashes of .py files:
python/utilities/config_setup.py: 128f8c475244577ed7184cc5cf6d7c7a6e9ced223c507b278ab3a9e6e3fe82e6
python/json_data_extractor/json_data_extractor.py: 1bfa7604c8a6ce182cc4e06eb7f12953974a3e3bfa32715829d52fc086f08b3c
python/git/plot_git_commits_frequency.py: 1c8ef93c895a8e9f71a3f8d1fd17ad422d92c7f1b3fdb3caf81270a4d1bf44c1
python/git/git_commit_automated.py: 66ce4e0d4f4b30534eca36ba2bf7d726408e12a685beec2ced8547866c5920ed
python/git/plot_git_commits_frequency_with_mouse_over.py: e7207f9592bf1b7bea4b2c202e9e7fcce380e1b23eaca5c3984426a31834a1a7
python/git/get_git_commits_frequency.py: 928a62a0dbc2659262f48f5011b87d3b2d124a8e74c7ea7cc61988c0b5163517
python/git/clone_entire_repo_of_user.py: ab6ddad7f939e96db66131e282989ad4466a4f1d0e61d750b6e13702e01cf454
python/test_suites/test_suite_tool.py: 63ae48a1da3dc8a40a0caba338a064d96f473ba24005325e71dba1a642ca4619
python/test_suites/report_extraction_dieharder.py: 575cabe1772bd4887178a1690f36ab17874229a88652dc5e6273c144830fc5d1
python/benchmark_and_plots/benchmark_and_plots.py: 6d769a084cb1b008b536eb0e32b7cc1edac031fa736bc209d4b3e2ba64de8573
python/benchmark_and_plots/testbenches/scaling_k_of_N_with_factor_with_plot.py: e3bb0a7b09b242e12fdc4389bbb18f8e9d9c169505ed51015757ee73993773ba
python/benchmark_and_plots/testbenches/scaling_k_of_N_with_factor.py: dfbf5ed7882e73791a19dc175e2db794f8382da147acef8ab659a1ba59548670
"""