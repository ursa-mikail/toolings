package main

import (
	"archive/zip"
	"crypto/sha256"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
)

var files = []string{
	"main.go",
	"profile.go",
	"util.go",
}

const repo = "https://raw.githubusercontent.com/ursa-mikail/mechanisms/main/resource_profiling/go/"
const downloadDir = "downloaded"
const zipFile = "archived.zip"

func main() {
	os.MkdirAll(downloadDir, 0755)

	// Download and hash each file
	for _, file := range files {
		url := repo + file
		localPath := filepath.Join(downloadDir, file)
		fmt.Printf("📥 Downloading %s...\n", url)
		err := downloadFile(url, localPath)
		if err != nil {
			fmt.Printf("❌ Failed to download %s: %v\n", file, err)
			continue
		}
		hash, err := sha256File(localPath)
		if err != nil {
			fmt.Printf("❌ Hash error for %s: %v\n", file, err)
			continue
		}
		fmt.Printf("🔒 SHA256(%s): %x\n", file, hash)
	}

	// Zip all files
	fmt.Printf("📦 Zipping to %s...\n", zipFile)
	err := zipFiles(zipFile, downloadDir, files)
	if err != nil {
		fmt.Printf("❌ Zip error: %v\n", err)
		return
	}

	// Hash the zip
	zipHash, err := sha256File(zipFile)
	if err != nil {
		fmt.Printf("❌ Zip hash error: %v\n", err)
		return
	}
	fmt.Printf("🔒 SHA256(%s): %x\n", zipFile, zipHash)
}

// --- Download file from URL ---
func downloadFile(url, filepath string) error {
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	out, err := os.Create(filepath)
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = io.Copy(out, resp.Body)
	return err
}

// --- Compute SHA256 hash of a file ---
func sha256File(path string) ([]byte, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	h := sha256.New()
	if _, err := io.Copy(h, f); err != nil {
		return nil, err
	}
	return h.Sum(nil), nil
}

// --- Zip multiple files ---
func zipFiles(output string, basePath string, filenames []string) error {
	zipfile, err := os.Create(output)
	if err != nil {
		return err
	}
	defer zipfile.Close()

	archive := zip.NewWriter(zipfile)
	defer archive.Close()

	for _, file := range filenames {
		fpath := filepath.Join(basePath, file)
		f, err := os.Open(fpath)
		if err != nil {
			return err
		}
		defer f.Close()

		w, err := archive.Create(file)
		if err != nil {
			return err
		}

		_, err = io.Copy(w, f)
		if err != nil {
			return err
		}
	}

	return nil
}

/* curl_and_zip_files_from_git.go
% go mod tidy
% go run main.go
📥 Downloading https://raw.githubusercontent.com/ursa-mikail/mechanisms/main/resource_profiling/go/main.go...
🔒 SHA256(main.go): d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed
📥 Downloading https://raw.githubusercontent.com/ursa-mikail/mechanisms/main/resource_profiling/go/profile.go...
🔒 SHA256(profile.go): d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed
📥 Downloading https://raw.githubusercontent.com/ursa-mikail/mechanisms/main/resource_profiling/go/util.go...
🔒 SHA256(util.go): d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed
📦 Zipping to archived.zip...
🔒 SHA256(archived.zip): 0a225fdd3bb284da40d6fcf4e91481fdfbe2fd99f5b1b5bea7d229306bea7c22
*/
