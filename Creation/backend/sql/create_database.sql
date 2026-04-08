DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'demo4_auth') THEN
        CREATE DATABASE demo4_auth;
    END IF;
END
$$;
