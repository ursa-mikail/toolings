import requests
import difflib

def download_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def diff_files(content1, content2):
    diff = difflib.unified_diff(
        content1.splitlines(), content2.splitlines(),
        fromfile='file1', tofile='file2', lineterm=''
    )
    return list(diff)

def colorize_diff(diff_lines):
    """Apply colors to diff output based on line type"""
    colored_lines = []
    
    # ANSI color codes
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Colors for different parts
    HEADER = '\033[38;5;45m'  # Bright cyan for headers
    FILE_INFO = '\033[38;5;51m'  # Light cyan for file info
    REMOVED = '\033[38;5;196m'  # Bright red for removed lines
    ADDED = '\033[38;5;46m'    # Bright green for added lines
    CONTEXT = '\033[38;5;248m' # Gray for context lines
    HUNK_HEADER = '\033[38;5;226m'  # Yellow for hunk headers
    LINE_NUMBERS = '\033[38;5;141m'  # Purple for line numbers
    
    for line in diff_lines:
        if line.startswith('---') or line.startswith('+++'):
            # File headers
            colored_lines.append(f"{HEADER}{BOLD}{line}{RESET}")
        elif line.startswith('@@'):
            # Hunk headers with line numbers
            colored_lines.append(f"{HUNK_HEADER}{line}{RESET}")
        elif line.startswith('-'):
            # Removed lines
            colored_lines.append(f"{REMOVED}{line}{RESET}")
        elif line.startswith('+'):
            # Added lines
            colored_lines.append(f"{ADDED}{line}{RESET}")
        elif line.startswith(' '):
            # Context lines (unchanged)
            colored_lines.append(f"{CONTEXT}{line}{RESET}")
        else:
            # Any other metadata
            colored_lines.append(f"{FILE_INFO}{line}{RESET}")
    
    return colored_lines

def print_colored_diff(colored_lines):
    """Print colored diff with enhanced formatting"""
    print("\n" + "="*80)
    print("🎨 COLORFUL DIFF VIEWER")
    print("="*80)
    
    for line in colored_lines:
        print(line)
    
    print("="*80)
    print_legend()

def print_legend():
    """Print a color legend for the diff"""
    RESET = '\033[0m'
    REMOVED = '\033[38;5;196m'
    ADDED = '\033[38;5;46m'
    CONTEXT = '\033[38;5;248m'
    HUNK_HEADER = '\033[38;5;226m'
    HEADER = '\033[38;5;45m'
    
    print("\n📖 LEGEND:")
    print(f"{REMOVED}--- Removed lines{RESET}")
    print(f"{ADDED}+++ Added lines{RESET}")
    print(f"{CONTEXT}    Context/unchanged lines{RESET}")
    print(f"{HUNK_HEADER}@@ Hunk headers (line numbers){RESET}")
    print(f"{HEADER}---/+++ File headers{RESET}")

def main():
    url1 = "https://raw.githubusercontent.com/ursa-mikail/toolings/main/python/git/git_diff_viewer/files/product_old.py"
    url2 = "https://raw.githubusercontent.com/ursa-mikail/toolings/main/python/git/git_diff_viewer/files/product_new.py"

    try:
        print("📥 Downloading files...")
        content1 = download_file(url1)
        content2 = download_file(url2)
        
        print("🔍 Generating diff...")
        diff_result = diff_files(content1, content2)
        
        if not diff_result:
            print("✅ No differences found!")
            return
            
        colored_diff = colorize_diff(diff_result)
        print_colored_diff(colored_diff)
        
    except requests.RequestException as e:
        print(f"❌ Error downloading files: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()

