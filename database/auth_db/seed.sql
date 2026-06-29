-- Auth database seed (run against auth_db)
-- User IDs use a deterministic pattern so business_db can reference them.

----------------------------------------------------
-- ROLES
----------------------------------------------------

INSERT INTO roles(name)
VALUES
('admin'),
('manager'),
('customer_support'),
('customer')
ON CONFLICT DO NOTHING;

----------------------------------------------------
-- USERS
----------------------------------------------------

INSERT INTO users (id, email, password_hash, full_name, provider)
SELECT
    ('00000000-0000-4000-8000-' || lpad(i::text, 12, '0'))::uuid,
    'user' || i || '@example.com',
    'fake_hash_' || i,
    'User ' || i,
    'local'
FROM generate_series(1, 500) i
ON CONFLICT DO NOTHING;

----------------------------------------------------
-- ADMIN ROLE
----------------------------------------------------

INSERT INTO user_roles(user_id, role_id)
SELECT u.id, r.id
FROM users u
JOIN roles r ON r.name = 'admin'
WHERE u.email = 'user1@example.com'
ON CONFLICT DO NOTHING;

----------------------------------------------------
-- CUSTOMER ROLE
----------------------------------------------------

INSERT INTO user_roles(user_id, role_id)
SELECT u.id, r.id
FROM users u
JOIN roles r ON r.name = 'customer'
ON CONFLICT DO NOTHING;
