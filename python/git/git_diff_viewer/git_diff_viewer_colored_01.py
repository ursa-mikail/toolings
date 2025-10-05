import requests
import difflib
from datetime import datetime

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

class ColorPalette:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # 256-color codes
    RED = '\033[38;5;196m'      # Bright red
    GREEN = '\033[38;5;46m'     # Bright green
    YELLOW = '\033[38;5;226m'   # Bright yellow
    BLUE = '\033[38;5;33m'      # Bright blue
    CYAN = '\033[38;5;51m'      # Bright cyan
    MAGENTA = '\033[38;5;201m'  # Bright magenta
    ORANGE = '\033[38;5;208m'   # Orange
    PURPLE = '\033[38;5;129m'   # Purple
    PINK = '\033[38;5;213m'     # Pink
    LIME = '\033[38;5;118m'     # Lime green
    TEAL = '\033[38;5;43m'      # Teal
    GRAY = '\033[38;5;248m'     # Gray
    DARK_GRAY = '\033[38;5;240m' # Dark gray

def colorize_diff_enhanced(diff_lines):
    """Apply enhanced coloring to diff output"""
    colored_lines = []
    c = ColorPalette()
    
    for line in diff_lines:
        if line.startswith('---'):
            # Original file
            colored_lines.append(f"{c.RED}{c.BOLD}📁 {line}{c.RESET}")
        elif line.startswith('+++'):
            # New file
            colored_lines.append(f"{c.GREEN}{c.BOLD}📁 {line}{c.RESET}")
        elif line.startswith('@@'):
            # Hunk header - extract and color parts separately
            parts = line.split(' ')
            if len(parts) >= 3:
                hunk_info = f"{c.YELLOW}{parts[0]}{c.RESET}"
                old_range = f"{c.RED}{parts[1]}{c.RESET}"
                new_range = f"{c.GREEN}{parts[2]}{c.RESET}"
                rest = f"{c.GRAY} {' '.join(parts[3:])}{c.RESET}" if len(parts) > 3 else ""
                colored_line = f"{hunk_info} {old_range} {new_range}{rest}"
                colored_lines.append(colored_line)
            else:
                colored_lines.append(f"{c.YELLOW}{line}{c.RESET}")
        elif line.startswith('-'):
            # Removed line with fancy marker
            colored_lines.append(f"{c.RED}➖ {line}{c.RESET}")
        elif line.startswith('+'):
            # Added line with fancy marker
            colored_lines.append(f"{c.GREEN}➕ {line}{c.RESET}")
        elif line.startswith(' '):
            # Context line
            colored_lines.append(f"{c.GRAY}  {line}{c.RESET}")
        else:
            # Other metadata
            colored_lines.append(f"{c.BLUE}{line}{c.RESET}")
    
    return colored_lines

def print_fancy_header(url1, url2):
    """Print a fancy header with file information"""
    c = ColorPalette()
    
    print(f"\n{c.CYAN}{'='*90}{c.RESET}")
    print(f"{c.CYAN}{c.BOLD}🎨 ENHANCED DIFF VIEWER{c.RESET}")
    print(f"{c.CYAN}{'='*90}{c.RESET}")
    print(f"{c.BLUE}🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{c.RESET}")
    print(f"{c.RED}📄 Original: {url1.split('/')[-1]}{c.RESET}")
    print(f"{c.GREEN}📄 Modified: {url2.split('/')[-1]}{c.RESET}")
    print(f"{c.CYAN}{'='*90}{c.RESET}\n")

def print_statistics(diff_lines):
    """Print diff statistics"""
    c = ColorPalette()
    
    additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
    deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
    hunks = sum(1 for line in diff_lines if line.startswith('@@'))
    
    print(f"\n{c.YELLOW}{c.BOLD}📊 DIFF STATISTICS:{c.RESET}")
    print(f"{c.GREEN}  ➕ Additions: {additions}{c.RESET}")
    print(f"{c.RED}  ➖ Deletions: {deletions}{c.RESET}")
    print(f"{c.BLUE}  🔧 Hunks: {hunks}{c.RESET}")
    print(f"{c.CYAN}  📈 Net change: {additions - deletions}{c.RESET}")

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
            
        print_fancy_header(url1, url2)
        colored_diff = colorize_diff_enhanced(diff_result)
        
        for line in colored_diff:
            print(line)
            
        print_statistics(diff_result)
        print_legend()
        
    except requests.RequestException as e:
        print(f"❌ Error downloading files: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def print_legend():
    """Print an enhanced color legend"""
    c = ColorPalette()
    
    print(f"\n{c.MAGENTA}{c.BOLD}📖 COLOR LEGEND:{c.RESET}")
    print(f"{c.RED}➖ - Removed lines{c.RESET}")
    print(f"{c.GREEN}➕ + Added lines{c.RESET}")
    print(f"{c.GRAY}    Context/unchanged lines{c.RESET}")
    print(f"{c.YELLOW}@@ Hunk headers (line numbers){c.RESET}")
    print(f"{c.RED}📁 --- Original file{c.RESET}")
    print(f"{c.GREEN}📁 +++ Modified file{c.RESET}")
    print(f"{c.CYAN}{'='*90}{c.RESET}")

if __name__ == "__main__":
    main()

