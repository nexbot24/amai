import re

with open('/Users/jd/.gemini/antigravity/scratch/amai-exact/m-hub.html', 'r') as f:
    m = f.read()

funcs_str = """
var chatBuilt=false, typing=false, convId=null, chatUnreadCount=0, chatSub=null;
function clock(ts){ return new Date(ts).toLocaleTimeString("en-GB",{hour:"2-digit",minute:"2-digit"}); }
function dayStamp(ts){
  var d=new Date(ts); d.setHours(0,0,0,0);
  var diff=Math.round((d0()-d)/86400000);
  if(diff===0) return "Today";
  if(diff===1) return "Yesterday";
  if(diff<7) return new Date(ts).toLocaleDateString("en-GB",{weekday:"long"});
  return new Date(ts).toLocaleDateString("en-GB",{day:"numeric",month:"long"});
}
function fitChat(){
  var w=document.querySelector(".chatwrap"); if(!w) return;
  var tabs=document.querySelector(".tabs");
  var top=w.getBoundingClientRect().top+ (document.documentElement.scrollTop||0) - (document.documentElement.scrollTop||0);
  var h=innerHeight - top - (tabs?tabs.getBoundingClientRect().height:64);
  w.style.height=Math.max(320,Math.round(h))+"px";
}
function renderSugg(){
  var box=$("sugg"); if(!box) return;
  var lastMine=S.chat&&S.chat.length&&S.chat[S.chat.length-1].who==="me";
  var v=nextVisit();
  var opts=[];
  if(!lastMine){
    if(v) opts.push("Could I move my appointment?");
    opts.push("What should I do beforehand?");
    if(!v) opts.push("Do you have anything this week?");
    opts.push("Thank you!");
  }
  box.style.display=opts.length?"flex":"none";
  box.innerHTML=opts.map(function(o){ return '<button data-quick="'+o.replace(/"/g,"&quot;")+'">'+o+'</button>'; }).join("");
  wire(box);
}
function buildChat(){
  var box = $("v-inbox");
  if(!box) return;
  box.innerHTML=
    '<div class="chatwrap">'+
      '<div class="chathead">'+
        '<span class="ring"><i></i></span>'+
        '<span style="flex:1;min-width:0">'+
          '<span class="serif" style="display:block;font-size:18px;line-height:1.25">Amai Studio</span>'+
          '<span id="c-status" style="font-size:12.5px;color:#B39C88"></span></span>'+
        '<a href="tel:+442000000000" style="width:40px;height:40px;border-radius:50%;border:1px solid rgba(232,213,196,.24);display:flex;align-items:center;justify-content:center;flex:none" aria-label="Call the studio">'+
          '<span style="display:block;width:13px;height:18px;border:1.3px solid #CBB49E;border-bottom:none;border-radius:999px 999px 0 0"></span></a>'+
      '</div>'+
      '<div class="thread" id="thread"></div>'+
      '<div class="sugg" id="sugg"></div>'+
      '<div class="composer">'+
        '<textarea id="c-in" rows="1" placeholder="Message the studio"></textarea>'+
        '<button class="send" id="c-send" disabled aria-label="Send">→</button>'+
      '</div>'+
    '</div>';
  var ta=$("c-in");
  ta.oninput=function(){
    this.style.height="auto";
    this.style.height=Math.min(112,this.scrollHeight)+"px";
    $("c-send").disabled=!this.value.trim();
  };
  ta.onkeydown=function(e){
    if(e.key==="Enter"&&!e.shiftKey&&this.value.trim()){ e.preventDefault(); sendMsg(this.value); }
  };
  $("c-send").onclick=function(){ sendMsg(ta.value); };
  chatBuilt=true;
  fitChat();
  addEventListener("resize",fitChat);
  if(window.visualViewport) visualViewport.addEventListener("resize",fitChat);
  loadConversation();
}
async function loadConversation() {
  if (!S.phone) return;
  var {data} = await sb.from('conversations').select('id, client_unread').eq('client_phone', S.phone).maybeSingle();
  if (data) {
    convId = data.id;
    chatUnreadCount = data.client_unread || 0;
    
    var {data: msgs} = await sb.from('chat_messages').select('*').eq('conversation_id', convId).order('created_at', {ascending: true});
    if (msgs) {
      S.chat = msgs.map(m => ({
        id: m.id,
        who: m.sender === 'client' ? 'me' : 'them',
        at: new Date(m.created_at).getTime(),
        body: m.body,
        seen: m.seen
      }));
    } else {
      S.chat = [];
    }
    
    if (!chatSub) {
      chatSub = sb.channel('client-inbox').on('postgres_changes',{event:'INSERT',schema:'public',table:'chat_messages',filter:'conversation_id=eq.'+convId},function(payload){
        if(payload.new.sender==='studio'){
          if (!S.chat) S.chat = [];
          S.chat.push({
            id: payload.new.id,
            who: 'them',
            at: new Date(payload.new.created_at).getTime(),
            body: payload.new.body,
            seen: payload.new.seen
          });
          chatUnreadCount++;
          if (view === 'inbox') {
            chatUnreadCount = 0;
            sb.from('conversations').update({client_unread: 0}).eq('id', convId).then(function(){});
          }
          renderThread(true);
          badge();
        }
      }).subscribe();
    }
    
    renderThread(true);
    badge();
  } else {
    S.chat = [];
    renderThread(true);
  }
}
function renderThread(stick){
  var t=$("thread"); if(!t) return;
  if (!S.chat) S.chat = [];
  var atBottom = stick || (t.scrollHeight-t.scrollTop-t.clientHeight)<80;
  var last="", out="";
  S.chat.forEach(function(m,i){
    var day=dayStamp(m.at);
    if(day!==last){ out+='<div class="dayline"><b></b><span>'+day+'</span><b></b></div>'; last=day; }
    var prev=S.chat[i-1], next=S.chat[i+1];
    var run = prev && prev.who===m.who && dayStamp(prev.at)===day && (m.at-prev.at)<600000;
    var lastOfRun = !(next && next.who===m.who && dayStamp(next.at)===day && (next.at-m.at)<600000);
    out+='<div class="bub '+(m.who==="me"?"mine":"them")+(run?" run":"")+'">'+m.body+'</div>';
    if(lastOfRun) out+='<div class="stamp2 '+(m.who==="me"?"mine":"them")+'">'+clock(m.at)+
      (m.who==="me"?' · '+(m.seen?"Read":"Sent"):'')+'</div>';
  });
  if(typing) out+='<div class="typing"><i></i><i></i><i></i></div>';
  t.innerHTML=out;
  if($("c-status")) $("c-status").textContent = typing? "Typing…" : "Replies within the hour";
  if(atBottom) t.scrollTop=t.scrollHeight;
  renderSugg();
}
async function sendMsg(text){
  var body=(text||"").trim(); if(!body) return;
  if (!S.chat) S.chat = [];
  var tempId = Date.now();
  S.chat.push({id:tempId,who:"me",at:Date.now(),body:body});
  var ta=$("c-in"); if(ta) { ta.value=""; ta.style.height="auto"; }
  var btn=$("c-send"); if(btn) btn.disabled=true;
  renderThread(true);
  
  if (!convId) {
    var {data, error} = await sb.from('conversations').insert({
      client_phone: S.phone,
      client_name: S.name || '',
      client_id: null,
      last_message_at: new Date().toISOString(),
      last_message_preview: body,
      last_sender: 'client',
      admin_unread: 1,
      client_unread: 0
    }).select().single();
    if (data) convId = data.id;
  } else {
    await sb.from('conversations').update({
      last_message_at: new Date().toISOString(),
      last_message_preview: body,
      last_sender: 'client',
      admin_unread: 1
    }).eq('id', convId);
  }
  
  if (convId) {
    await sb.from('chat_messages').insert({
      conversation_id: convId,
      sender: 'client',
      body: body,
      seen: false
    });
  }
}
async function markRead() {
  chatUnreadCount = 0;
  badge();
  if (convId) {
    await sb.from('conversations').update({client_unread: 0}).eq('id', convId);
  }
}
function badge(){
  var t=document.querySelector('.tab[data-go="rewards"]');
  if(t){
    var old=t.querySelector(".dot"); if(old) old.remove();
    if(S.stamps>=5){ var d=document.createElement("span"); d.className="dot"; t.appendChild(d); }
  }
  var i=document.querySelector('.tab[data-go="inbox"]');
  if(i){
    var oc=i.querySelector(".count"); if(oc) oc.remove();
    if(chatUnreadCount){ var c=document.createElement("span"); c.className="count"; c.textContent=chatUnreadCount; i.appendChild(c); }
  }
}
function go(name){
  view=name;
  if(name==="inbox"){
    markRead();
  }
  ["home","visits","inbox","rewards","account"].forEach(function(v){ var el=$("v-"+v); if(el) el.className = v===name?"view on":"view"; });
  [].forEach.call(document.querySelectorAll(".tab"),function(t){ t.className = t.dataset.go===name?"tab on":"tab"; });
  window.scrollTo(0,0);
  render();
  if(name==="inbox"){ fitChat(); renderThread(true); var ta=$("c-in"); if(ta) ta.blur(); }
}
function render(){
  ["home","visits","rewards","account"].forEach(function(v){ var el=$("v-"+v); if(el) el.innerHTML=V[v](); });
  var justBuilt=!chatBuilt;
  if(justBuilt) buildChat();
  renderThread(justBuilt);
  $("me").textContent=(first()[0]||"A").toUpperCase();
  badge(); wire(document);
  checkPWA();
}
"""

