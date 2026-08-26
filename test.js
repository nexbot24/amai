var st={email:"",name:"",account:null,isNew:false,step:1,timer:0};
var digits=function(v){ return String(v).replace(/\D/g,""); };

/* progress — two steps for a returning client, three for a new one */
function total(){ return st.isNew?3:2; }
function progress(){
  var bars=$("bars"); bars.innerHTML="";
  for(var n=1;n<=total();n++){
    var d=document.createElement("div");
    d.setAttribute("style","height:3px;flex:1;max-width:"+(n===st.step?"46px":"26px")+";background:"+(n<=st.step?"#E8D5C4":"rgba(232,213,196,.25)"));
    bars.appendChild(d);
  }
  $("steplbl").textContent = st.step>total()? "Signed in" : "Step "+st.step+" of "+total();
}
function panel(id){
  ["p-email","p-name","p-code","p-done"].forEach(function(p){ $(p).className = p===id? "" : "hide"; });
  progress();
}

/* ---- step 1: number, then branch ---- */
function emailOk(){ var e=$("email").value; return e.includes("@") && e.includes("."); }
$("email").oninput=function(){
  $("look").disabled=!emailOk();
};
$("email").onkeydown=function(e){ if(e.key==="Enter"&&emailOk()) lookup(); };
$("look").onclick=lookup;


async function lookup(){
  st.email=$("email").value.trim().toLowerCase();
  var btn = $("look");
  var oldText = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Checking...";
  
  let clients = [];
  try {
    let res = await sb.from('clients').select('id, name').eq('email', st.email);
    clients = res.data || [];
  } catch(e) {}
  
  btn.textContent = oldText;
  btn.disabled = false;
  
  st.account = (clients && clients.length > 0) ? clients[0] : null;
  if (!st.account && KNOWN[st.email]) {
      st.account = KNOWN[st.email];
  }

  st.isNew=!st.account;
  if(st.isNew){
    st.step=2; st.name="";
    $("new-email").textContent=st.email;
    panel("p-name");
    setTimeout(function(){ $("new-name").focus(); },60);
  } else {
    st.name=st.account.name;
    st.step=2;
    sendCode();
  }
}

/* ---- step 2 (new): name ---- */
$("new-name").oninput=function(){ $("tocode").disabled=!this.value.trim(); };
$("new-name").onkeydown=function(e){ if(e.key==="Enter"&&this.value.trim()) toCode(); };
$("tocode").onclick=toCode;
function toCode(){ st.name=$("new-name").value.trim(); st.step=3; sendCode(); }
$("back-1").onclick=function(){ st.step=1; st.isNew=false; panel("p-email"); $("email").focus(); };

/* ---- code ---- */

