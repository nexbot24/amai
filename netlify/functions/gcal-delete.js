/**
 * gcal-delete: Remove a Google Calendar event when a booking is cancelled
 */
const { deleteEvent } = require('./gcal-helper');

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
    const { gcalEventId } = JSON.parse(event.body);
    if (!gcalEventId) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: 'Missing gcalEventId' }) };
    }

    await deleteEvent(gcalEventId);

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true }),
    };
  } catch (err) {
    console.error('gcal-delete error:', err);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: err.message }),
    };
  }
};
