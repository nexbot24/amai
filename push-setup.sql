CREATE TABLE IF NOT EXISTS public.push_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role TEXT NOT NULL,
    client_id UUID REFERENCES public.clients(id) ON DELETE CASCADE,
    endpoint TEXT UNIQUE NOT NULL,
    keys JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.push_subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anon insert" ON public.push_subscriptions FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "Allow anon select" ON public.push_subscriptions FOR SELECT TO anon USING (true);
CREATE POLICY "Allow anon update" ON public.push_subscriptions FOR UPDATE TO anon USING (true);

-- Trigger for new bookings
CREATE OR REPLACE FUNCTION notify_new_booking() RETURNS TRIGGER AS $$
DECLARE
    request_body JSON;
BEGIN
    request_body := json_build_object(
        'type', 'new_booking',
        'record', row_to_json(NEW)
    );
    
    PERFORM net.http_post(
        url := 'https://tphyrmweauzfletdlqvi.supabase.co/functions/v1/send-push',
        headers := jsonb_build_object(
            'Content-Type', 'application/json',
            'Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwaHlybXdlYXV6ZmxldGRscXZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc0NTIxOTQsImV4cCI6MjEwMzAyODE5NH0.Z_utKsxYquCoL2LfTjjL8QFB1tnLJZW9j3El7Sykk8o'
        ),
        body := request_body::jsonb
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_new_booking ON public.bookings;
CREATE TRIGGER trigger_new_booking
    AFTER INSERT ON public.bookings
    FOR EACH ROW EXECUTE FUNCTION notify_new_booking();

-- Trigger for new requests
CREATE OR REPLACE FUNCTION notify_new_request() RETURNS TRIGGER AS $$
DECLARE
    request_body JSON;
BEGIN
    request_body := json_build_object(
        'type', 'new_request',
        'record', row_to_json(NEW)
    );
    
    PERFORM net.http_post(
        url := 'https://tphyrmweauzfletdlqvi.supabase.co/functions/v1/send-push',
        headers := jsonb_build_object(
            'Content-Type', 'application/json',
            'Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwaHlybXdlYXV6ZmxldGRscXZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc0NTIxOTQsImV4cCI6MjEwMzAyODE5NH0.Z_utKsxYquCoL2LfTjjL8QFB1tnLJZW9j3El7Sykk8o'
        ),
        body := request_body::jsonb
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_new_request ON public.requests;
CREATE TRIGGER trigger_new_request
    AFTER INSERT ON public.requests
    FOR EACH ROW EXECUTE FUNCTION notify_new_request();
