import os
import re
import string
import requests
import networkx as nx
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk import download

# Download stopwords if not already present
download("stopwords")

# Config
USERNAME = "ursa-mikail"
USER_URL = f"https://github.com/{USERNAME}"
API_URL = f"https://api.github.com/users/{USERNAME}/repos"

# Get all public repos with pagination
def fetch_all_repos(username):
    page = 1
    all_repos = []
    while True:
        response = requests.get(f"{API_URL}?per_page=100&page={page}")
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        all_repos.extend(data)
        page += 1
    return all_repos

# Clean and extract keywords from text
def extract_keywords(text):
    stop_words = set(stopwords.words("english"))
    custom_stopwords = {"def", "return", "import", "from", "self", "none", "true", "false"}
    stop_words.update(custom_stopwords)

    words = re.findall(r'\b\w+\b', text.lower())
    return [
        word for word in words
        if word not in stop_words and not any(char.isdigit() for char in word) and len(word) > 2
    ]

# Build and plot graph
def build_graph(repos):
    G = nx.Graph()
    G.add_node(USER_URL, type="center")

    for repo in repos:
        repo_name = repo["name"]
        full_name = f"{USERNAME}/{repo_name}"
        description = repo.get("description") or ""
        G.add_node(full_name, type="repo")
        G.add_edge(USER_URL, full_name)

        keywords = extract_keywords(repo_name + " " + description)
        for kw in keywords:
            G.add_node(kw, type="keyword")
            G.add_edge(full_name, kw)

    # Position using spring layout
    pos = nx.spring_layout(G, k=0.5)

    # Node styles
    node_colors = []
    node_sizes = []
    for node in G.nodes:
        ntype = G.nodes[node].get("type", "")
        if ntype == "center":
            node_colors.append("red")
            node_sizes.append(800)
        elif ntype == "repo":
            node_colors.append("skyblue")
            node_sizes.append(500)
        else:  # keyword
            node_colors.append("lightgreen")
            node_sizes.append(300)

    # Draw graph
    plt.figure(figsize=(14, 10))
    nx.draw(
        G, pos, with_labels=True, node_color=node_colors, node_size=node_sizes,
        font_size=8, edge_color='gray', font_weight='bold'
    )
    plt.title(f"Keyword Network for {USERNAME}'s GitHub")
    plt.tight_layout()
    plt.show()

# Run all
if __name__ == "__main__":
    repos = fetch_all_repos(USERNAME)
    print(f"Fetched {len(repos)} repos.")
    build_graph(repos)