async function sendCode(){
  $("shown-email").textContent=st.email;
  $("code-head").textContent = st.isNew? "Confirm it's you, "+st.name+"." : "Welcome back, "+st.name+".";
  $("verify").textContent = st.isNew? "Open my account" : "Take me to my dashboard";
  otpReset();
  panel("p-code");
  setTimeout(function(){ $("otp").firstChild.focus(); },60);
  
  var cleanEmail = st.email;
  
  try {
      const { data, error } = await sb.auth.signInWithOtp({ email: cleanEmail });
      if (error) alert("Error: " + error.message);
  } catch(e) {
      alert("Error: " + e);
  }

  var s=59; $("timer").textContent="0:59";
  clearInterval(st.timer);
  st.timer=setInterval(function(){
    s--; $("timer").textContent="0:"+(s<10?"0":"")+s;
    if(s<=0){ clearInterval(st.timer); $("timer").textContent="Resend code"; }
  },1000);
}
function code(){ return [].map.call($("otp").children,function(c){ return c.value; }).join(""); }
function otpReset(){
  var box=$("otp"); box.innerHTML="";
  for(var i=0;i<6;i++){
    var inp=document.createElement("input");
    inp.className="otp"; inp.inputMode="numeric"; inp.maxLength=1;
    inp.setAttribute("aria-label","Digit "+(i+1));
    box.appendChild(inp);
  }
  [].forEach.call(box.children,function(inp,i){
    inp.oninput=function(){
      this.value=digits(this.value).slice(0,1);
      this.className="otp"+(this.value?" filled":"");
      if(this.value&&i<5) box.children[i+1].focus();
      $("code-err").textContent="";
      $("verify").disabled=code().length!==6;
      if(code().length===6) $("verify").focus();
    };
    inp.onkeydown=function(e){
      if(e.key==="Backspace"&&!this.value&&i>0){ var p=box.children[i-1]; p.focus(); p.value=""; p.className="otp"; $("verify").disabled=true; }
      if(e.key==="ArrowLeft"&&i>0) box.children[i-1].focus();
      if(e.key==="ArrowRight"&&i<5) box.children[i+1].focus();
      if(e.key==="Enter"&&code().length===6) doVerify();
    };
    inp.onpaste=function(e){
      e.preventDefault();
      var d=digits((e.clipboardData||window.clipboardData).getData("text")).slice(0,6);
      [].forEach.call(box.children,function(c,j){ c.value=d[j]||""; c.className="otp"+(d[j]?" filled":""); });
      $("verify").disabled=d.length!==6;
      if(d.length===6) $("verify").focus();
    };
  });
  $("verify").disabled=true;
}
function countdown(s){
  clearInterval(st.timer);
  var left=s, r=$("resend");
  r.disabled=true; r.textContent="Send it again in "+left+"s";
  st.timer=setInterval(function(){
    left--;
    if(left<=0){ clearInterval(st.timer); r.disabled=false; r.textContent="Send it again"; }
    else r.textContent="Send it again in "+left+"s";
  },1000);
}
$("resend").onclick=function(){ if(!this.disabled){ otpReset(); $("otp").firstChild.focus(); countdown(30); } };
$("back-2").onclick=function(){ clearInterval(st.timer); st.step=1; st.isNew=false; panel("p-email"); $("email").focus(); };
$("verify").onclick=function(){ doVerify(); };



async function doVerify(){
  if(code().length!==6){ $("code-err").textContent="Enter all six digits."; return; }
  clearInterval(st.timer);
  
  var btn = $("verify");
  var oldText = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Verifying...";
  $("code-err").textContent = "";
  
  var cleanEmail = st.email;
  
  try {
      const { data, error } = await sb.auth.verifyOtp({ email: cleanEmail, token: code(), type: 'email' });
      if (error) {
          $("code-err").textContent = "Incorrect code. Try again.";
          btn.textContent = oldText;
          btn.disabled = false;
          return;
      }
  } catch (e) {
      $("code-err").textContent = "Something went wrong.";
      btn.textContent = oldText;
      btn.disabled = false;
      return;
  }
  
  if (st.isNew) {
    try {
      
      await sb.from('clients').insert([{ name: st.name, email: st.email }]);
    } catch(e) {}
  }
  
  signIn();
}

/* ---- sign in: write to the dashboard's own store ---- */
function signIn(){
  try{
    var raw=localStorage.getItem(HUB_KEY), h=raw?JSON.parse(raw):null;
    var samePerson = h && (h.email||"").toLowerCase()===st.email;
    if(samePerson){ h.signedIn=true; h.name=st.name||h.name; }
    else {
      var now=new Date();
      h={signedIn:true,name:st.name,email:st.email,
         since:now.toLocaleDateString("en-GB",{month:"long",year:"numeric"}),
         view:"home",stamps:st.account?st.account.stamps:0,plan:null,notes:"",card:null,
         upcoming:[],past:[]};
    }
    localStorage.setItem(HUB_KEY,JSON.stringify(h));
  }catch(e){}

  st.step=total()+1;
  $("done-title").textContent = st.isNew? st.name+", your account is open." : "You're in, "+st.name+".";
  $("done-copy").textContent = st.isNew
    ? "Book your first visit whenever suits — everything after that keeps itself up to date."
    : "Your bookings, stamps and aftercare are where you left them.";
  var facts = st.isNew
    ? [["Waiting for you","Book a visit and your loyalty card starts"],["Stamps","0 of 10"]]
    : [[st.account.next?"Next visit":"Bookings", st.account.next||"Nothing booked yet"],["Stamps",st.account.stamps+" of 10"],["Visits with us",String(st.account.visits)]];
  $("done-facts").innerHTML=facts.map(function(f){
    return '<div style="display:flex;justify-content:space-between;gap:18px;font-size:14px"><span style="color:#B39C88">'+f[0]+'</span><span>'+f[1]+'</span></div>';
  }).join("");
  panel("p-done");
}
