import re
with open('index.html', 'r') as f:
    content = f.read()

# I want to add a script logic in index.html to read the session and pre-fill step 3, or replace the UI entirely.
# Let's just modify checkKnown() or the step rendering logic.
# Wait, let's insert a script near the bottom of index.html that does this dynamically.

script = """
<script>
(function(){
  try {
    var raw = localStorage.getItem("amai_hub_v2"), h = raw ? JSON.parse(raw) : null;
    if (h && h.signedIn) {
      document.querySelectorAll("a[href='login.html']").forEach(function(el) {
        el.href = "hub.html";
      });
      
      // Auto-fill booking form if we are on the homepage
      var phoneInput = document.getElementById("f-contact");
      var nameInput = document.getElementById("f-name");
      if (phoneInput && nameInput) {
        phoneInput.value = h.phone;
        nameInput.value = h.name;
        
        // Hide the inputs and show a "Signed in as" message
        var container = phoneInput.closest("div.card"); // Or wherever they are
        if (container) {
          var signedInDiv = document.createElement("div");
          signedInDiv.innerHTML = '<div style="margin-bottom:16px"><span style="font-size:15px;color:#CBB49E">Signed in as </span><strong style="color:#E8D5C4">' + h.name + '</strong> <span style="color:#8A7361">(' + h.phone + ')</span></div>' +
                                  '<a href="#" id="sign-out-link" style="font-size:13px;color:#8A7361;text-decoration:underline">Not you? Sign out</a>';
          container.insertBefore(signedInDiv, container.firstChild);
          
          phoneInput.parentElement.style.display = "none";
          nameInput.parentElement.style.display = "none";
          var acctCheckbox = document.getElementById("f-acct");
          if(acctCheckbox) acctCheckbox.closest("label").style.display = "none";
          var knownDiv = document.getElementById("known");
          if(knownDiv) knownDiv.style.display = "none";
          
          document.getElementById("sign-out-link").onclick = function(e) {
            e.preventDefault();
            localStorage.removeItem("amai_hub_v2");
            window.location.reload();
          };
          
          // Trigger the input events so the form knows it's ready
          if (typeof syncNext === 'function') setTimeout(syncNext, 100);
        }
      }
    }
  } catch(e) {}
})();
</script>
"""

# Replace the previous script injected by fix.py
content = re.sub(r'<script>\s*\(function\(\)\{\s*try \{.*?\(\)\);\s*</script>', '', content, flags=re.DOTALL)

if "var raw = localStorage.getItem(\"amai_hub_v2\"" not in content:
    content = content.replace("</body>", script + "</body>")

with open('index.html', 'w') as f:
    f.write(content)
