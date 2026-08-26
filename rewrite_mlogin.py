import re

with open("m-login.html", "r") as f:
    content = f.read()

# 1. Insert p1b
p1b_html = """      <div id="p1b" class="hide">
        <button id="edit1b" style="background:none;border:none;color:#B39C88;font-size:13.5px;padding:0 0 20px">← Change email</button>
        <div class="lbl" style="color:#B39C88;margin-bottom:16px">Step 2 of 3</div>
        <h1 class="serif" style="font-size:34px;line-height:1.14;margin:0 0 12px">Welcome.</h1>
        <p style="font-size:15px;line-height:1.75;color:#CBB49E;margin:0 0 24px">Your account is created when you book.</p>
        <label class="flab" style="margin-bottom:14px">Your first name<input id="fname" class="field" placeholder="So we know what to call you"></label>
        <button id="sendname" class="btn" style="background:rgba(232,213,196,.28)">Next</button>
      </div>

      <div id="p2" class="hide">"""
content = content.replace('      <div id="p2" class="hide">', p1b_html)

# 2. Modify p2 step text
content = content.replace('<div class="lbl" style="color:#B39C88;margin-bottom:16px">Step 2 of 2</div>', '<div id="p2step" class="lbl" style="color:#B39C88;margin-bottom:16px">Step 2 of 2</div>')

# 3. Remove newname div from p2
newname_div = """        <div id="newname" class="hide" style="margin-top:26px;padding-top:22px;border-top:1px solid rgba(232,213,196,.16)">
          <label class="flab">Your first name<input id="fname" class="field" placeholder="So we know what to call you"></label>
        </div>"""
content = content.replace(newname_div, "")

# 4. Rewrite toStep2 and add sendCode
old_tostep2 = """async function toStep2(){
  st.email=$("email").value.trim().toLowerCase();
  var h=stored();
  
  // Lookup client in supabase
  try {
    let res = await sb.from('clients').select('id, name').eq('email', st.email);
    if (res.data && res.data.length > 0) {
      st.acct = res.data[0];
      st.name = st.acct.name;
    } else {
      st.acct = null;
    }
  } catch(e) {}
  
  st.isNew = !st.acct;
  
  $("p2title").textContent = st.isNew? "Enter your code." : "Welcome back, "+st.name+".";
  $("p2sub").innerHTML = 'Emailed to <strong style="font-weight:600;color:#E8D5C4">'+st.email+'</strong>.';
  $("newname").className = st.isNew? "" : "hide";
  $("p1").className="hide"; $("p2").className="";
  $("code").focus(); countdown();
  
  await sb.auth.signInWithOtp({ email: st.email });
}"""

new_tostep2 = """async function toStep2(){
  st.email=$("email").value.trim().toLowerCase();
  var h=stored();
  
  // Lookup client in supabase
  try {
    let res = await sb.from('clients').select('id, name').eq('email', st.email);
    if (res.data && res.data.length > 0) {
      st.acct = res.data[0];
      st.name = st.acct.name;
    } else {
      st.acct = null;
    }
  } catch(e) {}
  
  st.isNew = !st.acct;
  
  if (st.isNew) {
    $("p1").className="hide"; $("p1b").className="";
    $("fname").focus();
  } else {
    sendCode();
  }
}

async function sendCode() {
  $("p2title").textContent = st.isNew? "Enter your code." : "Welcome back, "+st.name+".";
  $("p2step").textContent = st.isNew? "Step 3 of 3" : "Step 2 of 2";
  $("p2sub").innerHTML = 'Emailed to <strong style="font-weight:600;color:#E8D5C4">'+st.email+'</strong>.';
  
  $("p1").className="hide"; $("p1b").className="hide"; $("p2").className="";
  $("code").focus(); countdown();
  
  await sb.auth.signInWithOtp({ email: st.email });
}"""
content = content.replace(old_tostep2, new_tostep2)

# 5. Add event listeners for p1b
old_events = """$("email").oninput=syncSend;
$("email").onkeydown=function(e){ if(e.key==="Enter"&&emailOk()) toStep2(); };
$("send").onclick=function(){ if(emailOk()) toStep2(); };
$("edit").onclick=function(){ clearInterval(st.tick); $("p2").className="hide"; $("p1").className=""; };"""

new_events = """$("email").oninput=syncSend;
$("email").onkeydown=function(e){ if(e.key==="Enter"&&emailOk()) toStep2(); };
$("send").onclick=function(){ if(emailOk()) toStep2(); };
$("edit").onclick=function(){ clearInterval(st.tick); $("p2").className="hide"; $("p1").className=""; };
$("edit1b").onclick=function(){ $("p1b").className="hide"; $("p1").className=""; };
$("fname").oninput=function(){ $("sendname").style.background = this.value.trim() ? "#E8D5C4" : "rgba(232,213,196,.28)"; };
$("fname").onkeydown=function(e){ if(e.key==="Enter"&&this.value.trim()){ st.name=this.value.trim(); sendCode(); } };
$("sendname").onclick=function(){ if($("fname").value.trim()){ st.name=$("fname").value.trim(); sendCode(); } };"""
content = content.replace(old_events, new_events)


# 6. Change edit button back to step 1
content = content.replace('$("edit").onclick=function(){ clearInterval(st.tick); $("p2").className="hide"; $("p1").className=""; };', '$("edit").onclick=function(){ clearInterval(st.tick); $("p2").className="hide"; $("p1").className=""; };')


with open("m-login.html", "w") as f:
    f.write(content)

