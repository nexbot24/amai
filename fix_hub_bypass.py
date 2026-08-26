import re

with open("m-hub.html", "r") as f:
    content = f.read()

pattern = r'/\* Bypass auth for now \*/\s*S\.email = session\.user\.email;\s*let res = await sb\.from\(\'clients\'\)\.select\(\'name\'\)\.eq\(\'email\', S\.email\);\s*if \(res\.data && res\.data\.length > 0\) \{\s*S\.name = res\.data\[0\]\.name;\s*\}'

new_code = """if (!session) {
    S.email = "demo@example.com";
    S.name = "Demo";
  } else {
    S.email = session.user.email;
    let res = await sb.from('clients').select('name').eq('email', S.email);
    if (res.data && res.data.length > 0) {
      S.name = res.data[0].name;
    }
  }"""

content = re.sub(pattern, new_code, content)

with open("m-hub.html", "w") as f:
    f.write(content)


with open("hub.html", "r") as f:
    hub = f.read()

# For hub.html, it uses st object and local storage.
# It might crash if it expects localStorage "amai_hub_v2" to be fully populated.
hub = hub.replace('var h=JSON.parse(localStorage.getItem(HUB_KEY));', 'var h=JSON.parse(localStorage.getItem(HUB_KEY)) || {name:"Demo", email:"demo@example.com"};')
hub = hub.replace('$("g-name").textContent=h.name;', '$("g-name").textContent=h ? h.name : "Demo";')
hub = hub.replace('var name = h.name;', 'var name = h ? h.name : "Demo";')

with open("hub.html", "w") as f:
    f.write(hub)

