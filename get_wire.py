import re
with open('/Users/jd/.gemini/antigravity/scratch/amai-exact/m-hub.html', 'r') as f:
    text = f.read()

match = re.search(r'function wire\(.*?\).*?^}', text, re.MULTILINE | re.DOTALL)
if match:
    print(match.group(0))

