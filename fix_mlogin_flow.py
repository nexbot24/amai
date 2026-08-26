with open("m-login.html", "r") as f:
    content = f.read()

import re

# 1. Replace the HTML for p1, p1b
new_html = """      <div id="p1">
        <div class="lbl" style="color:#B39C88;margin-bottom:16px" id="p1step">Step 1 of 2</div>
        <h1 class="serif" style="font-size:34px;line-height:1.14;margin:0 0 12px">Sign in.</h1>
        <p style="font-size:15px;line-height:1.75;color:#CBB49E;margin:0 0 24px">Your account is created when you book.</p>
        
        <label class="flab" style="margin-bottom:16px">Email address
          <input id="email" class="field" type="email" autocomplete="email" placeholder="hello@example.com">
        </label>
        
        <button id="send" class="btn" style="background:rgba(232,213,196,.28)" disabled>Continue</button>
      </div>

      <div id="p1b" class="hide">
        <button id="edit1b" style="background:none;border:none;color:#B39C88;font-size:13.5px;padding:0 0 20px">← Change number</button>
        <div class="lbl" style="color:#B39C88;margin-bottom:16px">Step 2 of 3</div>
        <h1 class="serif" style="font-size:34px;line-height:1.14;margin:0 0 12px">Welcome.</h1>
        <p style="font-size:15px;line-height:1.75;color:#CBB49E;margin:0 0 24px">Your account is created when you book.</p>
        <label class="flab" style="margin-bottom:14px">Your first name
          <input id="fname" class="field" placeholder="So we know what to call you">
        </label>
        <button id="sendname" class="btn" style="background:rgba(232,213,196,.28)">Next</button>
      </div>

      <div id="p2" class="hide">"""

# Replace anything from <div id="p1"> down to <div id="p2" class="hide">
content = re.sub(r'<div id="p1">.*?(<div id="p2" class="hide">)', new_html, content, flags=re.DOTALL)


# 2. Replace the JS
new_js = """function stored(){ try{ return JSON.parse(localStorage.getItem(HUB_KEY))||null; }catch(e){ return null; } }

function emailOk(){ var e=$("email").value; return e.includes("@") && e.includes("."); }
function syncSend(){ $("send").style.background=emailOk()?"#E8D5C4":"rgba(232,213,196,.28)"; $("send").disabled=!emailOk(); }

function countdown(){
  st.left=30; clearInterval(st.tick);
  $("resend").style.opacity=".45";
  $("timer").textContent="Code sent · resend in 30s";
  st.tick=setInterval(function(){
    st.left--;
    if(st.left<=0){ clearInterval(st.tick); $("timer").textContent="Didn't arrive?"; $("resend").style.opacity="1"; }
    else $("timer").textContent="Code sent · resend in "+st.left+"s";
  },1000);
}

async function toStep2(){
  st.email = $("email").value.trim().toLowerCase();
  
  var btn = $("send");
  var oldText = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Checking...";
  
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
  
  btn.disabled = false;
  btn.textContent = oldText;

  if (st.isNew) {
    $("p1step").textContent = "Step 1 of 3";
    $("p1").className="hide"; $("p1b").className="";
    $("fname").focus();
  } else {
    st.name = st.acct.name;
    sendCode();
  }
}

async function sendCode() {
  $("p2title").textContent = st.isNew? "Enter your code." : "Welcome back, "+st.name+".";
  $("p2step").textContent = st.isNew? "Step 3 of 3" : "Step 2 of 2";
  $("p2sub").innerHTML = 'Emailed to <strong style="font-weight:600;color:#E8D5C4">'+st.email+'</strong>.';
  
  $("p1").className="hide"; $("p1b").className="hide"; $("p2").className="";
  $("code").focus(); countdown();
  
  try {
      const { data, error } = await sb.auth.signInWithOtp({ email: st.email });
      if (error) {
        alert("Error sending code: " + error.message);
      }
  } catch(e) {
      alert("Error sending code: " + e);
  }
}

function stampRow(n){"""

content = re.sub(r'function stored\(\)\{.*?(?=function stampRow\(n\)\{)', new_js, content, flags=re.DOTALL)


# 3. Replace the Event Listeners
new_events = """$("email").oninput=syncSend;
$("email").onkeydown=function(e){ if(e.key==="Enter"&&emailOk()) toStep2(); };
$("send").onclick=function(){ if(emailOk()) toStep2(); };
$("edit").onclick=function(){ clearInterval(st.tick); $("p2").className="hide"; $("p1").className=""; };
$("edit1b").onclick=function(){ $("p1b").className="hide"; $("p1").className=""; };
$("fname").oninput=function(){ $("sendname").style.background = this.value.trim() ? "#E8D5C4" : "rgba(232,213,196,.28)"; };
$("fname").onkeydown=function(e){ if(e.key==="Enter"&&this.value.trim()){ st.name=this.value.trim(); sendCode(); } };
$("sendname").onclick=function(){ if($("fname").value.trim()){ st.name=$("fname").value.trim(); sendCode(); } };"""

content = re.sub(r'\$\("email"\)\.oninput=syncSend;.*?(?=\$\("code"\)\.oninput=async function\(\)\{)', new_events + "\n", content, flags=re.DOTALL)


with open("m-login.html", "w") as f:
    f.write(content)

