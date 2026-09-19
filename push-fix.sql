-- Fix: Make triggers fail gracefully so bookings ALWAYS go through
-- even if push notifications fail

CREATE OR REPLACE FUNCTION notify_new_booking() RETURNS TRIGGER AS $$
BEGIN
    BEGIN
        PERFORM net.http_post(
            url := 'https://tphyrmweauzfletdlqvi.supabase.co/functions/v1/send-push',
            headers := jsonb_build_object(
                'Content-Type', 'application/json',
                'Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwaHlybXdlYXV6ZmxldGRscXZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc0NTIxOTQsImV4cCI6MjEwMzAyODE5NH0.Z_utKsxYquCoL2LfTjjL8QFB1tnLJZW9j3El7Sykk8o'
            ),
            body := jsonb_build_object(
                'type', 'new_booking',
                'record', row_to_json(NEW)
            )
        );
    EXCEPTION WHEN OTHERS THEN
        RAISE LOG 'Push notification failed for booking %: %', NEW.id, SQLERRM;
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION notify_new_request() RETURNS TRIGGER AS $$
BEGIN
    BEGIN
        PERFORM net.http_post(
            url := 'https://tphyrmweauzfletdlqvi.supabase.co/functions/v1/send-push',
            headers := jsonb_build_object(
                'Content-Type', 'application/json',
                'Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwaHlybXdlYXV6ZmxldGRscXZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc0NTIxOTQsImV4cCI6MjEwMzAyODE5NH0.Z_utKsxYquCoL2LfTjjL8QFB1tnLJZW9j3El7Sykk8o'
            ),
            body := jsonb_build_object(
                'type', 'new_request',
                'record', row_to_json(NEW)
            )
        );
    EXCEPTION WHEN OTHERS THEN
        RAISE LOG 'Push notification failed for request %: %', NEW.id, SQLERRM;
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
