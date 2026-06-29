-- Run against business_db if your customers table was created before user_id was added.
--
--   psql -d business_db -f database/business_db/migrations/001_add_customers_user_id.sql

ALTER TABLE customers
ADD COLUMN IF NOT EXISTS user_id UUID;

-- Backfill using the same deterministic UUID pattern as database/business_db/seed.sql
-- (only works if auth_db was seeded with matching deterministic user IDs)
UPDATE customers
SET user_id = ('00000000-0000-4000-8000-' || lpad(id::text, 12, '0'))::uuid
WHERE user_id IS NULL;

ALTER TABLE customers
ALTER COLUMN user_id SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_user_id ON customers(user_id);

-- Demo: order #1 belongs to customer #1 (user1@example.com)
UPDATE orders SET customer_id = 1 WHERE id = 1;

-- After this migration, run:
--   ./scripts/sync-customer-user-ids.sh
-- if auth_db users have random UUIDs (old seed) instead of deterministic IDs.
