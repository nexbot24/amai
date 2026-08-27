/* booking.js — shared booking engine for AMAI (desktop + mobile) */

/* ─── Supabase ─── */
var SB_URL='https://tphyrmweauzfletdlqvi.supabase.co';
var SB_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwaHlybXdlYXV6ZmxldGRscXZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc0NTIxOTQsImV4cCI6MjEwMzAyODE5NH0.Z_utKsxYquCoL2LfTjjL8QFB1tnLJZW9j3El7Sykk8o';
var sb=null;
function loadSupabaseSDK(){
  return new Promise(function(resolve){
    if(window.supabase){sb=window.supabase.createClient(SB_URL,SB_KEY);window.sb=sb;resolve();return;}
    var s=document.createElement('script');
    s.src='https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2';
    s.onload=function(){sb=window.supabase.createClient(SB_URL,SB_KEY);window.sb=sb;resolve();};
    s.onerror=function(){resolve();};
    document.head.appendChild(s);
  });
}

/* ─── Data ─── */
var GROUPS=[
  {title:"Waxing",blurb:"Professional waxing delivered with care, precision and comfort.",
   heading:"Professional waxing, elevated.",
   copy:"Every appointment focuses on comfort, hygiene, detail and results — helping you leave feeling smooth, confident and cared for.",
   footnote:"First visits are booked with extra time, at no extra cost.",items:[]},
  {title:"Intimate Care",blurb:"Thoughtful intimate beauty support focused on confidence, sensitivity and aftercare.",
   heading:"Intimate care, without the awkwardness.",
   copy:"Booked with longer appointment times, talked through before anything begins, and always with one practitioner you\u2019ll see again.",
   footnote:"Every intimate booking includes aftercare in your hand.",items:[]},
  {title:"Skin, Body & Wellness",blurb:"Future skin, body and wellness treatments created to elevate your self-care.",
   heading:"Coming to the studio.",
   copy:"AMAI is built to grow beyond waxing. These are the treatments in preparation \u2014 ask to be told first when a date is set.",
   footnote:"Join the list when you book and we\u2019ll write to you once.",
   items:[{name:"Facials & skin consultation",time:"60 min",price:"Autumn 2026"},
          {name:"Body treatments",time:"60\u201390 min",price:"In preparation"},
          {name:"Aftercare products",time:"\u2014",price:"In preparation"}]}
];
var BOOKABLE=[];
var HUB_KEY="amai_hub_v2";
var S={group:0,step:1,treatment:"",monthOffset:0,dateKey:"",time:"",query:"",paid:"",how:"",sent:false,returning:false,promo:null};
var CAL_CACHE={};
var CLOSED_DAYS={};
var OPENING_HOURS={tue:{open:'9.00',close:'18.00'},wed:{open:'9.00',close:'18.00'},thu:{open:'9.00',close:'18.00'},fri:{open:'9.00',close:'18.00'},sat:{open:'9.00',close:'18.00'}};

/* ─── DOM helpers ─── */
var $=function(id){return document.getElementById(id);};
var el=function(tag,attrs,html){var n=document.createElement(tag);for(var k in attrs){if(k==="style")n.setAttribute("style",attrs[k]);else if(k.indexOf("on")===0)n[k]=attrs[k];else n.setAttribute(k,attrs[k]);}if(html!=null)n.innerHTML=html;return n;};

