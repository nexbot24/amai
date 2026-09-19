/**
 * gcal-pull: Poll Google Calendar for external events (Fresha bookings)
 * Scheduled to run every 5 minutes via Netlify Scheduled Functions
 * 
 * Syncs external calendar events → Supabase bookings table
 */
const { listEvents } = require('./gcal-helper');
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

// Netlify Scheduled Function config
exports.config = {
  schedule: '*/5 * * * *'  // every 5 minutes
};

exports.handler = async (event) => {
  try {
    // Look 60 days ahead for events
    const now = new Date();
    const future = new Date(now.getTime() + 60 * 24 * 60 * 60000);
    const timeMin = now.toISOString();
    const timeMax = future.toISOString();

    // Fetch all events from Google Calendar
    const data = await listEvents(timeMin, timeMax);
    const gcalEvents = data.items || [];

    // Get all existing bookings with gcal_event_id to avoid duplicates
    const { data: existingBookings } = await supabase
      .from('bookings')
      .select('id, gcal_event_id, status')
      .not('gcal_event_id', 'is', null);

    const existingIds = new Set((existingBookings || []).map(b => b.gcal_event_id));

    // Get all AMAI-created event IDs (these have extendedProperties.private.source = 'amai')
    let synced = 0;
    let removed = 0;

    for (const ev of gcalEvents) {
      // Skip events created by AMAI (they have our marker)
      const priv = ev.extendedProperties && ev.extendedProperties.private;
      if (priv && priv.source === 'amai') continue;

      // Skip all-day events (no dateTime means it's an all-day event)
      if (!ev.start || !ev.start.dateTime) continue;

      // Skip if we already have this event
      if (existingIds.has(ev.id)) continue;

      // Parse the event into a booking
      const start = new Date(ev.start.dateTime);
      const end = new Date(ev.end.dateTime);
      const durationMins = Math.round((end - start) / 60000);

      // Extract date and time
      const appointmentDate = `${start.getFullYear()}-${String(start.getMonth() + 1).padStart(2, '0')}-${String(start.getDate()).padStart(2, '0')}`;
      const appointmentTime = `${String(start.getHours()).padStart(2, '0')}:${String(start.getMinutes()).padStart(2, '0')}`;

      // Insert as a Fresha/external booking
      const { error } = await supabase.from('bookings').insert([{
        treatment_name: ev.summary || 'External booking',
        appointment_date: appointmentDate,
        appointment_time: appointmentTime,
        duration_minutes: durationMins || 60,
        status: 'confirmed',
        source: 'fresha',
        gcal_event_id: ev.id,
        external_title: ev.summary || '',
        notes: `Synced from Google Calendar\n${ev.description || ''}`.trim(),
      }]);

      if (!error) synced++;
      else console.warn('Insert error for event', ev.id, error.message);
    }

    // Check for MOVED Fresha events (time/date changed)
    let updated = 0;
    const { data: allFreshaBookings } = await supabase
      .from('bookings')
      .select('id, gcal_event_id, appointment_date, appointment_time')
      .eq('source', 'fresha')
      .eq('status', 'confirmed');

    if (allFreshaBookings) {
      const gcalMap = {};
      for (const ev of gcalEvents) {
        if (ev.start && ev.start.dateTime) gcalMap[ev.id] = ev;
      }

      for (const fb of allFreshaBookings) {
        const ev = gcalMap[fb.gcal_event_id];
        if (!ev) continue; // handled by deletion check below

        const start = new Date(ev.start.dateTime);
        const newDate = `${start.getFullYear()}-${String(start.getMonth() + 1).padStart(2, '0')}-${String(start.getDate()).padStart(2, '0')}`;
        const newTime = `${String(start.getHours()).padStart(2, '0')}:${String(start.getMinutes()).padStart(2, '0')}`;
        const end = new Date(ev.end.dateTime);
        const newDur = Math.round((end - start) / 60000);

        if (fb.appointment_date !== newDate || fb.appointment_time !== newTime) {
          await supabase.from('bookings').update({
            appointment_date: newDate,
            appointment_time: newTime,
            duration_minutes: newDur || 60,
            external_title: ev.summary || '',
          }).eq('id', fb.id);
          updated++;
        }
      }
    }

    // Check for deleted/cancelled external events
    // Get all fresha bookings and see if their gcal events still exist
    const { data: freshaBookings } = await supabase
      .from('bookings')
      .select('id, gcal_event_id')
      .eq('source', 'fresha')
      .eq('status', 'confirmed');

    if (freshaBookings) {
      const activeGcalIds = new Set(gcalEvents.map(e => e.id));
      for (const fb of freshaBookings) {
        if (fb.gcal_event_id && !activeGcalIds.has(fb.gcal_event_id)) {
          // Event was deleted from calendar — cancel the booking
          await supabase
            .from('bookings')
            .update({ status: 'cancelled' })
            .eq('id', fb.id);
          removed++;
        }
      }
    }

    console.log(`gcal-pull: synced=${synced}, updated=${updated}, removed=${removed}, total_events=${gcalEvents.length}`);

    return {
      statusCode: 200,
      body: JSON.stringify({ synced, updated, removed, totalEvents: gcalEvents.length }),
    };
  } catch (err) {
    console.error('gcal-pull error:', err);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message }),
    };
  }
};
