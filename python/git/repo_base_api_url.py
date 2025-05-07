from urllib.parse import urlparse
import requests

def parse_github_repo_url(url):
    parsed = urlparse(url)
    parts = parsed.path.strip('/').split('/')

    if len(parts) != 2:
        raise ValueError("URL must be in the form: https://github.com/{user}/{repo}")

    owner, repo = parts

    # Get default branch from GitHub API
    repo_info_url = f"https://api.github.com/repos/{owner}/{repo}"
    repo_info = requests.get(repo_info_url).json()
    default_branch = repo_info.get("default_branch", "main")

    # Starting API URL at repo root
    repo_api = f"https://api.github.com/repos/{owner}/{repo}/contents"
    raw_base = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}"

    return repo_api, raw_base, owner, repo, default_branch

# Example usage
repo_url = "https://github.com/ursa-mikail/mechanisms"
repo_api, raw_base, owner, repo, branch = parse_github_repo_url(repo_url)

print("GitHub API URL:", repo_api)
print("Raw Content Base URL:", raw_base)
print("Owner:", owner)
print("Repo:", repo)
print("Branch:", branch)

"""
GitHub API URL: https://api.github.com/repos/ursa-mikail/mechanisms/contents
Raw Content Base URL: https://raw.githubusercontent.com/ursa-mikail/mechanisms/main
Owner: ursa-mikail
Repo: mechanisms
Branch: main
"""