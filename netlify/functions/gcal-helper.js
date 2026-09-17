/**
 * Shared Google Calendar helper for Netlify Functions
 * Uses service account credentials to manage events
 */
const { GoogleAuth } = require('google-auth-library');

const CALENDAR_ID = process.env.GCAL_CALENDAR_ID;
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
 * Create a calendar event
 */
async function createEvent({ summary, description, startTime, endTime, bookingId }) {
  const token = await getToken();
  const url = `${BASE}/calendars/${encodeURIComponent(CALENDAR_ID)}/events`;

  const body = {
    summary,
    description,
    start: { dateTime: startTime, timeZone: 'Europe/London' },
    end: { dateTime: endTime, timeZone: 'Europe/London' },
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
 * Delete a calendar event
 */
async function deleteEvent(eventId) {
  const token = await getToken();
  const url = `${BASE}/calendars/${encodeURIComponent(CALENDAR_ID)}/events/${eventId}`;

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
 * List events in a time range
 */
async function listEvents(timeMin, timeMax) {
  const token = await getToken();
  const params = new URLSearchParams({
    timeMin,
    timeMax,
    singleEvents: 'true',
    orderBy: 'startTime',
    showDeleted: 'false',
    maxResults: '250',
  });

  const url = `${BASE}/calendars/${encodeURIComponent(CALENDAR_ID)}/events?${params}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) throw new Error(`GCal listEvents failed: ${await res.text()}`);
  const data = await res.json();
  return data;
}

/**
 * Incremental sync using syncToken
 */
async function incrementalSync(syncToken) {
  const token = await getToken();
  const params = new URLSearchParams({ singleEvents: 'true' });
  if (syncToken) params.append('syncToken', syncToken);

  const url = `${BASE}/calendars/${encodeURIComponent(CALENDAR_ID)}/events?${params}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });

  // 410 Gone = syncToken expired, need full sync
  if (res.status === 410) {
    return { expired: true, items: [], nextSyncToken: null };
  }
  if (!res.ok) throw new Error(`GCal sync failed: ${await res.text()}`);

  const data = await res.json();
  return {
    expired: false,
    items: data.items || [],
    nextSyncToken: data.nextSyncToken || null,
  };
}

module.exports = { createEvent, deleteEvent, listEvents, incrementalSync, CALENDAR_ID };
