-- Migrate legacy customers.full_name → first_name / last_name
-- Run: psql -d business_db -f database/business_db/migrations/002_customers_split_full_name.sql

ALTER TABLE customers
    ADD COLUMN IF NOT EXISTS first_name VARCHAR(100),
    ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);

UPDATE customers
SET
    first_name = COALESCE(
        first_name,
        NULLIF(split_part(full_name, ' ', 1), '')
    ),
    last_name = COALESCE(
        last_name,
        NULLIF(
            CASE
                WHEN position(' ' in full_name) > 0
                    THEN substring(full_name from position(' ' in full_name) + 1)
                ELSE ''
            END,
            ''
        )
    )
WHERE full_name IS NOT NULL;

ALTER TABLE customers DROP COLUMN IF EXISTS full_name;
