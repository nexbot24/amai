import re
import os

files = ['index.html', 'about.html', 'contact.html', 'services.html', 'login.html']
for f in files:
    if os.path.exists(f):
        with open(f, 'r') as file:
            content = file.read()
        
        # 1. Remove "How it works"
        content = re.sub(r'<a href="index.html#studio"[^>]*>How it works</a>\s*', '', content)
        
        # 2. Add inline session script right before </body>
        session_script = """
<script>
(function(){
  try {
    var raw = localStorage.getItem("amai_hub_v2"), h = raw ? JSON.parse(raw) : null;
    if (h && h.signedIn) {
      document.querySelectorAll("a[href='login.html']").forEach(function(el) {
        el.href = "hub.html";
      });
    }
  } catch(e) {}
})();
</script>
"""
        if "var raw = localStorage.getItem(\"amai_hub_v2\"" not in content:
            content = content.replace("</body>", session_script + "</body>")

        with open(f, 'w') as file:
            file.write(content)
print("done")
