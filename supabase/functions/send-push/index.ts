import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.7.1";
import webpush from 'https://esm.sh/web-push@3.6.7';

const publicVapidKey = 'BHUpB_ci9_Q9ZBbhRyguKziRcDwz3YhqxgBg7camsEoyzwOdwYlj-qlyShvLW1QU-wwMTO5MKgjifA7CxAEm76g';
const privateVapidKey = 'yJvGGqhYzDKyGIF61SWi57pnZjblUeCsEladtcHJCJU';

webpush.setVapidDetails(
    'mailto:hello@amai.co.uk',
    publicVapidKey,
    privateVapidKey
);

const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req: Request) => {
    if (req.method === 'OPTIONS') {
        return new Response('ok', { headers: corsHeaders });
    }

    try {
        const supabaseUrl = Deno.env.get('SUPABASE_URL') || '';
        const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || '';
        
        const supabase = createClient(supabaseUrl, supabaseKey);

        const { type, record } = await req.json();
        
        let payload = { title: '', body: '', url: '' };
        let targetSubscriptions: any[] = [];
        
        // Admin subscriptions
        const { data: adminSubs } = await supabase
            .from('push_subscriptions')
            .select('*')
            .eq('role', 'admin');
            
        if (adminSubs) {
            targetSubscriptions = [...adminSubs];
        }

        if (type === 'new_booking') {
            const service = record.treatment_name || 'a treatment';
            const date = record.appointment_date || '';
            const time = record.appointment_time || '';
            
            // Look up client name
            let clientName = 'A client';
            if (record.client_id) {
                const { data: client } = await supabase
                    .from('clients')
                    .select('name')
                    .eq('id', record.client_id)
                    .single();
                if (client) clientName = client.name;
            }
            
            // Format date nicely
            let dateStr = '';
            if (date) {
                try {
                    const d = new Date(date + 'T00:00:00');
                    dateStr = d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' });
                } catch(e) { dateStr = date; }
            }
            
            // Admin notification
            payload = {
                title: '📅 New Booking',
                body: `${clientName} · ${service}${dateStr ? ' · ' + dateStr : ''}${time ? ' at ' + time : ''}`,
                url: 'https://amailondon.co.uk/ipad/index.html'
            };
            
            if (record.client_id) {
                const { data: clientSubs } = await supabase
                    .from('push_subscriptions')
                    .select('*')
                    .eq('client_id', record.client_id);
                
                if (clientSubs) {
                    targetSubscriptions = [...targetSubscriptions, ...clientSubs.map(s => ({
                        ...s,
                        isClient: true,
                        clientPayload: {
                            title: '✓ Booking Confirmed',
                            body: `${service}${dateStr ? ' · ' + dateStr : ''}${time ? ' at ' + time : ''}`,
                            url: 'https://amailondon.co.uk/hub.html'
                        }
                    }))];
                }
            }
        } else if (type === 'new_request') {
            const name = record.name || 'Someone';
            payload = {
                title: '💬 New Enquiry',
                body: `${name} sent a message`,
                url: 'https://amailondon.co.uk/ipad/index.html'
            };
        } else {
            return new Response(JSON.stringify({ error: 'Unknown type' }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' },
                status: 400
            });
        }

        const results = await Promise.allSettled(
            targetSubscriptions.map(async (sub) => {
                const pushSubscription = {
                    endpoint: sub.endpoint,
                    keys: sub.keys
                };
                
                const currentPayload = sub.isClient && sub.clientPayload
                    ? sub.clientPayload
                    : payload;

                try {
                    await webpush.sendNotification(pushSubscription, JSON.stringify(currentPayload));
                    return { success: true, endpoint: sub.endpoint };
                } catch (error: any) {
                    if (error.statusCode === 404 || error.statusCode === 410) {
                        await supabase
                            .from('push_subscriptions')
                            .delete()
                            .eq('endpoint', sub.endpoint);
                    }
                    return { success: false, endpoint: sub.endpoint, error: error.message };
                }
            })
        );

        return new Response(JSON.stringify({ results }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 200,
        });

    } catch (error: any) {
        return new Response(JSON.stringify({ error: error.message }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 500,
        });
    }
});
