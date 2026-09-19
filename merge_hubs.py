import re

with open("/Users/jd/.gemini/antigravity/scratch/amai-exact/hub.html", "r") as f:
    desktop = f.read()

with open("/Users/jd/.gemini/antigravity/scratch/amai-exact/m-hub.html", "r") as f:
    mobile = f.read()

def get_block(regex, text, flags=re.DOTALL):
    m = re.search(regex, text, flags)
    return m.group(1) if m else ""

# Extract desktop CSS
desktop_css = get_block(r"<style>(.*?)</style>", desktop)
mobile_css = get_block(r"<style>(.*?)</style>", mobile)

# Scoping CSS: we can wrap the CSS in a class using modern CSS nesting.
# But wait, mobile body and html styles. 
# Desktop global styles:
desktop_css = desktop_css.replace("body{", ".desktop-shell{").replace("*,*::before,*::after{", ".desktop-shell *,.desktop-shell *::before,.desktop-shell *::after{")
mobile_css = mobile_css.replace("body{", ".mobile-shell{").replace("html{", ".mobile-shell{").replace("*,*::before,*::after{", ".mobile-shell *,.mobile-shell *::before,.mobile-shell *::after{")

scoped_css = f"""
.mobile-shell {{ display: none; }}
@media(max-width:860px) {{
  .desktop-shell {{ display: none !important; }}
  .mobile-shell {{ display: block; }}
}}
.desktop-shell {{ {desktop_css} }}
.mobile-shell {{ {mobile_css} }}
"""

# Extract HTML 
desktop_body = get_block(r"<body>(.*?)<script src=", desktop)
mobile_body = get_block(r"<body>(.*?)<script src=", mobile)

# Replace `#m-auth` with `#m-auth` inside `.mobile-shell` context
# Actually, we can wrap the entire desktop HTML in `<div class="desktop-shell">` and mobile in `<div class="mobile-shell">`

# Wait, we need to extract desktop JS and mobile JS
desktop_js_1 = get_block(r"(var supabaseUrl.*?</script>)", desktop)
desktop_js_2 = get_block(r"<script>\nvar \$=function(.*?)</script>", desktop)

mobile_js_2 = get_block(r"<script>\nconst supabaseUrl.*?</script>\n<script>\n(.*)</script>\n</body>", mobile)
if not mobile_js_2:
    mobile_js_2 = get_block(r"<script>\nconst supabaseUrl.*?</script>\n<script>\n(.*?)</script>", mobile)
if not mobile_js_2:
    # Just grab all the last scripts
    scripts = re.findall(r"<script>(.*?)</script>", mobile, re.DOTALL)
    mobile_js_2 = scripts[-1] if scripts else ""

desktop_js_all = re.findall(r"<script>(.*?)</script>", desktop, re.DOTALL)
desktop_js_core = desktop_js_all[-1] if desktop_js_all else ""

# Write out simple report
with open("/Users/jd/.gemini/antigravity/scratch/amai-exact/report.txt", "w") as f:
    f.write(f"Desktop scripts count: {len(desktop_js_all)}\n")
    f.write(f"Mobile JS length: {len(mobile_js_2)}\n")
    f.write(f"Desktop JS length: {len(desktop_js_core)}\n")

