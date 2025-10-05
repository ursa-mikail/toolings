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

def generate_html_diff(diff_lines, url1, url2):
    """Generate a complete HTML page with colored diff"""
    
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Colorful Diff Viewer</title>
    <style>
        body {{
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 14px;
            line-height: 1.4;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .diff-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 25px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            opacity: 0.8;
            margin-top: 8px;
        }}
        
        .file-info {{
            background: #ecf0f1;
            padding: 15px 25px;
            border-bottom: 1px solid #bdc3c7;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .file-original {{
            color: #e74c3c;
            font-weight: bold;
        }}
        
        .file-modified {{
            color: #27ae60;
            font-weight: bold;
        }}
        
        .timestamp {{
            color: #7f8c8d;
            font-size: 12px;
        }}
        
        .diff-content {{
            padding: 0;
        }}
        
        .diff-line {{
            display: flex;
            padding: 4px 8px;
            border-bottom: 1px solid #ecf0f1;
            transition: all 0.2s ease;
        }}
        
        .diff-line:hover {{
            background: #f8f9fa;
            transform: translateX(5px);
        }}
        
        .line-number {{
            min-width: 60px;
            text-align: right;
            padding-right: 15px;
            color: #95a5a6;
            font-size: 12px;
            border-right: 1px solid #ecf0f1;
            user-select: none;
        }}
        
        .line-content {{
            flex: 1;
            padding-left: 15px;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        
        /* Line type styles */
        .header-line {{
            background: #34495e;
            color: #ecf0f1;
            font-weight: bold;
            padding: 10px 25px;
        }}
        
        .hunk-header {{
            background: #fff3cd;
            color: #856404;
            font-weight: bold;
            padding: 8px 25px;
            border-left: 4px solid #ffc107;
        }}
        
        .removed {{
            background: #ffeaea;
            color: #c0392b;
            border-left: 4px solid #e74c3c;
        }}
        
        .added {{
            background: #e8f5e8;
            color: #27ae60;
            border-left: 4px solid #2ecc71;
        }}
        
        .context {{
            background: #f8f9fa;
            color: #2c3e50;
            border-left: 4px solid #bdc3c7;
        }}
        
        .metadata {{
            background: #d6eaf8;
            color: #2874a6;
            padding: 8px 25px;
            border-left: 4px solid #3498db;
        }}
        
        .statistics {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            margin-top: 20px;
            border-radius: 10px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
        }}
        
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .additions {{ color: #2ecc71; }}
        .deletions {{ color: #e74c3c; }}
        .hunks {{ color: #f39c12; }}
        .net-change {{ color: #3498db; }}
        
        .legend {{
            background: #ecf0f1;
            padding: 20px;
            margin-top: 20px;
            border-radius: 10px;
        }}
        
        .legend-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px;
            border-radius: 5px;
            background: white;
        }}
        
        .color-swatch {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
            border: 2px solid #bdc3c7;
        }}
        
        .swatch-removed {{ background: #ffeaea; border-color: #e74c3c; }}
        .swatch-added {{ background: #e8f5e8; border-color: #27ae60; }}
        .swatch-context {{ background: #f8f9fa; border-color: #bdc3c7; }}
        .swatch-hunk {{ background: #fff3cd; border-color: #ffc107; }}
        .swatch-header {{ background: #34495e; border-color: #2c3e50; }}
    </style>
</head>
<body>
    <div class="diff-container">
        <div class="header">
            <h1>🎨 Colorful Diff Viewer</h1>
            <div class="subtitle">Visual comparison of file differences</div>
        </div>
        
        <div class="file-info">
            <div>
                <span class="file-original">Original: {url1.split('/')[-1]}</span> | 
                <span class="file-modified">Modified: {url2.split('/')[-1]}</span>
            </div>
            <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="diff-content">
            {generate_diff_content(diff_lines)}
        </div>
        
        {generate_statistics(diff_lines)}
        {generate_legend()}
    </div>
</body>
</html>
    """
    
    return html_template

def generate_diff_content(diff_lines):
    """Generate the actual diff content with proper styling"""
    html_lines = []
    line_num_old = 0
    line_num_new = 0
    
    for line in diff_lines:
        if line.startswith('---'):
            html_lines.append(f'<div class="diff-line header-line">📁 {escape_html(line)}</div>')
        elif line.startswith('+++'):
            html_lines.append(f'<div class="diff-line header-line">📁 {escape_html(line)}</div>')
        elif line.startswith('@@'):
            # Parse hunk header to get line numbers
            parts = line.split(' ')
            if len(parts) >= 3:
                old_info = parts[1][1:] if parts[1].startswith('-') else parts[1]
                new_info = parts[2][1:] if parts[2].startswith('+') else parts[2]
                html_lines.append(f'<div class="diff-line hunk-header">🔧 {escape_html(line)}</div>')
        elif line.startswith('-'):
            line_num_old += 1
            html_lines.append(f'''
                <div class="diff-line removed">
                    <div class="line-number">{line_num_old}</div>
                    <div class="line-content">➖ {escape_html(line)}</div>
                </div>
            ''')
        elif line.startswith('+'):
            line_num_new += 1
            html_lines.append(f'''
                <div class="diff-line added">
                    <div class="line-number">{line_num_new}</div>
                    <div class="line-content">➕ {escape_html(line)}</div>
                </div>
            ''')
        elif line.startswith(' '):
            line_num_old += 1
            line_num_new += 1
            html_lines.append(f'''
                <div class="diff-line context">
                    <div class="line-number">{line_num_old}</div>
                    <div class="line-content">  {escape_html(line)}</div>
                </div>
            ''')
        else:
            html_lines.append(f'<div class="diff-line metadata">📋 {escape_html(line)}</div>')
    
    return '\n'.join(html_lines)

def generate_statistics(diff_lines):
    """Generate statistics section"""
    additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
    deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
    hunks = sum(1 for line in diff_lines if line.startswith('@@'))
    net_change = additions - deletions
    
    return f"""
    <div class="statistics">
        <h3>📊 Diff Statistics</h3>
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-number additions">+{additions}</div>
                <div>Additions</div>
            </div>
            <div class="stat-item">
                <div class="stat-number deletions">-{deletions}</div>
                <div>Deletions</div>
            </div>
            <div class="stat-item">
                <div class="stat-number hunks">{hunks}</div>
                <div>Hunks</div>
            </div>
            <div class="stat-item">
                <div class="stat-number net-change">{net_change:+d}</div>
                <div>Net Change</div>
            </div>
        </div>
    </div>
    """

def generate_legend():
    """Generate color legend section"""
    return """
    <div class="legend">
        <h3>📖 Color Legend</h3>
        <div class="legend-grid">
            <div class="legend-item">
                <div class="color-swatch swatch-removed"></div>
                <div><strong>Red</strong> - Removed lines</div>
            </div>
            <div class="legend-item">
                <div class="color-swatch swatch-added"></div>
                <div><strong>Green</strong> - Added lines</div>
            </div>
            <div class="legend-item">
                <div class="color-swatch swatch-context"></div>
                <div><strong>Gray</strong> - Context/unchanged lines</div>
            </div>
            <div class="legend-item">
                <div class="color-swatch swatch-hunk"></div>
                <div><strong>Yellow</strong> - Hunk headers</div>
            </div>
            <div class="legend-item">
                <div class="color-swatch swatch-header"></div>
                <div><strong>Blue</strong> - File headers</div>
            </div>
        </div>
    </div>
    """

def escape_html(text):
    """Escape HTML special characters"""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

def save_html_output(html_content, filename="diff_output.html"):
    """Save HTML content to file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return filename

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
            
        print("🎨 Generating HTML diff...")
        html_content = generate_html_diff(diff_result, url1, url2)
        
        output_file = save_html_output(html_content)
        print(f"💾 HTML diff saved to: {output_file}")
        print("🌐 Open this file in your browser to view the colorful diff!")
        
    except requests.RequestException as e:
        print(f"❌ Error downloading files: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()

"""
📥 Downloading files...
🔍 Generating diff...
🎨 Generating HTML diff...
💾 HTML diff saved to: diff_output.html
🌐 Open this file in your browser to view the colorful diff!
"""