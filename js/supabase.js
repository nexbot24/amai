/* ─── AMAI Supabase Client (single source of truth) ─── */

var AMAI_SB_URL = 'https://tphyrmweauzfletdlqvi.supabase.co';
var AMAI_SB_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwaHlybXdlYXV6ZmxldGRscXZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc0NTIxOTQsImV4cCI6MjEwMzAyODE5NH0.Z_utKsxYquCoL2LfTjjL8QFB1tnLJZW9j3El7Sykk8o';

/* Initialise once — every page that includes this file gets the same client */
var sb = null;
(function() {
  if (window.supabase) {
    sb = window.supabase.createClient(AMAI_SB_URL, AMAI_SB_KEY);
    window.sb = sb;
  }
})();

/* For pages that load the SDK dynamically (e.g. booking.js) */
function ensureSupabase() {
  if (sb) return Promise.resolve(sb);
  return new Promise(function(resolve) {
    if (window.supabase) {
      sb = window.supabase.createClient(AMAI_SB_URL, AMAI_SB_KEY);
      window.sb = sb;
      resolve(sb);
      return;
    }
    var s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2';
    s.onload = function() {
      sb = window.supabase.createClient(AMAI_SB_URL, AMAI_SB_KEY);
      window.sb = sb;
      resolve(sb);
    };
    s.onerror = function() { resolve(null); };
    document.head.appendChild(s);
  });
}
