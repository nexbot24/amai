/**
 * gcal-update: Update a Google Calendar event when a booking is rescheduled
 */
const { GoogleAuth } = require('google-auth-library');

const PUSH_CALENDAR_ID = process.env.GCAL_PUSH_CALENDAR_ID;
const SCOPES = ['https://www.googleapis.com/auth/calendar'];

let _auth = null;
function getAuth() {
  if (_auth) return _auth;
  const creds = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT);
  _auth = new GoogleAuth({ credentials: creds, scopes: SCOPES });
  return _auth;
}

async function getToken() {
  const auth = getAuth();
  const client = await auth.getClient();
  const { token } = await client.getAccessToken();
  return token;
}

exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers, body: 'Method Not Allowed' };
  }

  try {
    const { gcalEventId, date, time, duration } = JSON.parse(event.body);
    if (!gcalEventId) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: 'Missing gcalEventId' }) };
    }

    const token = await getToken();
    const BASE = 'https://www.googleapis.com/calendar/v3';
    const calId = encodeURIComponent(PUSH_CALENDAR_ID);

    // Build new start/end times
    const cleanTime = String(time).replace('.', ':');
    const [h, m] = cleanTime.split(':').map(Number);
    const startDate = new Date(`${date}T${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:00`);
    const endDate = new Date(startDate.getTime() + (duration || 60) * 60000);

    const fmt = (d) => {
      const pad = (n) => String(n).padStart(2, '0');
      return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:00`;
    };

    const res = await fetch(`${BASE}/calendars/${calId}/events/${gcalEventId}`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        start: { dateTime: fmt(startDate), timeZone: 'Europe/London' },
        end: { dateTime: fmt(endDate), timeZone: 'Europe/London' },
      }),
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(`GCal update failed [${res.status}]: ${err}`);
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true }),
    };
  } catch (err) {
    console.error('gcal-update error:', err);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: err.message }),
    };
  }
};
