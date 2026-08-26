import re
with open('/Users/jd/.gemini/antigravity/scratch/amai-exact/m-hub.html', 'r') as f:
    m = f.read()

m = m.replace('q("[data-close]").forEach(function(b){ b.onclick=closeSheet; });',
              'q("[data-close]").forEach(function(b){ b.onclick=closeSheet; });\n  q("[data-quick]").forEach(function(b){ b.onclick=function(){ sendMsg(b.dataset.quick); }; });')

with open('/Users/jd/.gemini/antigravity/scratch/amai-exact/m-hub.html', 'w') as f:
    f.write(m)
