#@title Git Diff Viewer with Colored Output
import requests
import os
import base64
from IPython.display import display, HTML

# Configuration
github_user = "ursa-mikail"
repo_name = "toolings"
branch = "main"
files_to_be_compares = ['product_old.py', 'product_new.py']
file_path_old = "python/git/git_diff_viewer/files/" + files_to_be_compares[0]
file_path_new = "python/git/git_diff_viewer/files/" + files_to_be_compares[1]

class ColoredDiff:
    @staticmethod
    def red(text):
        return f"\033[91m{text}\033[0m"
    
    @staticmethod
    def green(text):
        return f"\033[92m{text}\033[0m"
    
    @staticmethod
    def blue(text):
        return f"\033[94m{text}\033[0m"
    
    @staticmethod
    def yellow(text):
        return f"\033[93m{text}\033[0m"
    
    @staticmethod
    def bold(text):
        return f"\033[1m{text}\033[0m"

def download_files():
    """Download files from GitHub"""
    print("📥 Downloading files from GitHub...")
    
    files = {
        files_to_be_compares[0]: file_path_old,
        files_to_be_compares[1]: file_path_new
    }
    
    downloaded_files = {}
    
    for filename, path in files.items():
        # Try raw.githubusercontent.com
        url = f"https://raw.githubusercontent.com/{github_user}/{repo_name}/{branch}/{path}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                downloaded_files[filename] = filename
                print(f"✅ {ColoredDiff.green('Downloaded')} {filename}")
            else:
                print(f"❌ {ColoredDiff.red('Failed to download')} {filename}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {ColoredDiff.red('Error downloading')} {filename}: {e}")
    
    return downloaded_files

def generate_colored_diff():
    """Generate colored diff between the two files"""
    if not all(os.path.exists(f) for f in files_to_be_compares):
        print(f"❌ {ColoredDiff.red('Required files not found')}")
        return
    
    print(f"\n🎨 {ColoredDiff.bold('GENERATING COLORED DIFF')}")
    print("=" * 80)
    
    with open(files_to_be_compares[0], 'r', encoding='utf-8') as f1, \
         open(files_to_be_compares[1], 'r', encoding='utf-8') as f2:
        old_lines = f1.readlines()
        new_lines = f2.readlines()
    
    # Find differences
    max_lines = max(len(old_lines), len(new_lines))
    differences = []
    
    for i in range(max_lines):
        old_line = old_lines[i] if i < len(old_lines) else ""
        new_line = new_lines[i] if i < len(new_lines) else ""
        
        if old_line != new_line:
            differences.append((i + 1, old_line.rstrip(), new_line.rstrip()))
    
    # Display colored diff
    if not differences:
        print(f"✅ {ColoredDiff.green('No differences found - files are identical!')}")
        return
    
    print(f"📊 {ColoredDiff.blue('Found')} {len(differences)} {ColoredDiff.blue('differences:')}\n")
    
    for line_num, old_line, new_line in differences:
        print(f"{ColoredDiff.yellow('Line')} {ColoredDiff.bold(str(line_num))}:")
        
        if old_line and new_line:
            # Both lines exist but are different
            print(f"  {ColoredDiff.red('- OLD:')} {ColoredDiff.red(old_line)}")
            print(f"  {ColoredDiff.green('+ NEW:')} {ColoredDiff.green(new_line)}")
        elif old_line and not new_line:
            # Line was removed
            print(f"  {ColoredDiff.red('- OLD:')} {ColoredDiff.red(old_line)} {ColoredDiff.red('(REMOVED)')}")
        elif not old_line and new_line:
            # Line was added
            print(f"  {ColoredDiff.green('+ NEW:')} {ColoredDiff.green(new_line)} {ColoredDiff.green('(ADDED)')}")
        
        print()

