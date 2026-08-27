-- ============================================================
-- PHASE 1: PROMOS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS promos (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('%', '£')),
    value NUMERIC NOT NULL DEFAULT 0,
    note TEXT DEFAULT '',
    uses INTEGER DEFAULT 0,
    cap INTEGER DEFAULT 0,
    until DATE,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE promos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read promos" ON promos FOR SELECT USING (true);
CREATE POLICY "Public insert promos" ON promos FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update promos" ON promos FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "Public delete promos" ON promos FOR DELETE USING (true);

-- ============================================================
-- PHASE 2: ADD MISSING COLUMNS TO CLIENTS
-- ============================================================
ALTER TABLE clients ADD COLUMN IF NOT EXISTS phone TEXT;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS visits INTEGER DEFAULT 0;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS spend NUMERIC DEFAULT 0;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS plan TEXT;

-- ============================================================
-- PHASE 3: ADD MISSING COLUMNS TO BOOKINGS
-- ============================================================
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS promo_code TEXT;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS discount_amount NUMERIC DEFAULT 0;

-- ============================================================
-- PHASE 4: CLEAR ALL DUMMY / TEST DATA
-- ============================================================
DELETE FROM chat_messages;
DELETE FROM conversations;
DELETE FROM bookings;
DELETE FROM clients;
