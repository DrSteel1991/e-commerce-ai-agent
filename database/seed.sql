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

INSERT INTO users
(email,password_hash,full_name,provider)

SELECT

'user'||i||'@example.com',

'fake_hash_'||i,

'User '||i,

'local'

FROM generate_series(1,500) i

ON CONFLICT DO NOTHING;

----------------------------------------------------
-- ADMIN ROLE
----------------------------------------------------

INSERT INTO user_roles(user_id,role_id)

SELECT u.id,r.id

FROM users u

JOIN roles r

ON r.name='admin'

WHERE u.email='user1@example.com'

ON CONFLICT DO NOTHING;

----------------------------------------------------
-- CUSTOMER ROLE
----------------------------------------------------

INSERT INTO user_roles(user_id,role_id)

SELECT u.id,r.id

FROM users u

JOIN roles r

ON r.name='customer'

ON CONFLICT DO NOTHING;

----------------------------------------------------
-- CUSTOMERS
----------------------------------------------------

INSERT INTO customers
(user_id,first_name,last_name,email,phone)

SELECT

u.id,

'CustomerFirst'||i,

'CustomerLast'||i,

u.email,

'+9617000'||LPAD(i::text,4,'0')

FROM generate_series(1,500) i

JOIN users u

ON u.email='user'||i||'@example.com'

ON CONFLICT DO NOTHING;

----------------------------------------------------
-- PRODUCTS
----------------------------------------------------

INSERT INTO products
(name,description,price,stock,category)

SELECT

category||' Product '||i,

'Description for product '||i,

ROUND((20+random()*300)::numeric,2),

(random()*200)::int+5,

category

FROM generate_series(1,1000) i

CROSS JOIN LATERAL(

SELECT

CASE floor(random()*8)::int

WHEN 0 THEN 'Shoes'

WHEN 1 THEN 'Electronics'

WHEN 2 THEN 'Sports'

WHEN 3 THEN 'Home'

WHEN 4 THEN 'Beauty'

WHEN 5 THEN 'Clothing'

WHEN 6 THEN 'Accessories'

ELSE 'Toys'

END category

)c;

----------------------------------------------------
-- ORDERS
----------------------------------------------------

INSERT INTO orders
(customer_id,total_price,status,ordered_at)

SELECT

(random()*499)::int+1,

0,

CASE floor(random()*7)::int

WHEN 0 THEN 'Pending'

WHEN 1 THEN 'Processing'

WHEN 2 THEN 'Shipped'

WHEN 3 THEN 'Delivered'

WHEN 4 THEN 'Cancelled'

WHEN 5 THEN 'Refunded'

ELSE 'Returned'

END,

NOW()-(random()*INTERVAL '180 days')

FROM generate_series(1,3000);

----------------------------------------------------
-- ORDER ITEMS
----------------------------------------------------

INSERT INTO order_items
(order_id,product_id,quantity,price)

SELECT

o.id,

(random()*999)::int+1,

(random()*3)::int+1,

ROUND((20+random()*300)::numeric,2)

FROM orders o

CROSS JOIN generate_series(1,4)

WHERE random()<0.7;

----------------------------------------------------
-- UPDATE TOTALS
----------------------------------------------------

UPDATE orders o

SET total_price=sub.total

FROM(

SELECT

order_id,

SUM(quantity*price) total

FROM order_items

GROUP BY order_id

) sub

WHERE sub.order_id=o.id;

----------------------------------------------------
-- DOCUMENTS
----------------------------------------------------

INSERT INTO documents
(filename,document_type)

VALUES

('refund_policy.txt','policy'),

('shipping_policy.txt','policy'),

('return_policy.txt','policy'),

('payment_policy.txt','policy'),

('faq.txt','faq'),

('product_manual.txt','manual');

----------------------------------------------------
-- DOCUMENT CHUNKS
----------------------------------------------------

INSERT INTO document_chunks
(document_id,content)

SELECT

d.id,

chunk

FROM documents d

JOIN LATERAL(

SELECT unnest(ARRAY[

'Customers can request refunds within seven days of delivery.',

'Damaged items must be reported within forty eight hours.',

'Shipping usually takes two to five business days.',

'Refunds are processed within five business days.',

'Orders cannot be cancelled after shipment.',

'Credit cards and cash on delivery are accepted.',

'Products must be returned with original packaging.',

'Warranty duration depends on the supplier.'

]) chunk

)c

ON TRUE;