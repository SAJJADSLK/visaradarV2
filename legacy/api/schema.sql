-- schema.sql
-- Run with: wrangler d1 execute visaradar24-db --file=api/schema.sql

-- Visa rules table (seeded from visa-rules.json)
CREATE TABLE IF NOT EXISTS visa_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_country TEXT NOT NULL,
  to_country TEXT NOT NULL,
  requirement TEXT NOT NULL CHECK(requirement IN ('visa_free','visa_on_arrival','esta','visa_required')),
  max_stay INTEGER,
  notes TEXT,
  updated TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(from_country, to_country)
);

CREATE INDEX IF NOT EXISTS idx_visa_from ON visa_rules(from_country);
CREATE INDEX IF NOT EXISTS idx_visa_to ON visa_rules(to_country);

-- Email alert subscribers
CREATE TABLE IF NOT EXISTS subscribers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  countries TEXT,
  active INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_sub_email ON subscribers(email);

-- Contact form messages
CREATE TABLE IF NOT EXISTS contact_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  email TEXT NOT NULL,
  subject TEXT,
  message TEXT NOT NULL,
  read INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Policy change log (populated by alert monitor)
CREATE TABLE IF NOT EXISTS policy_changes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  country_code TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  change_type TEXT DEFAULT 'update' CHECK(change_type IN ('new','warn','red','gray','update')),
  source_url TEXT,
  published_at TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_policy_country ON policy_changes(country_code);
CREATE INDEX IF NOT EXISTS idx_policy_date ON policy_changes(published_at);

-- Seed visa rules from JSON
-- Run separately: wrangler d1 execute visaradar24-db --file=api/seed.sql
