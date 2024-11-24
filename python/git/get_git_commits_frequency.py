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
        
        # Check if the response status code indicates an error
        if response.status_code != 200:
            print(f"Error fetching commits for repository: {repo_name}, page: {page}, status code: {response.status_code}")
            break
        
        response_data = response.json()
        
        # Check if the response contains an error message
        if isinstance(response_data, dict) and 'message' in response_data:
            print(f"Error message: {response_data['message']}")
            break
        
        # Break the loop if no more commits are returned
        if len(response_data) == 0:
            break
        
        # Process the response data
        for commit in response_data:
            try:
                commit_date = commit['commit']['author']['date'][:10]  # Get the date (YYYY-MM-DD)
                all_commits_data.append({'date': commit_date, 'repo': repo_name})
            except KeyError as e:
                print(f"KeyError: {e} in repo: {repo_name}, commit: {commit}")
        
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