/* ─── Utilities ─── */
function dayKeyToDate(k){var p=k.split('-');var d=new Date(+p[0],+p[1],+p[2]);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
function priceOf(n){for(var i=0;i<BOOKABLE.length;i++)if(BOOKABLE[i].name===n)return BOOKABLE[i].price;return"";}
function balanceOf(n){var p=priceOf(n),v=parseFloat(String(p).replace(/[^0-9.]/g,""));if(!v)return"Balance";
  return(String(p).indexOf("from")===0||String(p).indexOf("\u2013")>-1?"from \u00a3":"\u00a3")+(v-10);}
function today(){var d=new Date();d.setHours(0,0,0,0);return d;}
function viewMonth(){var t=today();return new Date(t.getFullYear(),t.getMonth()+S.monthOffset,1);}
function timeToMins(t){if(!t)return 0;var p=String(t).split(/[:.]/) ;return parseInt(p[0],10)*60+parseInt(p[1]||0,10);}
function minsToTime(m){var h=Math.floor(m/60),mm=m%60;return h+"."+(mm<10?"0"+mm:mm);}
function getDuration(name){var t=BOOKABLE.find(function(i){return i.name===name;});if(!t)return 60;var match=String(t.time).match(/(\d+)/);return match?parseInt(match[1],10):60;}
function dotTimeToMins(t){var p=t.split('.');return parseInt(p[0])*60+parseInt(p[1]||0);}
function chosenDate(){if(!S.dateKey)return null;var p=S.dateKey.split("-");return new Date(+p[0],+p[1],+p[2]);}
function longDate(d){return d.toLocaleDateString("en-GB",{weekday:"long",day:"numeric",month:"long"});}
function whenLabel(){var d=chosenDate();if(!d)return"Not chosen yet";return S.time?longDate(d)+", "+S.time:longDate(d);}
function digits(v){return String(v).replace(/\D/g,"");}
function priceNum(n){return parseFloat(String(priceOf(n)).replace(/[^0-9.]/g,""))||0;}
function wantsAccount(){return $("f-acct")&&$("f-acct").checked;}

/* ─── Data loading ─── */
async function loadServicesIntoGroups(){
  if(!sb) return;
  var r=await sb.from('services').select('*').eq('available',true).order('sort_order');
  if(r.data){
    GROUPS[0].items=[];GROUPS[1].items=[];
    r.data.forEach(function(s){
      var item={name:s.name,time:s.duration_minutes+' min',price:'\u00a3'+Number(s.price)};
      if(s.category==='Waxing') GROUPS[0].items.push(item);
      else if(s.category==='Intimate Care') GROUPS[1].items.push(item);
    });
    BOOKABLE=GROUPS[0].items.concat(GROUPS[1].items);
  }
}

async function fetchMonthBookings(v){
  var y=v.getFullYear(),m=v.getMonth(),key=y+"-"+m;
  if(CAL_CACHE[key])return CAL_CACHE[key];
  if(!sb)return[];
  var startStr=y+"-"+String(m+1).padStart(2,'0')+"-01";
  var dim=new Date(y,m+1,0).getDate();
  var endStr=y+"-"+String(m+1).padStart(2,'0')+"-"+String(dim).padStart(2,'0');
  var r=await sb.from('bookings').select('appointment_date, appointment_time, treatment_name').gte('appointment_date',startStr).lte('appointment_date',endStr).neq('status','cancelled');
  CAL_CACHE[key]=r.data||[];
  return CAL_CACHE[key];
}

function calcSlots(d){
  var y=d.getFullYear(),m=d.getMonth(),day=d.getDate();
  var key=y+"-"+m;
  var dateStr=y+"-"+String(m+1).padStart(2,'0')+"-"+String(day).padStart(2,'0');
  var bookings=CAL_CACHE[key]||[];
  var dayBookings=bookings.filter(function(b){return b.appointment_date===dateStr;});
  var dur=getDuration(S.treatment);
  var dayMap=['sun','mon','tue','wed','thu','fri','sat'];
  var dk=dayMap[d.getDay()];
  var hrs=OPENING_HOURS[dk]||{open:'9.00',close:'18.00'};
  var start=dotTimeToMins(hrs.open),end=dotTimeToMins(hrs.close),step=15;
  var now=new Date();
  var isToday=d.getFullYear()===now.getFullYear()&&d.getMonth()===now.getMonth()&&d.getDate()===now.getDate();
  var nowMins=isToday?now.getHours()*60+now.getMinutes():0;
  var slots=[];
  for(var t=start;t+dur<=end;t+=step){
    if(isToday&&t<=nowMins)continue;
    var t_end=t+dur,overlap=false;
    for(var i=0;i<dayBookings.length;i++){
      var b=dayBookings[i];
      var b_start=timeToMins(b.appointment_time);
      var b_dur=getDuration(b.treatment_name);
      var b_end=b_start+b_dur;
      if(t<b_end&&t_end>b_start){overlap=true;break;}
    }
    if(!overlap)slots.push({label:minsToTime(t),open:true});
  }
  return slots;
}

function dayOpen(d){var w=d.getDay();if(w===0||w===1)return false;var k=d.getFullYear()+'-'+d.getMonth()+'-'+d.getDate();return!CLOSED_DAYS[k];}
function dayFree(d){return calcSlots(d).length>0;}
function slotList(d){return calcSlots(d);}

/* ─── Rendering: Picker ─── */
function renderPicker(){
  var q=S.query.trim().toLowerCase();
  var list=q?BOOKABLE.filter(function(i){return i.name.toLowerCase().indexOf(q)>-1;}):BOOKABLE;
  var box=$("picker");if(!box)return;
  box.innerHTML="";
  if(!list.length){
    box.appendChild(el("div",{style:"padding:18px 2px;font-size:14px;color:#B39C88"},'No treatment by that name. Clear the search to see everything, or tell us in the notes at the next step.'));
  }
  list.forEach(function(it){
    var b=el("button",{class:"srow","aria-checked":String(S.treatment===it.name),onclick:function(){S.treatment=it.name;renderPicker();if(typeof renderTracker==='function')renderTracker();syncNext();}});
    b.innerHTML='<span style="flex:1;text-align:left;font-family:Marcellus,serif;font-size:17px">'+it.name+'</span>'+
      '<span style="font-size:12.5px;color:#B39C88">'+it.time+'</span>'+
      '<span style="font-size:14.5px;font-weight:600;min-width:78px;text-align:right">'+it.price+'</span><span class="tick"></span>';
    box.appendChild(b);
  });
}

/* ─── Rendering: Calendar ─── */
async function renderCalendar(){
  var v=viewMonth();
  if($("month"))$("month").textContent=v.toLocaleDateString("en-GB",{month:"long",year:"numeric"});
  if($("prev"))$("prev").style.opacity=S.monthOffset>0?"1":".35";
  var firstDow=(v.getDay()+6)%7,dim=new Date(v.getFullYear(),v.getMonth()+1,0).getDate(),t=today();
  var box=$("cells");if(!box)return;
  box.innerHTML="<div style='grid-column:1/-1;padding:20px;text-align:center;color:#B39C88'>Loading...</div>";
  await fetchMonthBookings(v);
  box.innerHTML="";
  for(var i=0;i<firstDow;i++)box.appendChild(el("div",{style:"height:44px"}));
  for(var day=1;day<=dim;day++){
    (function(day){
      var d=new Date(v.getFullYear(),v.getMonth(),day);
      var key=d.getFullYear()+"-"+d.getMonth()+"-"+day;
      var usable=d>=t&&dayOpen(d)&&dayFree(d);
      var b=el("button",{class:"day",style:"height:44px;font-family:Mulish,sans-serif;font-size:14.5px;background:transparent;color:#E8D5C4;border:1px solid rgba(232,213,196,.22);cursor:pointer","aria-pressed":String(S.dateKey===key)},String(day));
      if(!usable){b.setAttribute("disabled","disabled");b.style.color="rgba(232,213,196,.22)";b.style.borderColor="transparent";b.style.cursor="default";}
      else b.onclick=function(){S.dateKey=key;S.time="";renderCalendar();renderSlots();if(typeof renderTracker==='function')renderTracker();syncNext();};
      if(d.getTime()===t.getTime())b.style.boxShadow="inset 0 0 0 1px rgba(232,213,196,.35)";
      if(S.dateKey===key){b.style.background="#E8D5C4";b.style.color="#3A322E";b.style.borderColor="#E8D5C4";b.style.fontWeight="600";}
      box.appendChild(b);
    })(day);
  }
}

function renderSlots(){
  var d=chosenDate(),box=$("slots");if(!box)return;box.innerHTML="";
  if($("slots-label"))$("slots-label").textContent=d?"Times on "+longDate(d):"Choose a day to see times";
  if(!d)return;
  slotList(d).forEach(function(sl){
    var b=el("button",{class:"chip","aria-pressed":String(S.time===sl.label)},sl.label);
    if(!sl.open)b.setAttribute("disabled","disabled");
    else b.onclick=function(){S.time=sl.label;renderSlots();if(typeof renderTracker==='function')renderTracker();syncNext();};
    box.appendChild(b);
  });
}

/* ─── Rendering: Tracker (desktop only) ─── */
function renderTracker(){
  if(!$("tracker"))return;
  var titles=["Treatment","Date & time","You & your account","Deposit"];
  var vals=[S.treatment,whenLabel(),
    ($("f-name")&&$("f-name").value.trim()?$("f-name").value.trim()+(wantsAccount()?(S.returning?" \u00b7 signing in":" \u00b7 account included"):""):"Mobile number and name"),
    "\u00a310, refundable"];
  var t=$("tracker");t.innerHTML="";
  titles.forEach(function(title,i){
    var n=i+1,active=S.step>=n;
    t.appendChild(el("div",{style:"display:grid;grid-template-columns:44px 1fr;gap:16px;padding:16px 0;border-top:1px solid rgba(232,213,196,.16);opacity:"+(active?"1":".55")},
      '<span style="font-family:Marcellus,serif;font-size:17px;color:'+(S.step===n?"#E8D5C4":"#B39C88")+'">0'+n+'</span>'+
      '<div><div style="font-family:Marcellus,serif;font-size:19px;color:#E8D5C4">'+title+'</div>'+
      '<div style="font-size:13px;color:#B39C88;margin-top:4px">'+vals[i]+'</div></div>'));
  });
  /* progress bars */
  var bars=$("bars");
  if(bars){
    bars.innerHTML="";
    [1,2,3,4].forEach(function(n){bars.appendChild(el("div",{style:"height:3px;flex:1;max-width:"+(n===S.step?"44px":"26px")+";background:"+(n<=S.step?"#E8D5C4":"rgba(232,213,196,.25)")}));});
  }
  if($("step-label"))$("step-label").textContent="Step "+S.step+" of 4";
}

/* ─── Step control ─── */
function syncNext(){
  var ok=ready(),b=$("next");
  if(!b)return;
  b.textContent=S.step<3?"Continue":S.step===3?"Continue to deposit":"Pay \u00a310 and confirm";
  b.style.background=ok?"#E8D5C4":"rgba(232,213,196,.28)";
  b.style.cursor=ok?"pointer":"default";
  if($("back"))$("back").className=S.step>1?"":"hide";
  if($("helper"))$("helper").textContent=S.step===1?"First visits include a consultation and extra time, at no extra cost."
    :S.step===2?"Crossed-out times are already taken. Closed Sunday and Monday."
    :S.step===3?(wantsAccount()?"We\u2019ll email you a six-digit code after payment \u2014 that opens your account. No password.":"Next: a \u00a310 deposit holds the room. Refundable up to 24 hours before.")
    :"Payment is secure. The balance is paid in the studio.";
}

function showStep(){
  [1,2,3,4].forEach(function(n){var e=$("step"+n);if(e)e.className=S.step===n?"":"hide";});
  if(S.step===3){if($("s3-treat"))$("s3-treat").textContent=S.treatment;if($("s3-when"))$("s3-when").textContent=whenLabel();}
  if(S.step===4){
    if($("s4-treat"))$("s4-treat").textContent=S.treatment;
    if($("s4-price"))$("s4-price").textContent=priceOf(S.treatment);
    if($("s4-when"))$("s4-when").textContent=whenLabel();
    if($("s4-name"))$("s4-name").textContent=$("f-name")?$("f-name").value.trim():"";
    var p=priceNum(S.treatment),bal=p-10;
    if(S.promo){
      if($("s4-promo-row"))$("s4-promo-row").className="";
      if($("s4-promo-code"))$("s4-promo-code").textContent="Promo: "+S.promo.code;
      if($("s4-promo-discount"))$("s4-promo-discount").textContent="\u2212\u00a3"+S.promo.discount.toFixed(2);
      bal=p-S.promo.discount-10;
    } else {
      if($("s4-promo-row"))$("s4-promo-row").className="hide";
    }
    var prefix=String(priceOf(S.treatment)).indexOf("from")===0?"from \u00a3":"\u00a3";
    if($("s4-bal"))$("s4-bal").textContent=prefix+Math.max(0,bal).toFixed(2);
  }
  /* mobile-specific: update progress bars inline */
  var bars=$("bars");
  if(bars&&!$("tracker")){
    bars.innerHTML="";
    [1,2,3,4].forEach(function(n){
      var d=document.createElement("div");
      d.style.cssText="height:3px;flex:1;background:"+(n<=S.step?"#E8D5C4":"rgba(232,213,196,.22)");
      bars.appendChild(d);
    });
    if($("step-label"))$("step-label").textContent="Step "+S.step+" of 4";
  }
  renderTracker();syncNext();
  /* scroll to booking on mobile */
  if(window.innerWidth<=820&&$("book"))window.scrollTo({top:$("book").offsetTop-40,behavior:"smooth"});
}

function ready(){
  if(S.step===1)return!!S.treatment;
  if(S.step===2)return!!(S.dateKey&&S.time);
  if(S.step===3){
    var contactInput=$("f-contact");
    var nameInput=$("f-name");
    if(contactInput&&nameInput)return contactInput.value.indexOf("@")>-1&&contactInput.value.indexOf(".")>-1&&!!nameInput.value.trim();
    return true;
  }
  return true;/* cardValid — real validation when Stripe is added */
}

async function checkKnown(){
  var contactInput=$("f-contact");
  if(!contactInput)return;
  var email=contactInput.value.trim().toLowerCase();
  if(!email||email.indexOf('@')===-1){
    if($("known"))$("known").className="hide";
    if($("f-name"))$("f-name").closest("label").style.display="";
    if($("f-phone"))$("f-phone").closest("label").style.display="";
    if($("acct-head"))$("acct-head").textContent="Keep this as my AMAI account";
    return;
  }
  if(!sb)return;
  var r=await sb.from('clients').select('*').eq('email',email).maybeSingle();
  S.returning=!!(r&&r.data);
  if(r&&r.data){
    if($("known"))$("known").className="";
    if($("known-copy"))$("known-copy").innerHTML='Welcome back, <strong style="font-weight:600">'+r.data.name+'</strong>. We\'ve found your account \u2014 your stamps and history are waiting.';
    if($("f-name")){$("f-name").value=r.data.name;$("f-name").closest("label").style.display="none";}
    if($("f-phone")&&r.data.phone){$("f-phone").value=r.data.phone;$("f-phone").closest("label").style.display="none";}
    if($("acct-head"))$("acct-head").textContent="Add this visit to my account";
  } else {
    if($("known"))$("known").className="hide";
    if($("f-name"))$("f-name").closest("label").style.display="";
    if($("f-phone"))$("f-phone").closest("label").style.display="";
    if($("acct-head"))$("acct-head").textContent="Keep this as my AMAI account";
  }
  syncNext();
}

/* ─── Payment / Submission ─── */
function saveToHub(){
  try{
    var raw=localStorage.getItem(HUB_KEY),h=raw?JSON.parse(raw):null;
    var visit={id:Date.now(),treat:S.treatment,dateKey:S.dateKey,time:S.time,price:priceNum(S.treatment),deposit:10};
    if(h&&h.upcoming){h.upcoming.push(visit);h.name=$("f-name")?$("f-name").value.trim():h.name;h.email=$("f-contact")?$("f-contact").value.trim():h.email;h.signedIn=true;}
    else{h={signedIn:true,name:$("f-name")?$("f-name").value.trim():"",email:$("f-contact")?$("f-contact").value.trim().toLowerCase():"",upcoming:[visit],pendingFromWeb:true};}
    localStorage.setItem(HUB_KEY,JSON.stringify(h));
  }catch(e){}
}

async function confirm(how){
  S.how=how;
  var name=$("f-name")?$("f-name").value.trim():"Thank you";
  if(!name)name="Thank you";
  /* hide all step containers */
  [1,2,3,4].forEach(function(n){var e=$("step"+n);if(e)e.className="hide";});
  if($("form-side"))$("form-side").className="hide";
  if($("navrow"))$("navrow").className="hide";
  if($("helper"))$("helper").textContent="";

  if(wantsAccount()){
    var email=$("f-contact")?$("f-contact").value.trim().toLowerCase():"";
    $("v-title").textContent=name+", you\u2019re booked in.";
    $("v-sub").textContent=S.returning?"One code and you\u2019re back in your account.":"One code and your account is open.";
    $("v-treat").textContent=S.treatment;
    $("v-when").textContent=whenLabel();
    if($("v-code-label"))$("v-code-label").textContent="Sending code to "+email+"\u2026";
    if($("verify-side"))$("verify-side").className="";
    /* scroll on mobile */
    if($("book"))window.scrollTo({top:$("book").offsetTop-40,behavior:"smooth"});
    /* send real OTP */
    if(sb){
      var res=await sb.auth.signInWithOtp({email:email,options:{shouldCreateUser:true}});
      if(res.error){if($("v-code-label"))$("v-code-label").textContent="Could not send code: "+res.error.message;}
      else{if($("v-code-label"))$("v-code-label").textContent="Code emailed to "+email;}
    }
    setTimeout(function(){if($("v-code"))$("v-code").focus();},60);
    return;
  }
  showDone(how,false);
}

async function showDone(how,acct){
  var name=$("f-name")?$("f-name").value.trim():"Thank you";
  if(!name)name="Thank you";
  var email=$("f-contact")?$("f-contact").value.trim():"";
  var phone=$("f-phone")?$("f-phone").value.trim():"";
  var notes=$("f-note")?$("f-note").value.trim():"";

  /* save to DB */
  if(sb){
    try{
      var r=await sb.from('clients').select('id,phone').eq('email',email);
      var clientId;
      if(!r.data||r.data.length===0){
        var ins=await sb.from('clients').insert([{name:name,email:email,phone:phone}]).select().single();
        if(ins.data)clientId=ins.data.id;
      } else {
        clientId=r.data[0].id;
        if(phone&&r.data[0].phone!==phone)await sb.from('clients').update({phone:phone}).eq('id',clientId);
      }
      if(clientId){
        await sb.from('bookings').insert([{
          client_id:clientId,
          treatment_name:S.treatment,
          appointment_date:dayKeyToDate(S.dateKey),appointment_time:S.time.replace('.',':'),
          price:priceNum(S.treatment),deposit_amount:10,
          duration_minutes:getDuration(S.treatment),status:'confirmed',
          notes:notes,
          promo_code:S.promo?S.promo.code:null,
          discount_amount:S.promo?S.promo.discount:0
        }]);
      }
    }catch(e){console.warn('booking save error',e);}
  }

  /* update done UI */
  if($("d-title"))$("d-title").textContent=acct?(S.returning?name+", you\u2019re booked and signed in.":name+", your account is ready."):name+", you\u2019re booked in.";
  if($("d-treat"))$("d-treat").textContent=S.treatment;
  if($("d-when"))$("d-when").textContent=whenLabel();
  if($("d-paid"))$("d-paid").textContent=how==="apple"?"\u00a310 paid \u00b7 Apple Pay":"\u00a310 deposit to be paid later";
  if($("d-bal"))$("d-bal").textContent=balanceOf(S.treatment)+" in the studio";
  var hasHub = acct;
  try { var h=JSON.parse(localStorage.getItem('amai_hub')||'{}'); if(h&&h.signedIn) hasHub=true; } catch(e){}
  if($("d-hub"))$("d-hub").className=hasHub?"btn":"hide";

  /* hide everything, show done */
  [1,2,3,4].forEach(function(n){var e=$("step"+n);if(e)e.className="hide";});
  if($("form-side"))$("form-side").className="hide";
  if($("verify-side"))$("verify-side").className="hide";
  if($("navrow"))$("navrow").className="hide";
  if($("helper"))$("helper").textContent="";
  if($("done-side"))$("done-side").className="";
}

/* ─── Event bindings ─── */
function bindBookingEvents(){
  if($("q"))$("q").oninput=function(){S.query=this.value;renderPicker();};
  if($("prev"))$("prev").onclick=function(){if(S.monthOffset>0){S.monthOffset--;renderCalendar();}};
  if($("next-m"))$("next-m").onclick=function(){S.monthOffset++;renderCalendar();};
  if($("f-contact")){
    $("f-contact").oninput=function(){if(typeof renderTracker==='function')renderTracker();syncNext();};
    $("f-contact").onblur=function(){checkKnown();if(typeof renderTracker==='function')renderTracker();syncNext();};
  }
  if($("f-acct"))$("f-acct").onchange=function(){if(typeof renderTracker==='function')renderTracker();syncNext();};
  ["f-name","c-num","c-exp","c-cvc"].forEach(function(id){if($(id))$(id).oninput=function(){if(typeof renderTracker==='function')renderTracker();syncNext();};});
  if($("next"))$("next").onclick=function(){if(!ready())return;if(S.step<4){S.step++;showStep();}else confirm("card");};
  if($("back"))$("back").onclick=function(){if(S.step>1){S.step--;showStep();}};
  if($("apple"))$("apple").onclick=function(){confirm("apple");};
  if($("v-code"))$("v-code").oninput=function(){
    this.value=digits(this.value).slice(0,6);
    var ok=this.value.length===6,b=$("v-go");
    if(b){b.style.background=ok?"#E8D5C4":"rgba(232,213,196,.28)";b.style.cursor=ok?"pointer":"default";}
  };
  if($("v-go"))$("v-go").onclick=async function(){
    if(digits($("v-code").value).length!==6)return;
    var email=$("f-contact")?$("f-contact").value.trim().toLowerCase():"";
    $("v-go").textContent="Verifying\u2026";
    if(sb){
      var res=await sb.auth.verifyOtp({email:email,token:$("v-code").value.trim(),type:'email'});
      $("v-go").textContent="Open my account";
      if(res.error){if($("v-code-label"))$("v-code-label").textContent=res.error.message;return;}
    }
    saveToHub();showDone(S.how,true);
  };
  if($("v-skip"))$("v-skip").onclick=function(){showDone(S.how,false);};
  if($("again"))$("again").onclick=function(){
    S={group:S.group,step:1,treatment:(BOOKABLE.length?BOOKABLE[0].name:""),monthOffset:0,dateKey:"",time:"",query:"",paid:"",how:"",sent:false,returning:false,promo:null};
    ["f-name","f-phone","f-promo","f-contact","f-note","c-num","c-exp","c-cvc","q","v-code"].forEach(function(id){if($(id))$(id).value="";});
    if($("promo-result"))$("promo-result").innerHTML="";
    if($("f-name"))$("f-name").closest("label").style.display="";
    if($("f-phone"))$("f-phone").closest("label").style.display="";
    if($("f-acct"))$("f-acct").checked=true;
    checkKnown();
    if($("done-side"))$("done-side").className="hide";
    if($("verify-side"))$("verify-side").className="hide";
    if($("form-side"))$("form-side").className="";
    if($("navrow"))$("navrow").className="";
    renderPicker();renderCalendar();renderSlots();showStep();
  };
  /* promo code (desktop-only for now) */
  if($("apply-promo")){
    $("apply-promo").onclick=async function(){
      var code=$("f-promo")?$("f-promo").value.trim().toUpperCase():"";
      if(!code||!sb)return;
      var r=await sb.from('promos').select('*').eq('code',code).eq('active',true).maybeSingle();
      var res=$("promo-result");
      if(!r.data){if(res)res.innerHTML='<span style="color:#ef4444">Invalid or expired promo code.</span>';S.promo=null;showStep();return;}
      if(r.data.cap>0&&r.data.uses>=r.data.cap){if(res)res.innerHTML='<span style="color:#ef4444">This promo code has reached its usage limit.</span>';S.promo=null;showStep();return;}
      if(r.data.until&&new Date(r.data.until)<today()){if(res)res.innerHTML='<span style="color:#ef4444">This promo code has expired.</span>';S.promo=null;showStep();return;}
      var p=priceNum(S.treatment),discount=0;
      if(r.data.kind==='%')discount=p*(r.data.value/100);
      else if(r.data.kind==='\u00a3')discount=r.data.value;
      S.promo={code:code,discount:discount};
      if(res)res.innerHTML='<span style="color:#4ade80">'+code+' applied \u2014 '+(r.data.kind==='%'?r.data.value+'% off':'\u00a3'+r.data.value+' off')+' (\u2212\u00a3'+discount.toFixed(2)+')</span>';
      showStep();
    };
  }
}

/* ─── Day-of-week header ─── */
function renderDOW(){
  var d=$("dow");if(!d||d.children.length>0)return;
  ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].forEach(function(w){
    d.appendChild(el("div",{style:"text-align:center;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#B39C88;padding-bottom:4px"},w));
  });
}

/* ─── Init ─── */
async function initBooking(){
  await loadSupabaseSDK();
  await loadServicesIntoGroups();
  /* load closed days */
  if(sb){
    try{var cd=await sb.from('closed_days').select('date_key');if(cd.data)cd.data.forEach(function(r){CLOSED_DAYS[r.date_key]=true;});}catch(e){}
    try{
      var sh=await sb.from('studio_settings').select('value').eq('key','opening_hours').single();
      if(sh.data&&sh.data.value){
        OPENING_HOURS=sh.data.value;
        if($('footer-hours')){var t=OPENING_HOURS.tue||{open:'9.00',close:'18.00'};$('footer-hours').innerHTML='Tuesday to Saturday<br>'+t.open+' \u2013 '+t.close;}
      }
    }catch(e){}
  }
  if(BOOKABLE.length)S.treatment=BOOKABLE[0].name;
  renderDOW();
  bindBookingEvents();
  renderPicker();renderCalendar();renderSlots();checkKnown();showStep();
}
