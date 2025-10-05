# git_diff_viewer

## git_diff_viewer_with_html.py

To compare 2 files remotely, point to 2 files and run the program, and view with: 
http://htmlpreview.github.io/

to view:

http://htmlpreview.github.io/?https://raw.githubusercontent.com/ursa-mikail/toolings/main/python/git/git_diff_viewer/side_by_side_diff.html

i.e.
http://htmlpreview.github.io/?https://raw.githubusercontent.com/ursa-mikail/toolings/main/python/git/git_diff_viewer/side_by_side_diff.html


i.e.
http://htmlpreview.github.io/?https://raw.githubusercontent.com/ursa-mikail/toolings/main/python/git/git_diff_viewer/diff_output.html


# git_diff_viewer_colored.py
```
Key Features Added:
Rich Color Palette: Uses 256-color ANSI codes for vibrant colors
Visual Indicators: Emojis and symbols (➖, ➕, 📁, etc.)
Enhanced Headers: Fancy borders and timestamps
Statistics: Shows additions, deletions, and net changes
Color Legend: Explains what each color represents
Error Handling: Better error messages with emojis
Separate Color Class: Organized color management
```
```
Colors Used:
🔴 Red: Removed lines, original file headers
🟢 Green: Added lines, modified file headers
🟡 Yellow: Hunk headers with line numbers
🔵 Blue: Metadata and statistics
🟣 Purple/Magenta: Legends and highlights
⚫ Gray: Context/unchanged lines
🟠 Orange/Cyan: Various accents and borders
```