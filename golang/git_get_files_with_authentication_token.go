package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
)

var (
	// 🔧 Change this URL to your target GitHub folder or repo root
	staticGitHubURL = "https://github.com/ursa-mikail/mechanisms/tree/main/resource_profiling/go"
	githubToken     = "" // Optional: "ghp_..." # Replace with your GitHub token (ciphered: U2FsdGVkX1+7TtLL8EZXcO+sDvRQ830mnmRH+1bPozCC3DDFIc4hyk/kAlvk6OBrlMhC6s/DVrAJypjnA/6zdQ==)

	allowedExt = []string{".py", ".go"}
)

type GitHubItem struct {
	Name        string `json:"name"`
	Path        string `json:"path"`
	Type        string `json:"type"`
	DownloadURL string `json:"download_url"`
	URL         string `json:"url"`
}

func main() {
	repoPath, branch, subPath, err := parseGitHubURL(staticGitHubURL)
	if err != nil {
		fmt.Println("❌ URL parse error:", err)
		return
	}

	apiURL := fmt.Sprintf("https://api.github.com/repos/%s/contents/%s?ref=%s", repoPath, subPath, branch)
	fmt.Println("📥 Starting from:", apiURL)
	err = fetchRecursive(apiURL)
	if err != nil {
		fmt.Println("❌ Download error:", err)
	}
}

func parseGitHubURL(githubURL string) (repoPath, branch, path string, err error) {
	u, err := url.Parse(githubURL)
	if err != nil {
		return
	}
	parts := strings.Split(strings.Trim(u.Path, "/"), "/")
	if len(parts) < 2 {
		err = fmt.Errorf("URL must be in form github.com/{user}/{repo}")
		return
	}
	user := parts[0]
	repo := parts[1]
	repoPath = user + "/" + repo
	branch = "main"
	if len(parts) >= 5 && parts[2] == "tree" {
		branch = parts[3]
		path = strings.Join(parts[4:], "/")
	}
	return
}

func fetchRecursive(apiURL string) error {
	req, _ := http.NewRequest("GET", apiURL, nil)
	if githubToken != "" {
		req.Header.Set("Authorization", "token "+githubToken)
	}
	req.Header.Set("Accept", "application/vnd.github.v3+json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("GitHub API returned %d: %s", resp.StatusCode, string(body))
	}

	var items []GitHubItem
	if err := json.NewDecoder(resp.Body).Decode(&items); err != nil {
		return err
	}

	for _, item := range items {
		switch item.Type {
		case "file":
			if isAllowed(item.Name) {
				fmt.Println("📄 Downloading:", item.Path)
				if err := download(item.DownloadURL, item.Path); err != nil {
					fmt.Println("⚠️ Error:", err)
				}
			}
		case "dir":
			if err := fetchRecursive(item.URL); err != nil {
				fmt.Println("⚠️ Error in dir:", item.Path, err)
			}
		}
	}
	return nil
}

func isAllowed(name string) bool {
	for _, ext := range allowedExt {
		if strings.HasSuffix(name, ext) {
			return true
		}
	}
	return false
}

func download(rawURL, savePath string) error {
	resp, err := http.Get(rawURL)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	localPath := filepath.Join("downloaded", savePath)
	if err := os.MkdirAll(filepath.Dir(localPath), 0755); err != nil {
		return err
	}

	out, err := os.Create(localPath)
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = io.Copy(out, resp.Body)
	return err
}

/* git_get_files_with_authentication_token.go
% go mod tidy
% go run main.go
📥 Starting from: https://api.github.com/repos/ursa-mikail/mechanisms/contents/resource_profiling/go?ref=main
📄 Downloading: resource_profiling/go/magic_bytes_hunting.go
📄 Downloading: resource_profiling/go/memory_dumping_simulation.go
📄 Downloading: resource_profiling/go/memory_limit_test.go
*/
