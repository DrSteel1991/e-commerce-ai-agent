-- RAG database seed (run against rag_db)
-- Vector chunks are created by knowledge_seeder, not SQL.

INSERT INTO documents (filename, document_type)
VALUES
    ('refund_policy.pdf', 'policy'),
    ('shipping_policy.pdf', 'policy'),
    ('payment_policy.pdf', 'policy'),
    ('warranty_policy.pdf', 'policy'),
    ('faq.pdf', 'faq');

-- After seeding metadata, run:
--   cd backend/rag-service
--   python -m app.seeders.knowledge_seeder
