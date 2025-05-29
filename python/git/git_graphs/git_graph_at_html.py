# output to html

import os
import re
import requests
import networkx as nx
import plotly.graph_objects as go
from nltk.corpus import stopwords
from nltk import download

# Ensure NLTK stopwords are available
download("stopwords")

# Config
USERNAME = "ursa-mikail"
USER_URL = f"https://github.com/{USERNAME}"
API_URL = f"https://api.github.com/users/{USERNAME}/repos"

# Get all repositories (paginated)
def fetch_all_repos(username):
    all_repos = []
    page = 1
    while True:
        response = requests.get(f"{API_URL}?per_page=100&page={page}")
        if response.status_code != 200:
            break
        page_repos = response.json()
        if not page_repos:
            break
        all_repos.extend(page_repos)
        page += 1
    return all_repos

# Extract cleaned keywords
def extract_keywords(text):
    stop_words = set(stopwords.words("english"))
    custom_stopwords = {
        "def", "return", "import", "from", "self", "none", "true", "false",
        "https", "http", "github", "com"
    }
    stop_words.update(custom_stopwords)

    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return [word for word in words if word not in stop_words]

# Build interactive graph
def build_interactive_graph(repos):
    G = nx.Graph()
    G.add_node(USER_URL, type="center")

    for repo in repos:
        repo_name = f"{USERNAME}/{repo['name']}"
        description = repo.get("description") or ""
        G.add_node(repo_name, type="repo")
        G.add_edge(USER_URL, repo_name)

        keywords = extract_keywords(repo_name + " " + description)
        for kw in keywords:
            G.add_node(kw, type="keyword")
            G.add_edge(repo_name, kw)

    pos = nx.spring_layout(G, k=0.5, seed=42)
    edge_x = []
    edge_y = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    node_x, node_y, node_text, node_color, node_size = [], [], [], [], []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        ntype = G.nodes[node].get("type")
        node_text.append(node)

        if ntype == "center":
            node_color.append("red")
            node_size.append(20)
        elif ntype == "repo":
            node_color.append("blue")
            node_size.append(14)
        else:
            node_color.append("green")
            node_size.append(10)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line_width=1
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=f"<b>Keyword Graph for {USERNAME}</b>",
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=[dict(
                            text="Drag, zoom, and explore",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002
                        )],
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False)
                    ))

    fig.write_html("keyword_graph.html")
    print("✅ Saved interactive graph as 'keyword_graph.html'")

# Run it
if __name__ == "__main__":
    repos = fetch_all_repos(USERNAME)
    print(f"Fetched {len(repos)} repos.")
    build_interactive_graph(repos)

"""
[nltk_data] Downloading package stopwords to /root/nltk_data...
[nltk_data]   Package stopwords is already up-to-date!
Fetched 98 repos.
✅ Saved interactive graph as 'keyword_graph.html'
"""