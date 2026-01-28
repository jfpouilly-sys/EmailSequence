-- Create Lead Generator Database
-- Run this script as postgres superuser

CREATE DATABASE leadgenerator
    WITH ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8';

-- Create user
CREATE USER leadgen_user WITH PASSWORD 'ChangeThisPassword123!';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE leadgenerator TO leadgen_user;

-- Connect to the database
\c leadgenerator

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO leadgen_user;
