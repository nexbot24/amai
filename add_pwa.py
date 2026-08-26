import re

with open("m-hub.html", "r") as f:
    content = f.read()

# 1. Add manifest
content = content.replace('<link rel="icon" href="favicon/amai-favicon.svg" type="image/svg+xml">',
                          '<link rel="manifest" href="manifest.json">\n<link rel="icon" href="favicon/amai-favicon.svg" type="image/svg+xml">')

# 2. Update V.account
old_account = """    '<div class="sec last" style="display:flex;flex-direction:column;gap:8px">'+
      '<a class="btn btn-o" href="m-home.html">Back to the site</a>'+
      '<button class="btn btn-o" id="signout">Sign out</button></div>';"""
      
new_account = """    '<div class="sec" id="pwa-card" style="display:none"><div class="lbl" style="margin-bottom:12px">Amai on your phone</div>'+
      '<div class="card">'+
        '<div class="serif" style="font-size:21px;line-height:1.3;margin-bottom:8px">Add Amai to your home screen.</div>'+
        '<p style="font-size:14px;line-height:1.7;color:#CBB49E;margin:0 0 16px">Opens full screen like an app, straight into your bookings. Nothing to download.</p>'+
        '<button class="btn" style="background:#E8D5C4" id="a-pwa">Add to home screen</button></div></div>'+
    '<div class="sec last" style="display:flex;flex-direction:column;gap:8px">'+
      '<a class="btn btn-o" href="m-home.html">Back to the site</a>'+
      '<button class="btn btn-o" id="signout">Sign out</button></div>';"""
content = content.replace(old_account, new_account)

# 3. Add JS logic
js_add = """
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  checkPWA();
});

function isIos() { return /iphone|ipad|ipod/.test(window.navigator.userAgent.toLowerCase()); }
function checkPWA() {
  var pwa = $("pwa-card"); if(!pwa) return;
  var isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;
  if(isStandalone) { pwa.style.display = "none"; }
  else if (isIos() || deferredPrompt) { pwa.style.display = "block"; }
  else { pwa.style.display = "none"; }
}

if ('serviceWorker' in navigator) { navigator.serviceWorker.register('sw.js'); }
"""

# Append just before initSupabase
content = content.replace("async function initSupabase() {", js_add + "\nasync function initSupabase() {")

# Add the wire logic for a-pwa and checkPWA to render()
wire_add = """
  var apwa = one("a-pwa"); if(apwa) apwa.onclick = async function() {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      var choice = await deferredPrompt.userChoice;
      if (choice.outcome === 'accepted') { deferredPrompt = null; checkPWA(); }
    } else if (isIos()) {
      sheet('<div class="lbl" style="margin-bottom:12px">Install Amai</div>'+
        '<h2 class="serif" style="font-size:25px;line-height:1.2;margin:0 0 18px">Add to Home Screen</h2>'+
        '<ol style="font-size:15px;line-height:1.75;color:#CBB49E;padding-left:18px;margin:0 0 24px">'+
          '<li style="margin-bottom:12px">Tap the <strong>Share</strong> icon (square with an up arrow) at the bottom of Safari.</li>'+
          '<li style="margin-bottom:12px">Scroll down and tap <strong>Add to Home Screen</strong>.</li>'+
        '</ol>'+
        '<button class="btn btn-o" data-close="1">Close</button>');
    }
  };
"""

content = content.replace('  var so=one("signout"); if(so) so.onclick=async function(){ await sb.auth.signOut(); S.signedIn=false; save(); location.href="m-home.html"; };',
                          '  var so=one("signout"); if(so) so.onclick=async function(){ await sb.auth.signOut(); S.signedIn=false; save(); location.href="m-home.html"; };\n' + wire_add)


content = content.replace("badge(); wire(document);\n}", "badge(); wire(document);\n  checkPWA();\n}")


with open("m-hub.html", "w") as f:
    f.write(content)

