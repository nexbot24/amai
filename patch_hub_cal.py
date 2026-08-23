import re

with open('hub.html', 'r') as f:
    content = f.read()

helpers = '''var CAL_CACHE = {};

function timeToMins(t) {
  if(!t) return 0;
  var p = String(t).split(/[:.]/);
  return parseInt(p[0], 10) * 60 + parseInt(p[1]||0, 10);
}
function minsToTime(m) {
  var h = Math.floor(m / 60);
  var mm = m % 60;
  return h + "." + (mm < 10 ? "0" + mm : mm);
}
function getDuration(name) {
  var t = TREATMENTS.find(function(i){ return i.name === name; });
  if(!t) return 60;
  var match = String(t.time).match(/(\\d+)/);
  return match ? parseInt(match[1], 10) : 60;
}
async function fetchMonthBookings(v) {
  var y = v.getFullYear(), m = v.getMonth();
  var key = y + "-" + m;
  if (CAL_CACHE[key]) return CAL_CACHE[key];
  
  var startStr = y + "-" + String(m+1).padStart(2,'0') + "-01";
  var dim = new Date(y, m+1, 0).getDate();
  var endStr = y + "-" + String(m+1).padStart(2,'0') + "-" + String(dim).padStart(2,'0');

  var { data } = await supabase.from('bookings')
    .select('appointment_date, appointment_time, treatment_name')
    .gte('appointment_date', startStr)
    .lte('appointment_date', endStr)
    .neq('status', 'cancelled');
  
  CAL_CACHE[key] = data || [];
  return CAL_CACHE[key];
}

function calcSlots(d) {
  var y = d.getFullYear(), m = d.getMonth(), day = d.getDate();
  var key = y + "-" + m;
  var dateStr = y + "-" + String(m+1).padStart(2,'0') + "-" + String(day).padStart(2,'0');
  
  var bookings = CAL_CACHE[key] || [];
  var dayBookings = bookings.filter(function(b){ return b.appointment_date === dateStr; });
  
  var dur = getDuration(draft.treat);
  var start = 9 * 60; // 9:00
  var end = 18 * 60; // 18:00
  var step = 15;
  
  var slots = [];
  for (var t = start; t + dur <= end; t += step) {
    var t_end = t + dur;
    var overlap = false;
    for (var i=0; i<dayBookings.length; i++) {
      var b = dayBookings[i];
      var b_start = timeToMins(b.appointment_time);
      var b_dur = getDuration(b.treatment_name);
      var b_end = b_start + b_dur;
      if (t < b_end && t_end > b_start) {
        overlap = true;
        break;
      }
    }
    if (!overlap) slots.push({ label: minsToTime(t), open: true });
  }
  return slots;
}

async function calendarHTML(sel){
  var t=addDays(0), v=new Date(t.getFullYear(),t.getMonth()+calOffset,1);
  await fetchMonthBookings(v);
  
  var firstDow=(v.getDay()+6)%7, dim=new Date(v.getFullYear(),v.getMonth()+1,0).getDate();
  var cells="";
  for(var i=0;i<firstDow;i++) cells+='<div></div>';
  for(var d=1;d<=dim;d++){
    var day=new Date(v.getFullYear(),v.getMonth(),d), k=iso(day);
    var slots = calcSlots(day);
    var ok=day>=t&&day.getDay()!==0&&day.getDay()!==1&&slots.length>0;
    cells+='<button class="day" data-day="'+k+'" aria-pressed="'+(sel===k)+'"'+(ok?"":" disabled")+'>'+d+'</button>';
  }
  return '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">'+
    '<button class="btn btn-o btn-sm" id="cal-prev" style="padding:7px 14px'+(calOffset>0?'':';opacity:.35')+'">←</button>'+
    '<span class="serif" style="font-size:18px">'+v.toLocaleDateString("en-GB",{month:"long",year:"numeric"})+'</span>'+
    '<button class="btn btn-o btn-sm" id="cal-next" style="padding:7px 14px">→</button></div>'+
    '<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:5px;margin-bottom:6px">'+
    ["M","T","W","T","F","S","S"].map(function(w){ return '<div style="text-align:center;font-size:10px;letter-spacing:.1em;color:#8A7361">'+w+'</div>'; }).join("")+
    '</div><div style="display:grid;grid-template-columns:repeat(7,1fr);gap:5px" id="cal">'+cells+'</div>';
}
function slotsHTML(dayKey,sel){
  if(!dayKey) return '<p style="font-size:13.5px;color:#6E5B49;margin:0">Choose a day to see times.</p>';
  var d=parseKey(dayKey);
  var slots = calcSlots(d);
  if (slots.length === 0) return '<p style="font-size:13.5px;color:#6E5B49;margin:0">No times available.</p>';
  
  return slots.map(function(sl){
    var open=sl.open||sl.label===sel;
    return '<button class="chip" data-slot="'+sl.label+'" aria-pressed="'+(sel===sl.label)+'"'+(open?"":" disabled")+'>'+sl.label+'</button>';
  }).join("");
}
var draft={id:null,treat:"",price:0,dateKey:"",time:"",mode:"new"};
var lastModal=null;
function monthsFromNow(k){
  var d=parseKey(k), t=addDays(0);
  return (d.getFullYear()-t.getFullYear())*12 + d.getMonth()-t.getMonth();
}
async function bookingModal(title,intro,cta,keepOffset){
  if(!keepOffset) calOffset = draft.dateKey ? Math.max(0,monthsFromNow(draft.dateKey)) : 0;
  lastModal={t:title,i:intro,c:cta};
  
  // Show loading modal briefly
  modal('<div class="lbl" style="margin-bottom:14px">'+(draft.mode==="amend"?"Move your visit":"New booking")+'</div>'+
    '<h3 class="serif" style="font-size:26px;margin:0 0 8px">'+title+'</h3>'+
    '<p style="font-size:14.5px;line-height:1.7;color:#5C5148;margin:0 0 22px">'+intro+'</p>'+
    '<div style="padding:40px;text-align:center;color:#B39C88">Loading calendar...</div>');
    
  var calHtml = await calendarHTML(draft.dateKey);
  var sHtml = slotsHTML(draft.dateKey,draft.time);
  
  modal('<div class="lbl" style="margin-bottom:14px">'+(draft.mode==="amend"?"Move your visit":"New booking")+'</div>'+
    '<h3 class="serif" style="font-size:26px;margin:0 0 8px">'+title+'</h3>'+
    '<p style="font-size:14.5px;line-height:1.7;color:#5C5148;margin:0 0 22px">'+intro+'</p>'+
    calHtml+
    '<div class="lbl" style="margin:22px 0 10px" id="slabel">'+(draft.dateKey?"Times on "+longDate(parseKey(draft.dateKey)):"Times")+'</div>'+
    '<div style="display:flex;flex-wrap:wrap;gap:8px" id="slots">'+sHtml+'</div>'+
    '<div style="display:flex;gap:12px;margin-top:26px;padding-top:20px;border-top:1px solid #E0D2C2">'+
      '<button class="btn btn-o btn-sm" id="m-cancel">Back</button>'+
      '<button class="btn btn-sm" id="m-ok" style="flex:1"'+(draft.dateKey&&draft.time?'':' disabled')+'>'+cta+'</button></div>');
  bindBookingModal(cta);
}
function bindBookingModal(cta){
  $("m-cancel").onclick=closeModal;
  $("m-ok").onclick=async function(){
    if(!draft.dateKey||!draft.time) return;
    closeModal();
    if(draft.mode==="amend"){
      // We will actually update Supabase later, for now just ui
      S.upcoming.forEach(function(b){ if(b.id===draft.id){ b.dateKey=draft.dateKey; b.time=draft.time; } });
      save(); render();
    } else {
      var b={id:Date.now(),treat:draft.treat,dateKey:draft.dateKey,time:draft.time,price:draft.price,deposit:10};
      S.upcoming.push(b);
      // Actual Supabase insert
      var email = S.phone || "unknown@amai"; // Temporary fallback
      let { data: clients } = await supabase.from('clients').select('id').eq('email', email);
      let clientId;
      if (!clients || clients.length === 0) {
        const { data: newClient } = await supabase.from('clients').insert([{ name: S.name, email: email, phone: S.phone }]).select().single();
        if(newClient) clientId = newClient.id;
      } else {
        clientId = clients[0].id;
      }
      if(clientId) {
        await supabase.from('bookings').insert([{
          client_id: clientId,
          treatment_name: draft.treat,
          appointment_date: draft.dateKey,
          appointment_time: draft.time,
          price: draft.price,
          deposit_amount: 10,
          status: 'confirmed'
        }]);
      }
      save(); render();
    }
  };
  if($("cal-prev")) $("cal-prev").onclick=function(){ if(calOffset>0){ calOffset--; bookingModal(lastModal.t,lastModal.i,lastModal.c,true); } };
  if($("cal-next")) $("cal-next").onclick=function(){ calOffset++; bookingModal(lastModal.t,lastModal.i,lastModal.c,true); };
  [].forEach.call(document.querySelectorAll("[data-day]"),function(b){
    b.onclick=function(){ draft.dateKey=b.dataset.day; draft.time="";
      [].forEach.call(document.querySelectorAll("[data-day]"),function(x){ x.setAttribute("aria-pressed",String(x.dataset.day===draft.dateKey)); });
      $("slots").innerHTML=slotsHTML(draft.dateKey,draft.time);
      $("slabel").textContent="Times on "+longDate(parseKey(draft.dateKey));
      bindBookingModal(cta);
    };
  });
  [].forEach.call(document.querySelectorAll("[data-slot]"),function(b){
    b.onclick=function(){ draft.time=b.dataset.slot;
      [].forEach.call(document.querySelectorAll("[data-slot]"),function(x){ x.setAttribute("aria-pressed",String(x.dataset.slot===draft.time)); });
      bindBookingModal(cta);
    };
  });
}'''

start_str = "function calendarHTML(sel){"
end_str = "function bindBookingModal(cta){"

start_idx = content.find(start_str)
# Find the end of bindBookingModal
end_idx = content.find("function setupHub(){")

if start_idx != -1 and end_idx != -1:
    updated_content = content[:start_idx] + helpers + "\n" + content[end_idx:]
    with open('hub.html', 'w') as f:
        f.write(updated_content)
    print("Patched hub.html")
else:
    print("Could not find start/end bounds in hub.html")
