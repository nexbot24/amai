-- ============================================================
-- INBOX / MESSAGING TABLES
-- ============================================================

-- 1. CONVERSATIONS — one per client
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    client_phone TEXT,
    client_name TEXT,
    last_message_at TIMESTAMPTZ DEFAULT now(),
    last_message_preview TEXT DEFAULT '',
    last_sender TEXT DEFAULT 'client',
    admin_unread INTEGER DEFAULT 0,
    client_unread INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_conv_client ON conversations(client_id);
CREATE INDEX IF NOT EXISTS idx_conv_phone ON conversations(client_phone);
CREATE INDEX IF NOT EXISTS idx_conv_last ON conversations(last_message_at DESC);

ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read conversations" ON conversations FOR SELECT USING (true);
CREATE POLICY "Public insert conversations" ON conversations FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update conversations" ON conversations FOR UPDATE USING (true) WITH CHECK (true);

-- 2. CHAT MESSAGES — individual messages in a conversation
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    sender TEXT NOT NULL CHECK (sender IN ('client', 'studio')),
    body TEXT NOT NULL,
    seen BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_msg_conv ON chat_messages(conversation_id, created_at);

ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read messages" ON chat_messages FOR SELECT USING (true);
CREATE POLICY "Public insert messages" ON chat_messages FOR INSERT WITH CHECK (true);
CREATE POLICY "Public update messages" ON chat_messages FOR UPDATE USING (true) WITH CHECK (true);

-- 3. AUTO-UPDATE conversation on new message
CREATE OR REPLACE FUNCTION update_conversation_on_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations SET
        last_message_at = NEW.created_at,
        last_message_preview = LEFT(NEW.body, 100),
        last_sender = NEW.sender,
        admin_unread = CASE WHEN NEW.sender = 'client' THEN admin_unread + 1 ELSE admin_unread END,
        client_unread = CASE WHEN NEW.sender = 'studio' THEN client_unread + 1 ELSE client_unread END
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_msg_update_conv
AFTER INSERT ON chat_messages
FOR EACH ROW EXECUTE FUNCTION update_conversation_on_message();

-- 4. ENABLE REALTIME on chat_messages for instant delivery
ALTER PUBLICATION supabase_realtime ADD TABLE chat_messages;
ALTER PUBLICATION supabase_realtime ADD TABLE conversations;
