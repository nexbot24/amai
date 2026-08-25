-- ============================================================
-- AMAI Database Migration: Full Integration
-- Run this in Supabase SQL Editor (Dashboard → SQL Editor → New Query)
-- ============================================================

-- 1. SERVICES TABLE — Single source of truth for treatments & prices
-- ============================================================
CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    available BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- RLS: Anyone can read services (needed for booking forms & price pages)
ALTER TABLE services ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read services" ON services FOR SELECT USING (true);


-- 2. SEED THE 11 SERVICES
-- ============================================================
INSERT INTO services (name, category, duration_minutes, price, sort_order) VALUES
    ('First visit — consultation & treatment', 'Waxing', 60, 30.00, 1),
    ('Full leg wax', 'Waxing', 45, 38.00, 2),
    ('Half leg wax', 'Waxing', 30, 26.00, 3),
    ('Underarm wax', 'Waxing', 15, 14.00, 4),
    ('Arm wax', 'Waxing', 25, 22.00, 5),
    ('Facial waxing', 'Waxing', 15, 12.00, 6),
    ('Brow shape & tidy', 'Waxing', 20, 16.00, 7),
    ('Bikini wax', 'Intimate Care', 30, 28.00, 8),
    ('Brazilian wax', 'Intimate Care', 40, 36.00, 9),
    ('Hollywood wax', 'Intimate Care', 45, 42.00, 10),
    ('Maintenance visit', 'Intimate Care', 30, 24.00, 11)
ON CONFLICT (name) DO NOTHING;


-- 3. REQUESTS TABLE — Contact form enquiries → Admin inbox
-- ============================================================
CREATE TABLE IF NOT EXISTS requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    service_name TEXT,
    message TEXT,
    preferred_time TEXT,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE requests ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public insert requests" ON requests FOR INSERT WITH CHECK (true);
CREATE POLICY "Authenticated read requests" ON requests FOR SELECT USING (true);
CREATE POLICY "Authenticated update requests" ON requests FOR UPDATE USING (true);


-- 4. ADD COLUMNS TO EXISTING clients TABLE
-- ============================================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='clients' AND column_name='notes') THEN
        ALTER TABLE clients ADD COLUMN notes TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='clients' AND column_name='preferences') THEN
        ALTER TABLE clients ADD COLUMN preferences JSONB DEFAULT '{}';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='clients' AND column_name='stamps') THEN
        ALTER TABLE clients ADD COLUMN stamps INTEGER DEFAULT 0;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='clients' AND column_name='plan') THEN
        ALTER TABLE clients ADD COLUMN plan TEXT;
    END IF;
END $$;


-- 5. ADD COLUMNS TO EXISTING bookings TABLE
-- ============================================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='bookings' AND column_name='admin_notes') THEN
        ALTER TABLE bookings ADD COLUMN admin_notes TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='bookings' AND column_name='completed_at') THEN
        ALTER TABLE bookings ADD COLUMN completed_at TIMESTAMPTZ;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='bookings' AND column_name='duration_minutes') THEN
        ALTER TABLE bookings ADD COLUMN duration_minutes INTEGER;
    END IF;
END $$;


-- 6. ADD MISSING RLS POLICIES FOR bookings
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public read booking availability') THEN
        CREATE POLICY "Public read booking availability" ON bookings
            FOR SELECT USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Public update bookings') THEN
        CREATE POLICY "Public update bookings" ON bookings
            FOR UPDATE USING (true);
    END IF;
END $$;


-- 7. CLOSED_DAYS TABLE — Studio closure management
-- ============================================================
CREATE TABLE IF NOT EXISTS closed_days (
    date_key TEXT PRIMARY KEY,
    reason TEXT DEFAULT 'Closed',
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE closed_days ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read closed_days" ON closed_days FOR SELECT USING (true);
CREATE POLICY "Admin insert closed_days" ON closed_days FOR INSERT WITH CHECK (true);
CREATE POLICY "Admin delete closed_days" ON closed_days FOR DELETE USING (true);


-- ============================================================
-- DONE. Verify by running:
--   SELECT * FROM services ORDER BY sort_order;
--   SELECT column_name FROM information_schema.columns WHERE table_name='clients';
--   SELECT column_name FROM information_schema.columns WHERE table_name='bookings';
-- ============================================================
