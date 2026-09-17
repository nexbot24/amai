/**
 * gcal-push: Push an AMAI booking to Google Calendar
 * Called after a booking is saved to Supabase
 */
const { createEvent } = require('./gcal-helper');
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers, body: '' };
  }

  try {
    const { bookingId, treatmentName, date, time, duration, clientName } = JSON.parse(event.body);

    // Build start/end times in ISO format
    // date is like "2026-09-20", time is like "10:00" or "10.00"
    const cleanTime = String(time).replace('.', ':');
    const [h, m] = cleanTime.split(':').map(Number);
    const startDate = new Date(`${date}T${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:00`);
    const endDate = new Date(startDate.getTime() + (duration || 60) * 60000);

    // Format as ISO with London timezone offset
    const fmt = (d) => {
      const pad = (n) => String(n).padStart(2, '0');
      return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:00`;
    };

    const gcalEvent = await createEvent({
      summary: `AMAI: ${treatmentName} — ${clientName}`,
      description: `Client: ${clientName}\nTreatment: ${treatmentName}\nDuration: ${duration || 60} min\nBooked via AMAI website`,
      startTime: fmt(startDate),
      endTime: fmt(endDate),
      bookingId: bookingId || '',
    });

    // Save the GCal event ID back to the booking row
    if (bookingId && gcalEvent.id) {
      await supabase
        .from('bookings')
        .update({ gcal_event_id: gcalEvent.id })
        .eq('id', bookingId);
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, eventId: gcalEvent.id }),
    };
  } catch (err) {
    console.error('gcal-push error:', err);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: err.message }),
    };
  }
};
