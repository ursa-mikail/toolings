import requests
import pandas as pd

# Define the GitHub user
user = "ursa-mikail"

# GitHub API endpoint for user's repositories
repos_url = f"https://api.github.com/users/{user}/repos"

# Fetch all repositories
response = requests.get(repos_url)
repos_data = response.json()

# Initialize list to hold commit data
all_commits_data = []

# Loop through each repository
for repo in repos_data:
    repo_name = repo['name']
    print(f"Fetching commits for repository: {repo_name}")
    
    # GitHub API endpoint for commits in the repository
    commits_url = f"https://api.github.com/repos/{user}/{repo_name}/commits"
    
    page = 1
    while True:
        response = requests.get(commits_url, params={'per_page': 100, 'page': page})
        response_data = response.json()
        
        # Break the loop if no more commits are returned
        if len(response_data) == 0:
            break
        
        # Process the response data
        for commit in response_data:
            commit_date = commit['commit']['author']['date'][:10]  # Get the date (YYYY-MM-DD)
            #commit_date = commit_date.replace("-", ".")  # Replace '-' with '.'
            all_commits_data.append({'date': commit_date, 'repo': repo_name})
        
        # Go to the next page
        page += 1

# Convert list to DataFrame
df = pd.DataFrame(all_commits_data)

# Group by date and count commits per day
commit_counts = df.groupby(['date', 'repo']).size().reset_index(name='commits')

# Save to CSV
file_git_commits_csv = './sample_data/git_commits.csv'
commit_counts.to_csv(file_git_commits_csv, index=False)

print("CSV file 'git_commits.csv' created successfully.")

"""
Fetching commits for repository: chrome-ext-moon-phase
Fetching commits for repository: chrome-ext-utilities-timestamp-and-random-hex
Fetching commits for repository: cipher_js
Fetching commits for repository: flask-for-server_curl_simple
Fetching commits for repository: golang-gaia-basic-structure
Fetching commits for repository: jwt_rsa_ecc
Fetching commits for repository: mikail-eliyah.github.io
Fetching commits for repository: reference_codes
Fetching commits for repository: scrambler
Fetching commits for repository: shell_script_utility
Fetching commits for repository: templates
Fetching commits for repository: x509_js
CSV file 'git_commits.csv' created successfully.
"""