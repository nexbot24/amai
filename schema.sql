-- Create tables

CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    treatment_name TEXT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    deposit_amount DECIMAL(10,2) NOT NULL,
    stripe_payment_intent_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, confirmed, completed, cancelled
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Set up Row Level Security (RLS)

-- Clients table policies
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

-- Allow anyone to create a client (for the booking form)
CREATE POLICY "Allow anonymous client creation" ON clients
    FOR INSERT WITH CHECK (true);

-- Allow authenticated users to read their own client data
CREATE POLICY "Allow authenticated users to read their own data" ON clients
    FOR SELECT USING (auth.email() = email);

-- Bookings table policies
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- Allow anyone to create a booking (it starts as pending until Stripe confirms)
CREATE POLICY "Allow anonymous booking creation" ON bookings
    FOR INSERT WITH CHECK (true);

-- Allow authenticated users to read their own bookings
CREATE POLICY "Allow authenticated users to read their own bookings" ON bookings
    FOR SELECT USING (
        client_id IN (
            SELECT id FROM clients WHERE email = auth.email()
        )
    );
