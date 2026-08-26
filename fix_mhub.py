import re
with open("m-hub.html", "r") as f:
    content = f.read()

new_content = content.replace('if (!session) {', 'const { data: { session } } = await sb.auth.getSession();\n  if (!session) {')

with open("m-hub.html", "w") as f:
    f.write(new_content)
