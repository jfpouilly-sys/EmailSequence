-- Seed default admin user
-- Password: Admin123! (BCrypt hash)

INSERT INTO users (username, email, password_hash, role, is_active)
VALUES ('admin', 'admin@company.com',
        '$2a$11$rBNdGDmjXGPqXcH7JhHxPeZVzYw7aBhqF7YHQz.gE7gEz8QzEkMmK',
        'Admin', true);

-- Note: The default password is Admin123!
-- IMPORTANT: Change this password immediately after first login for security reasons