def generate_unified_colored_diff():
    """Generate unified diff with color (like git diff)"""
    if not all(os.path.exists(f) for f in files_to_be_compares):
        return
    
    print(f"\n🔄 {ColoredDiff.bold('UNIFIED DIFF VIEW')}")
    print("=" * 80)
    
    with open(files_to_be_compares[0], 'r', encoding='utf-8') as f1, \
         open(files_to_be_compares[1], 'r', encoding='utf-8') as f2:
        old_lines = [line.rstrip() for line in f1]
        new_lines = [line.rstrip() for line in f2]
    
    # Simple unified diff algorithm
    i = j = 0
    changes = []
    
    while i < len(old_lines) or j < len(new_lines):
        if i < len(old_lines) and j < len(new_lines) and old_lines[i] == new_lines[j]:
            # Lines are equal
            changes.append((' ', old_lines[i]))
            i += 1
            j += 1
        else:
            # Look for additions/removals
            added = []
            removed = []
            
            # Check if this is a removal
            remove_search = old_lines[i] if i < len(old_lines) else None
            if remove_search and remove_search not in new_lines[j:j+3]:
                removed.append(old_lines[i])
                i += 1
            
            # Check if this is an addition  
            add_search = new_lines[j] if j < len(new_lines) else None
            if add_search and add_search not in old_lines[i:i+3]:
                added.append(new_lines[j])
                j += 1
            
            if removed or added:
                changes.append(('-', removed[0] if removed else ''))
                changes.append(('+', added[0] if added else ''))
            else:
                # Context line
                if i < len(old_lines):
                    changes.append((' ', old_lines[i]))
                    i += 1
                if j < len(new_lines):
                    changes.append((' ', new_lines[j]))
                    j += 1
    
    # Display unified diff
    context_lines = 2
    in_change_block = False
    
    for idx, (change_type, line) in enumerate(changes):
        if change_type == '-':
            if not in_change_block:
                print(f"{ColoredDiff.blue('@@ -%d,%d +%d,%d @@' % (max(1, idx-context_lines), context_lines*2, max(1, idx-context_lines), context_lines*2))}")
                in_change_block = True
            
            # Show previous context
            for ctx_idx in range(max(0, idx-context_lines), idx):
                if ctx_idx < len(changes) and changes[ctx_idx][0] == ' ':
                    print(f" {changes[ctx_idx][1]}")
            
            print(f"{ColoredDiff.red('-')}{ColoredDiff.red(line)}")
            in_change_block = True
        elif change_type == '+':
            print(f"{ColoredDiff.green('+')}{ColoredDiff.green(line)}")
        else:
            if in_change_block:
                # Show following context
                for ctx_idx in range(idx, min(len(changes), idx+context_lines)):
                    if changes[ctx_idx][0] == ' ':
                        print(f" {changes[ctx_idx][1]}")
                print()
                in_change_block = False

def generate_side_by_side_colored():
    """Generate side-by-side comparison with color"""
    if not all(os.path.exists(f) for f in files_to_be_compares):
        return
    
    print(f"\n📑 {ColoredDiff.bold('SIDE-BY-SIDE COMPARISON')}")
    print("=" * 100)
    
    with open(files_to_be_compares[0], 'r', encoding='utf-8') as f1, \
         open(files_to_be_compares[1], 'r', encoding='utf-8') as f2:
        old_lines = [line.rstrip() for line in f1]
        new_lines = [line.rstrip() for line in f2]
    
    max_lines = max(len(old_lines), len(new_lines))
    
    # Fixed: Apply format specifier to the entire colored string
    old_header = ColoredDiff.red('OLD ('+ files_to_be_compares[0] +')')
    new_header = ColoredDiff.green('| NEW ('+ files_to_be_compares[1] +')')
    print(f"{old_header:<54} {new_header}")
    print("-" * 90)
    
    for i in range(max_lines):
        old_line = old_lines[i] if i < len(old_lines) else ""
        new_line = new_lines[i] if i < len(new_lines) else ""
        
        # Color coding
        if old_line != new_line:
            old_display = ColoredDiff.red(old_line[:43]) if old_line else ""
            new_display = ColoredDiff.green(new_line[:43]) if new_line else ""
            marker = f" {ColoredDiff.yellow('>>>')}"
        else:
            old_display = old_line[:43] if old_line else ""
            new_display = new_line[:43] if new_line else ""
            marker = ""
        
        # Fixed: Remove format specifier from inside the f-string
        print(f"{old_display:<52} {ColoredDiff.blue('|')} {new_display}{marker}")

