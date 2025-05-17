package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

type TreeResponse struct {
	Tree []struct {
		Path string `json:"path"`
		Type string `json:"type"`
	} `json:"tree"`
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}

func writeJSONFile(path string, data map[string]interface{}) {
	f, err := os.Create(path)
	must(err)
	defer f.Close()
	enc := json.NewEncoder(f)
	enc.SetIndent("", "  ")
	must(enc.Encode(data))
}

func getGitHubToken() string {
	// Safe handling of tokens (replace this with secure method in production)
	token := os.Getenv("GITHUB_TOKEN")
	if token == "" {
		panic("GITHUB_TOKEN env variable not set")
	}
	return token
}

func main() {
	username := "ursa-mikail"
	token := getGitHubToken()

	repoOwner := "ursa-mikail"
	repoName := "templates"
	repoURL := fmt.Sprintf("https://%s:%s@github.com/%s/%s.git", username, token, repoOwner, repoName)
	localRepo := filepath.Join(os.TempDir(), repoName)
	json0 := filepath.Join(localRepo, "hash_data_00.json")
	json1 := filepath.Join(localRepo, "hash_data_01.json")

	// Step 1: Cleanup old repo if exists
	os.RemoveAll(localRepo)

	// Step 2: Clone repo
	cmd := exec.Command("git", "clone", repoURL, localRepo)
	must(cmd.Run())
	fmt.Println("✅ Cloned repository")

	// Step 3: Create hash_data_00.json
	now := time.Now()
	hashes := map[string]interface{}{
		"user1":          "babe00ca5e0065d61d8327deb882cf99",
		"user2":          fmt.Sprintf("%x", sha256.Sum256([]byte(time.Now().String()))), // random
		"timestamp":      now.Format("2006-01-02_1504:05"),
		"timestamp_unix": now.Unix(),
	}
	writeJSONFile(json0, hashes)
	fmt.Println("✅ Created hash_data_00.json")

	// Step 4: Fetch and hash files from GitHub folder
	owner, repo, branch := "ursa-mikail", "mechanisms", "main"
	remoteDir := "security"
	apiURL := fmt.Sprintf("https://api.github.com/repos/%s/%s/git/trees/%s?recursive=1", owner, repo, branch)

	resp, err := http.Get(apiURL)
	must(err)
	defer resp.Body.Close()

	var treeResp TreeResponse
	must(json.NewDecoder(resp.Body).Decode(&treeResp))

	hashes1 := make(map[string]string)
	for _, item := range treeResp.Tree {
		if item.Type == "blob" && strings.HasPrefix(item.Path, remoteDir+"/") {
			rawURL := fmt.Sprintf("https://raw.githubusercontent.com/%s/%s/%s/%s", owner, repo, branch, item.Path)
			fileResp, err := http.Get(rawURL)
			if err != nil {
				fmt.Printf("❌ Error downloading %s: %v\n", item.Path, err)
				continue
			}
			defer fileResp.Body.Close()

			hasher := sha256.New()
			_, err = io.Copy(hasher, fileResp.Body)
			if err != nil {
				fmt.Printf("❌ Error hashing %s: %v\n", item.Path, err)
				continue
			}
			hash := hex.EncodeToString(hasher.Sum(nil))
			hashes1[item.Path] = hash
			fmt.Printf("✅ %s: %s\n", item.Path, hash)
		}
	}

	writeJSONFile(json1, map[string]interface{}{
		"files":    hashes1,
		"fetched":  time.Now().Format(time.RFC3339),
		"source":   fmt.Sprintf("https://github.com/%s/%s/tree/%s/%s", owner, repo, branch, remoteDir),
		"hashType": "SHA-256",
	})
	fmt.Println("✅ Created hash_data_01.json")

	// Step 5: Commit and push both JSON files
	os.Chdir(localRepo)
	must(exec.Command("git", "add", ".").Run())
	must(exec.Command("git", "commit", "-m", "Add hash_data_00.json and hash_data_01.json").Run())
	must(exec.Command("git", "push").Run())

	fmt.Println("✅ hash_data_00.json and hash_data_01.json committed and pushed.")

	// Delete file, commit and push
	if err := os.Remove(json0); err != nil {
		panic(err)
	}
	must(exec.Command("git", "add", ".").Run())
	must(exec.Command("git", "commit", "-m", fmt.Sprintf("Remove --- %s", json0)).Run())
	must(exec.Command("git", "push").Run())

	fmt.Printf("✅ JSON: %s pushed and deleted successfully.\n", json0)
}

/* git_get_files_with_authentication_token_and_commit_hashes_to_git.go
% go mod tidy
% go run main.go
✅ Cloned repository
✅ Created hash_data_00.json
✅ security/confidentiality/go/asymmetric/generate_ecdsa_and_eddsa_certs.go: 610d2ba28171be6ccae6f64f5ef6845c05b4474eca98d2bc139f03e82a9ab96e
✅ security/confidentiality/python/aes_log_exclusive_access.py: 15019787e87b6473520e92c66cbaec4571d591ce48c7048d58aa11fa10c24622
✅ security/confidentiality/python/generate_key_split_and_recovery.py: ff6c5c3c121286443a50e1a7b53aecc299e579c0510ba21c3bb242046236524a
✅ security/confidentiality/python/readme.md: ba44ab10881244ca5fd1c198666ea4954b972cacb48be4e4e6212f46f17f2d62
:
✅ Created hash_data_01.json
✅ hash_data_00.json and hash_data_01.json committed and pushed.

	username := "ursa-mikail"
	token := "U2FsdGVkX1+7TtLL8EZXcO+sDvRQ830mnmRH+1bPozCC3DDFIc4hyk/kAlvk6OBrlMhC6s/DVrAJypjnA/6zdQ==" // "YOUR_TOKEN_HERE" // Replace with your GitHub token (ciphered: U2FsdGVkX1+7TtLL8EZXcO+sDvRQ830mnmRH+1bPozCC3DDFIc4hyk/kAlvk6OBrlMhC6s/DVrAJypjnA/6zdQ==)

	export GITHUB_TOKEN="U2FsdGVkX1+7TtLL8EZXcO+sDvRQ830mnmRH+1bPozCC3DDFIc4hyk/kAlvk6OBrlMhC6s/DVrAJypjnA/6zdQ=="

*/
