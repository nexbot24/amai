/* ─── AMAI Calendar Engine (single source of truth) ─── */
/* Used by: booking.js, hub.html, ipad/index.html */

var CAL_CACHE = {};

var OPENING_HOURS = {
  tue: { open: '9.00', close: '18.00' },
  wed: { open: '9.00', close: '18.00' },
  thu: { open: '9.00', close: '18.00' },
  fri: { open: '9.00', close: '18.00' },
  sat: { open: '9.00', close: '18.00' }
};

var CLOSED_DAYS = {};

/* ─── Time helpers ─── */
function timeToMins(t) {
  if (!t) return 0;
  var p = String(t).split(/[:.]/);
  return parseInt(p[0], 10) * 60 + parseInt(p[1] || 0, 10);
}

function minsToTime(m) {
  var h = Math.floor(m / 60), mm = m % 60;
  return h + '.' + (mm < 10 ? '0' + mm : mm);
}

/* ─── Treatment duration lookup ─── */
/* Pass in the treatments array from wherever it's stored (BOOKABLE, TREATMENTS, etc.) */
function getDuration(name, treatments) {
  if (!treatments) treatments = window.BOOKABLE || window.TREATMENTS || [];
  var t = treatments.find(function(i) { return i.name === name; });
  if (!t) return 60;
  var match = String(t.time).match(/(\d+)/);
  return match ? parseInt(match[1], 10) : 60;
}

/* ─── Fetch bookings for a month (cached) ─── */
async function fetchMonthBookings(v) {
  var y = v.getFullYear(), m = v.getMonth();
  var key = y + '-' + m;
  if (CAL_CACHE[key]) return CAL_CACHE[key];
  if (!sb) return [];
  var startStr = y + '-' + String(m + 1).padStart(2, '0') + '-01';
  var dim = new Date(y, m + 1, 0).getDate();
  var endStr = y + '-' + String(m + 1).padStart(2, '0') + '-' + String(dim).padStart(2, '0');
  var r = await sb.from('bookings')
    .select('appointment_date, appointment_time, treatment_name')
    .gte('appointment_date', startStr)
    .lte('appointment_date', endStr)
    .neq('status', 'cancelled');
  CAL_CACHE[key] = r.data || [];
  return CAL_CACHE[key];
}

/* ─── Calculate available slots for a given day and treatment ─── */
function calcSlots(d, treatmentName) {
  var y = d.getFullYear(), m = d.getMonth(), day = d.getDate();
  var key = y + '-' + m;
  var dateStr = y + '-' + String(m + 1).padStart(2, '0') + '-' + String(day).padStart(2, '0');

  var bookings = CAL_CACHE[key] || [];
  var dayBookings = bookings.filter(function(b) { return b.appointment_date === dateStr; });

  var dur = getDuration(treatmentName);
  var dayMap = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
  var dk = dayMap[d.getDay()];
  var hrs = OPENING_HOURS[dk] || { open: '9.00', close: '18.00' };
  var start = timeToMins(hrs.open), end = timeToMins(hrs.close), step = 15;

  /* If today, skip times that have already passed */
  var now = new Date();
  var isToday = d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate();
  var nowMins = isToday ? now.getHours() * 60 + now.getMinutes() : 0;

  var slots = [];
  for (var t = start; t + dur <= end; t += step) {
    if (isToday && t <= nowMins) continue;
    var t_end = t + dur, overlap = false;
    for (var i = 0; i < dayBookings.length; i++) {
      var b = dayBookings[i];
      var b_start = timeToMins(b.appointment_time);
      var b_dur = getDuration(b.treatment_name);
      var b_end = b_start + b_dur;
      if (t < b_end && t_end > b_start) { overlap = true; break; }
    }
    if (!overlap) slots.push({ label: minsToTime(t), open: true });
  }
  return slots;
}

/* ─── Day availability checks ─── */
function dayOpen(d) {
  var w = d.getDay();
  if (w === 0 || w === 1) return false; /* closed Sun & Mon */
  var k = d.getFullYear() + '-' + d.getMonth() + '-' + d.getDate();
  return !CLOSED_DAYS[k];
}

function dayFree(d, treatmentName) {
  return dayOpen(d) && calcSlots(d, treatmentName).length > 0;
}

/* ─── Invalidate cache (call after a booking is made) ─── */
function clearCalCache() {
  CAL_CACHE = {};
}
