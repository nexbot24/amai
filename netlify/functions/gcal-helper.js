/**
 * Shared Google Calendar helper for Netlify Functions
 * Uses service account credentials to manage events
 * 
 * Two calendars:
 *  - PUSH calendar (primary): where AMAI events go so Fresha sees them
 *  - PULL calendar (Fresha): where we read Fresha bookings from
 */
const { GoogleAuth } = require('google-auth-library');

const PUSH_CALENDAR_ID = process.env.GCAL_PUSH_CALENDAR_ID;  // primary calendar
const PULL_CALENDAR_ID = process.env.GCAL_CALENDAR_ID;        // Fresha calendar
const SCOPES = ['https://www.googleapis.com/auth/calendar'];

let _auth = null;
function getAuth() {
  if (_auth) return _auth;
  const creds = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT);
  _auth = new GoogleAuth({
    credentials: creds,
    scopes: SCOPES,
  });
  return _auth;
}

async function getToken() {
  const auth = getAuth();
  const client = await auth.getClient();
  const { token } = await client.getAccessToken();
  return token;
}

const BASE = 'https://www.googleapis.com/calendar/v3';

/**
 * Create a calendar event on the PRIMARY calendar (so Fresha sees it)
 */
async function createEvent({ summary, description, startTime, endTime, bookingId }) {
  const token = await getToken();
  const calId = PUSH_CALENDAR_ID;
  const url = `${BASE}/calendars/${encodeURIComponent(calId)}/events`;

  const body = {
    summary,
    description,
    start: { dateTime: startTime, timeZone: 'Europe/London' },
    end: { dateTime: endTime, timeZone: 'Europe/London' },
    transparency: 'opaque',  // Shows as "Busy" — required for Fresha to pick it up
    status: 'confirmed',
    extendedProperties: {
      private: {
        bookingId: String(bookingId || ''),
        source: 'amai'
      }
    }
  };

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`GCal createEvent failed [${res.status}]: ${err}`);
  }
  return await res.json();
}

/**
 * Delete a calendar event from the PRIMARY calendar
 */
async function deleteEvent(eventId) {
  const token = await getToken();
  const calId = PUSH_CALENDAR_ID;
  const url = `${BASE}/calendars/${encodeURIComponent(calId)}/events/${eventId}`;

  const res = await fetch(url, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok && res.status !== 404 && res.status !== 410) {
    const err = await res.text();
    throw new Error(`GCal deleteEvent failed [${res.status}]: ${err}`);
  }
  return true;
}

/**
 * List events from the FRESHA calendar (to pull Fresha bookings)
 */
async function listEvents(timeMin, timeMax) {
  const token = await getToken();
  const calId = PULL_CALENDAR_ID;
  const params = new URLSearchParams({
    timeMin,
    timeMax,
    singleEvents: 'true',
    orderBy: 'startTime',
    showDeleted: 'false',
    maxResults: '250',
  });

  const url = `${BASE}/calendars/${encodeURIComponent(calId)}/events?${params}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) throw new Error(`GCal listEvents failed: ${await res.text()}`);
  const data = await res.json();
  return data;
}

module.exports = { createEvent, deleteEvent, listEvents, PUSH_CALENDAR_ID, PULL_CALENDAR_ID };
