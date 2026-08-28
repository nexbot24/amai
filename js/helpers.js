/* ─── AMAI Shared Helpers (single source of truth) ─── */
/* Used by: booking.js, hub.html, ipad/index.html */

/* ─── DOM ─── */
var $ = function(id) { return document.getElementById(id); };

/* ─── Date helpers ─── */
/* Key format: "YYYY-M-D" (month is 0-indexed, matching JS Date) */
function iso(d) {
  return d.getFullYear() + '-' + d.getMonth() + '-' + d.getDate();
}

function parseKey(k) {
  var p = k.split('-');
  return new Date(+p[0], +p[1], +p[2]);
}

function dayKeyToDate(k) {
  var p = k.split('-');
  var d = new Date(+p[0], +p[1], +p[2]);
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}

function dateToDayKey(isoStr) {
  var d = new Date(isoStr + 'T00:00:00');
  return d.getFullYear() + '-' + d.getMonth() + '-' + d.getDate();
}

function addDays(n) {
  var d = new Date();
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() + n);
  return d;
}

function today() {
  var d = new Date();
  d.setHours(0, 0, 0, 0);
  return d;
}

function longDate(d) {
  return d.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' });
}

function shortDate(d) {
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
}

/* ─── Currency ─── */
function money(v) {
  var n = parseFloat(String(v).replace(/[^0-9.]/g, ''));
  if (isNaN(n)) return String(v);
  return '£' + n;
}
