import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

# 1. Update all links to login.html -> hub.html
for file in html_files:
    if file in ('hub.html', 'm-hub.html', 'login.html', 'm-login.html'):
        continue
    with open(file, 'r') as f:
        content = f.read()
    
    # Replace href="login.html" with href="hub.html"
    new_content = content.replace('href="login.html"', 'href="hub.html"')
    # And specifically for mobile.html where it might have href="m-login.html"
    new_content = new_content.replace('href="m-login.html"', 'href="m-hub.html"')
    
    # Also fix the JS check in pages that replaces login.html -> hub.html if signed in
    new_content = new_content.replace("document.querySelectorAll(\"a[href*='login.html']\").forEach(function(el) {\n        el.href = \"hub.html\";\n      });", "")
    new_content = new_content.replace("document.querySelectorAll(\"a[href*='login.html']\").forEach(function(el) {\n      el.href = \"hub.html\";\n    });", "")

    if new_content != content:
        with open(file, 'w') as f:
            f.write(new_content)

# 2. Remove redirect from hub.html
with open('hub.html', 'r') as f:
    hub_content = f.read()

# Replace the redirect block
hub_redirect_pattern = r'<script>\s*try \{\s*var raw = localStorage.getItem\("amai_hub_v2"\), h = raw \? JSON\.parse\(raw\) : null;\s*if \(\!h \|\| \!h\.signedIn\) \{\s*window\.location\.replace\("login\.html"\);\s*\}\s*\} catch\(e\) \{\s*window\.location\.replace\("login\.html"\);\s*\}\s*</script>'
hub_content = re.sub(hub_redirect_pattern, '<script>\n  // Bypass auth for now\n</script>', hub_content, flags=re.DOTALL)

with open('hub.html', 'w') as f:
    f.write(hub_content)

# 3. Remove redirect from m-hub.html
with open('m-hub.html', 'r') as f:
    mhub_content = f.read()

mhub_redirect_pattern = r'const \{ data: \{ session \} \} = await sb\.auth\.getSession\(\);\s*if \(\!session\) \{\s*window\.location\.href = "m-login\.html";\s*return;\s*\}'
mhub_content = re.sub(mhub_redirect_pattern, '/* Bypass auth for now */', mhub_content, flags=re.DOTALL)

with open('m-hub.html', 'w') as f:
    f.write(mhub_content)

print("Done")
