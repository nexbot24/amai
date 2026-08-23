import re

# Get footer from index.html
with open('index.html', 'r') as f:
    index_content = f.read()

# Extract from <!-- FOOTER --> to just before the closing </body> tag, but wait!
# In index.html, it's <div style="background:#241F1C;color:#B39C88">
# Let's extract the footer from index.html
footer_match = re.search(r'(<div style="background:#241F1C;color:#B39C88.*?)(?=\s*<template|<script>|\s*</body>)', index_content, re.DOTALL)
if not footer_match:
    print("Could not extract footer from index.html")
    exit(1)
footer_html = footer_match.group(1).strip()

files = ['services.html', 'contact.html']
for filename in files:
    with open(filename, 'r') as f:
        content = f.read()
    
    # In services.html, footer starts with <div style="background:#241F1C;color:#B39C88">
    # In contact.html, it might start with <div style="background:#241F1C;color:#B39C88;border-top:1px solid rgba(232,213,196,.14)">
    # Let's just find the last <div style="background:#241F1C;..."
    last_div_idx = content.rfind('<div style="background:#241F1C')
    if last_div_idx != -1:
        # replace from last_div_idx to the end, keeping the script we injected
        # The injected script starts with <script>\n(function(){
        end_idx = content.find('<script>\n(function(){', last_div_idx)
        if end_idx == -1:
            end_idx = content.find('</body>', last_div_idx)
            
        if end_idx != -1:
            new_content = content[:last_div_idx] + footer_html + "\n\n" + content[end_idx:]
            with open(filename, 'w') as f:
                f.write(new_content)
            print(f"Fixed footer in {filename}")