# Replace badge, go, render completely
m = re.sub(r'function badge\(\).*?^}', '', m, flags=re.MULTILINE | re.DOTALL)
m = re.sub(r'function go\(\w+\).*?^}', '', m, flags=re.MULTILINE | re.DOTALL)
m = re.sub(r'function render\(\).*?^}', '', m, flags=re.MULTILINE | re.DOTALL)

# Insert the functions before checkPWA() which is after these
m = m.replace('let deferredPrompt;', funcs_str + '\nlet deferredPrompt;')

# In V.home we need to include inbox in quick buttons if it's missing, let's see.
# Original quick in m-hub.html:
#       '<button class="btn btn-q" data-tab="visits"><i></i>My visits</button>'+
#       '<button class="btn btn-q" data-tab="rewards"><i></i>Rewards</button>'+
#       '<a class="btn btn-q" href="tel:+442000000000"><i></i>Call studio</a>'+

new_quick = """'<button class="btn btn-q" data-tab="visits"><i></i>My visits</button>'+
      '<button class="btn btn-q" data-tab="inbox"><i></i>Message'+
        (chatUnreadCount?'<span style="position:absolute;top:11px;right:11px;width:8px;height:8px;border-radius:50%;background:#E8D5C4"></span>':'')+'</button>'+
      '<a class="btn btn-q" href="tel:+442000000000"><i></i>Call studio</a>'+"""
      
m = m.replace("""'<button class="btn btn-q" data-tab="visits"><i></i>My visits</button>'+
      '<button class="btn btn-q" data-tab="rewards"><i></i>Rewards</button>'+
      '<a class="btn btn-q" href="tel:+442000000000"><i></i>Call studio</a>'+""", new_quick)

with open('/Users/jd/.gemini/antigravity/scratch/amai-exact/m-hub.html', 'w') as f:
    f.write(m)
print("Applied JS functions.")
