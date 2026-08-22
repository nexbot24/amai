const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    const { treatmentName, appointmentDate, appointmentTime, price, depositAmount, clientEmail, clientName, clientPhone } = JSON.parse(event.body);

    // 1. Create or get client in Supabase
    let { data: client } = await supabase
      .from('clients')
      .select('id')
      .eq('email', clientEmail)
      .single();

    if (!client) {
      const { data: newClient, error: insertError } = await supabase
        .from('clients')
        .insert([{ email: clientEmail, name: clientName, phone: clientPhone }])
        .select()
        .single();
      
      if (insertError) throw insertError;
      client = newClient;
    }

    // 2. Create Stripe PaymentIntent for the deposit
    const paymentIntent = await stripe.paymentIntents.create({
      amount: Math.round(depositAmount * 100), // Stripe expects cents
      currency: 'gbp',
      receipt_email: clientEmail,
      metadata: {
        treatmentName,
        appointmentDate,
        appointmentTime,
        clientId: client.id
      },
      // In a real scenario, you might want to use automatic_payment_methods
      automatic_payment_methods: {
        enabled: true,
      },
    });

    // 3. Create a pending booking in Supabase
    const { data: booking, error: bookingError } = await supabase
      .from('bookings')
      .insert([{
        client_id: client.id,
        treatment_name: treatmentName,
        appointment_date: appointmentDate,
        appointment_time: appointmentTime,
        price,
        deposit_amount: depositAmount,
        stripe_payment_intent_id: paymentIntent.id,
        status: 'pending'
      }])
      .select()
      .single();

    if (bookingError) throw bookingError;

    return {
      statusCode: 200,
      body: JSON.stringify({
        clientSecret: paymentIntent.client_secret,
        bookingId: booking.id
      }),
    };
  } catch (error) {
    console.error('Error creating payment intent:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};
