import re

with open("m-login.html", "r") as f:
    content = f.read()

# 1. Replace p1 and remove p1b
old_p1_p1b = re.search(r'      <div id="p1">.*?</div>\s+<div id="p1b" class="hide">.*?</div>', content, re.DOTALL)
if old_p1_p1b:
    new_p1 = """      <div id="p1">
        <div class="lbl" style="color:#B39C88;margin-bottom:16px">Step 1 of 2</div>
        <h1 class="serif" style="font-size:34px;line-height:1.14;margin:0 0 12px">Sign in.</h1>
        <p style="font-size:15px;line-height:1.75;color:#CBB49E;margin:0 0 24px">Your account is created when you book.</p>
        
        <label class="flab" style="margin-bottom:16px">Your first name
          <input id="fname" class="field" placeholder="So we know what to call you">
        </label>

        <label class="flab" style="margin-bottom:16px">Email address
          <input id="email" class="field" type="email" autocomplete="email" placeholder="hello@example.com">
        </label>
        
        <button id="send" class="btn" style="background:rgba(232,213,196,.28)" disabled>Continue</button>
      </div>"""
    content = content.replace(old_p1_p1b.group(0), new_p1)

# 2. Replace syncSend to include nameOk
old_syncSend = """function emailOk(){ var e=$("email").value; return e.includes("@") && e.includes("."); }
function syncSend(){ $("send").style.background=emailOk()?"#E8D5C4":"rgba(232,213,196,.28)"; }"""
new_syncSend = """function emailOk(){ var e=$("email").value; return e.includes("@") && e.includes("."); }
function nameOk(){ return $("fname") && $("fname").value.trim().length > 0; }
function syncSend(){ 
  var ok = emailOk() && nameOk();
  $("send").style.background = ok ? "#E8D5C4" : "rgba(232,213,196,.28)"; 
  $("send").disabled = !ok;
}"""
content = content.replace(old_syncSend, new_syncSend)

# 3. Replace toStep2 and sendCode logic
old_toStep2 = re.search(r'async function toStep2\(\)\{.*?} // End of toStep2', content, re.DOTALL)
# It's easier to just match from `async function toStep2(){` down to `await sb.auth.signInWithOtp({ email: st.email });\n}`
old_functions = re.search(r'async function toStep2\(\)\{.*?\n\}\n\nasync function sendCode\(\) \{.*?\n\}', content, re.DOTALL)

new_functions = """async function toStep2(){
  st.email = $("email").value.trim().toLowerCase();
  st.name = $("fname").value.trim();
  
  var btn = $("send");
  var oldText = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Sending...";
  
  // Lookup client in supabase
  try {
    let res = await sb.from('clients').select('id, name').eq('email', st.email);
    if (res.data && res.data.length > 0) {
      st.acct = res.data[0];
    } else {
      st.acct = null;
    }
  } catch(e) {}
  
  st.isNew = !st.acct;
  
  try {
      const { data, error } = await sb.auth.signInWithOtp({ email: st.email });
      if (error) {
        alert("Error sending code: " + error.message);
        btn.disabled = false;
        btn.textContent = oldText;
        return;
      }
  } catch(e) {
      alert("Error: " + e);
      btn.disabled = false;
      btn.textContent = oldText;
      return;
  }
  
  btn.disabled = false;
  btn.textContent = oldText;
  
  $("p2title").textContent = st.isNew? "Enter your code." : "Welcome back, "+st.name+".";
  $("p2step").textContent = "Step 2 of 2";
  $("p2sub").innerHTML = 'Emailed to <strong style="font-weight:600;color:#E8D5C4">'+st.email+'</strong>.';
  
  $("p1").className="hide"; $("p2").className="";
  $("code").focus(); countdown();
}"""

if old_functions:
    content = content.replace(old_functions.group(0), new_functions)


# 4. Update event listeners
old_events = """$("email").oninput=syncSend;
$("email").onkeydown=function(e){ if(e.key==="Enter"&&emailOk()) toStep2(); };
$("send").onclick=function(){ if(emailOk()) toStep2(); };
$("edit").onclick=function(){ clearInterval(st.tick); $("p2").className="hide"; $("p1").className=""; };
$("edit1b").onclick=function(){ $("p1b").className="hide"; $("p1").className=""; };
$("fname").oninput=function(){ $("sendname").style.background = this.value.trim() ? "#E8D5C4" : "rgba(232,213,196,.28)"; };
$("fname").onkeydown=function(e){ if(e.key==="Enter"&&this.value.trim()){ st.name=this.value.trim(); sendCode(); } };
$("sendname").onclick=function(){ if($("fname").value.trim()){ st.name=$("fname").value.trim(); sendCode(); } };"""

new_events = """$("email").oninput=syncSend;
$("fname").oninput=syncSend;
$("email").onkeydown=function(e){ if(e.key==="Enter"&&emailOk()&&nameOk()) toStep2(); };
$("fname").onkeydown=function(e){ if(e.key==="Enter"&&emailOk()&&nameOk()) toStep2(); };
$("send").onclick=function(){ if(emailOk()&&nameOk()) toStep2(); };
$("edit").onclick=function(){ clearInterval(st.tick); $("p2").className="hide"; $("p1").className=""; };"""

content = content.replace(old_events, new_events)

with open("m-login.html", "w") as f:
    f.write(content)