def generate_side_by_side_html():
    """Generate side-by-side comparison in HTML format and save to file"""
    if not all(os.path.exists(f) for f in files_to_be_compares):
        return None
    
    with open(files_to_be_compares[0], 'r', encoding='utf-8') as f1, \
         open(files_to_be_compares[1], 'r', encoding='utf-8') as f2:
        old_lines = [line.rstrip() for line in f1]
        new_lines = [line.rstrip() for line in f2]
    
    max_lines = max(len(old_lines), len(new_lines))
    
    html_output = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Side-by-Side Diff: {files_to_be_compares[0]} vs {files_to_be_compares[1]}</title>
    <style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #ffffff;
        margin: 20px;
        padding: 0;
    }}
    .side-by-side-container {{ 
        font-family: 'Courier New', monospace; 
        background: #f8f9fa; 
        padding: 20px; 
        border-radius: 8px;
        margin: 20px auto;
        max-width: 1400px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .side-by-side-header {{ 
        background: #f1f8ff; 
        padding: 15px; 
        margin-bottom: 15px; 
        border-radius: 5px;
        font-weight: bold;
        font-size: 18px;
        color: #0366d6;
        border-left: 4px solid #0366d6;
    }}
    .side-by-side-table {{
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 5px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    .side-by-side-table th {{
        background: #24292e;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
        font-size: 14px;
    }}
    .side-by-side-table td {{
        padding: 8px 12px;
        border-bottom: 1px solid #e1e4e8;
        vertical-align: top;
        font-size: 13px;
        line-height: 1.5;
    }}
    .side-by-side-table tr:hover {{
        background: #f6f8fa;
    }}
    .old-column {{ 
        background: #ffeef0; 
        color: #24292e;
        width: 48%;
    }}
    .new-column {{ 
        background: #e6ffed; 
        color: #24292e;
        width: 48%;
    }}
    .separator {{ 
        width: 4%;
        text-align: center;
        color: #0366d6;
        font-weight: bold;
        background: #f6f8fa;
    }}
    .line-changed-old {{ background: #ffeef0; }}
    .line-changed-new {{ background: #e6ffed; }}
    .line-unchanged {{ background: white; }}
    .line-number {{
        color: #6a737d;
        font-weight: bold;
        padding-right: 8px;
        display: inline-block;
        min-width: 40px;
    }}
    .change-marker {{
        color: #f39c12;
        font-weight: bold;
        padding-left: 10px;
    }}
    .footer {{
        text-align: center;
        padding: 20px;
        color: #6a737d;
        font-size: 12px;
    }}
    </style>
</head>
<body>
    <div class="side-by-side-container">
        <div class="side-by-side-header">
            📑 Side-by-Side Comparison: {files_to_be_compares[0]} vs {files_to_be_compares[1]}
        </div>
        <table class="side-by-side-table">
            <thead>
                <tr>
                    <th class="old-column">OLD ({files_to_be_compares[0]})</th>
                    <th class="separator">|</th>
                    <th class="new-column">NEW ({files_to_be_compares[1]})</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for i in range(max_lines):
        old_line = old_lines[i] if i < len(old_lines) else ""
        new_line = new_lines[i] if i < len(new_lines) else ""
        line_num = i + 1
        
        # Escape HTML characters
        old_line_escaped = old_line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        new_line_escaped = new_line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Determine styling
        if old_line != new_line:
            old_class = "line-changed-old"
            new_class = "line-changed-new"
            marker = '<span class="change-marker">◄►</span>'
        else:
            old_class = "line-unchanged"
            new_class = "line-unchanged"
            marker = ""
        
        html_output += f"""
            <tr>
                <td class="{old_class}">
                    <span class="line-number">{line_num:3d}</span>{old_line_escaped}
                </td>
                <td class="separator">|</td>
                <td class="{new_class}">
                    <span class="line-number">{line_num:3d}</span>{new_line_escaped}{marker}
                </td>
            </tr>
        """
    
    html_output += """
            </tbody>
        </table>
        <div class="footer">
            Generated by Git Diff Viewer | 🔴 Red background = removed/changed | 🟢 Green background = added/changed | ◄► = modified line
        </div>
    </div>
</body>
</html>
    """
    
    # Save to file
    output_filename = "side_by_side_diff.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    # Also display in Colab
    display(HTML(html_output))
    
    return output_filename

def show_file_preview():
    """Show preview of both files with line numbers"""
    if not all(os.path.exists(f) for f in files_to_be_compares):
        return
    
    print(f"\n📄 {ColoredDiff.bold('FILE PREVIEW')}")
    print("=" * 80)
    
    for filename in files_to_be_compares:
        print(f"\n{ColoredDiff.bold(filename)}:")
        print("-" * 40)
        
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            for i, line in enumerate(lines[:10]):  # Show first 10 lines
                line_num = i + 1
                print(f"{ColoredDiff.yellow(str(line_num).zfill(2))}: {line.rstrip()}")
            
            if len(lines) > 10:
                print(f"{ColoredDiff.blue('...')} ({len(lines) - 10} more lines)")

def show_change_summary():
    """Show summary of changes with statistics"""
    if not all(os.path.exists(f) for f in files_to_be_compares):
        return
    
    with open(files_to_be_compares[0], 'r', encoding='utf-8') as f1, \
         open(files_to_be_compares[1], 'r', encoding='utf-8') as f2:
        old_content = f1.read()
        new_content = f2.read()
    
    old_lines = old_content.split('\n')
    new_lines = new_content.split('\n')
    
    added = set(new_lines) - set(old_lines)
    removed = set(old_lines) - set(new_lines)
    common = set(old_lines) & set(new_lines)
    
    print(f"\n📈 {ColoredDiff.bold('CHANGE SUMMARY')}")
    print("=" * 80)
    
    print(f"{ColoredDiff.blue('Total lines (old):')} {len(old_lines)}")
    print(f"{ColoredDiff.blue('Total lines (new):')} {len(new_lines)}")
    print(f"{ColoredDiff.green('Lines added:')} {len(added)}")
    print(f"{ColoredDiff.red('Lines removed:')} {len(removed)}")
    print(f"{ColoredDiff.yellow('Common lines:')} {len(common)}")
    
    if added:
        print(f"\n{ColoredDiff.green('➕ ADDED LINES:')}")
        for line in list(added)[:3]:
            if line.strip():
                print(f"  {ColoredDiff.green('+')} {line[:60]}{'...' if len(line) > 60 else ''}")
        if len(added) > 3:
            print(f"  {ColoredDiff.blue('... and')} {len(added) - 3} {ColoredDiff.blue('more')}")
    
    if removed:
        print(f"\n{ColoredDiff.red('➖ REMOVED LINES:')}")
        for line in list(removed)[:3]:
            if line.strip():
                print(f"  {ColoredDiff.red('-')} {line[:60]}{'...' if len(line) > 60 else ''}")
        if len(removed) > 3:
            print(f"  {ColoredDiff.blue('... and')} {len(removed) - 3} {ColoredDiff.blue('more')}")

# Main execution
print(f"🚀 {ColoredDiff.bold('Git Diff Viewer with Colored Output')}")
print("=" * 60)

# Download files
downloaded = download_files()

if len(downloaded) == 2:
    # Show file preview
    show_file_preview()
    
    # Generate various diff views
    generate_colored_diff()           # Line-by-line colored diff
    generate_unified_colored_diff()   # Git-style unified diff
    generate_side_by_side_colored()   # Side-by-side comparison
    
    # Show summary
    show_change_summary()
    
    # Generate HTML side-by-side view
    print(f"\n🌐 {ColoredDiff.bold('Generating HTML Side-by-Side View...')}")
    html_file = generate_side_by_side_html()
    
    print(f"\n✅ {ColoredDiff.green('Analysis complete!')}")
    print(f"📁 {ColoredDiff.blue('Files downloaded:')} {', '.join(downloaded.keys())}")
    
    if html_file:
        print(f"\n📄 {ColoredDiff.bold('HTML Output File:')} {ColoredDiff.yellow(html_file)}")
        print(f"   {ColoredDiff.blue('→ You can open this file in any web browser')}")
        print(f"   {ColoredDiff.blue('→ The HTML is also displayed above in Colab')}")
else:
    print(f"\n❌ {ColoredDiff.red('Could not download both files. Analysis aborted.')}")

#@title HTML Colored Diff (Better for Colab)
import requests
from IPython.display import display, HTML

def create_html_diff():
    """Create HTML formatted diff for better display in Colab"""
    
    # Download files
    old_url = f"https://raw.githubusercontent.com/{github_user}/{repo_name}/{branch}/{file_path_old}"
    new_url = f"https://raw.githubusercontent.com/{github_user}/{repo_name}/{branch}/{file_path_new}"
    
    try:
        old_content = requests.get(old_url).text.split('\n')
        new_content = requests.get(new_url).text.split('\n')
    except:
        print("❌ Could not download files")
        return
    
    # Generate HTML diff
    html_output = f"""
    <style>
    .diff-container {{ font-family: monospace; background: #f8f9fa; padding: 15px; border-radius: 5px; }}
    .diff-line {{ margin: 2px 0; padding: 2px 5px; }}
    .diff-old {{ background: #ffeef0; color: #cb2431; }}
    .diff-new {{ background: #e6ffed; color: #22863a; }}
    .diff-unchanged {{ background: white; color: #24292e; }}
    .diff-line-number {{ color: #6a737d; padding-right: 10px; }}
    .diff-header {{ background: #f1f8ff; padding: 10px; margin-bottom: 10px; border-radius: 3px; }}
    </style>
    
    <div class="diff-header">
        <h3>🎨 Colored Diff: {files_to_be_compares[0]} vs {files_to_be_compares[1]}</h3>
    </div>
    <div class="diff-container">
    """
    
    max_lines = max(len(old_content), len(new_content))
    
    for i in range(max_lines):
        old_line = old_content[i] if i < len(old_content) else ""
        new_line = new_content[i] if i < len(new_content) else ""
        
        line_num = i + 1
        
        if old_line != new_line:
            if old_line and new_line:
                # Modified line
                html_output += f'<div class="diff-line diff-old"><span class="diff-line-number">{line_num}</span>- {old_line}</div>'
                html_output += f'<div class="diff-line diff-new"><span class="diff-line-number">{line_num}</span>+ {new_line}</div>'
            elif old_line:
                # Removed line
                html_output += f'<div class="diff-line diff-old"><span class="diff-line-number">{line_num}</span>- {old_line} <em>(removed)</em></div>'
            elif new_line:
                # Added line
                html_output += f'<div class="diff-line diff-new"><span class="diff-line-number">{line_num}</span>+ {new_line} <em>(added)</em></div>'
        else:
            # Unchanged line
            html_output += f'<div class="diff-line diff-unchanged"><span class="diff-line-number">{line_num}</span>  {old_line}</div>'
    
    html_output += "</div>"
    
    display(HTML(html_output))

# Run HTML diff
create_html_diff()

"""
🔴 Red: Lines removed/changed in old file
🟢 Green: Lines added/changed in new file
🟡 Yellow: Line numbers and markers
🔵 Blue: Headers and statistics
"""