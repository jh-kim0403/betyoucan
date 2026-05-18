BEGIN;
END;

----------------------------
-- Extensions
----------------------------
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS citext;    -- case-insensitive email


----------------------------
-- Helper Functions
----------------------------

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


---------------------------------------
-- Add later --

-- ---------- Email verification (manual signup flow) ----------
CREATE TABLE IF NOT EXISTS email_verifications (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token        TEXT NOT NULL UNIQUE,   -- random, single-use
  sent_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at   TIMESTAMPTZ NOT NULL,
  consumed_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_email_verifications_user ON email_verifications(user_id);

-- ---------- Password reset (manual signup flow) ----------
CREATE TABLE IF NOT EXISTS password_resets (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token        TEXT NOT NULL UNIQUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at   TIMESTAMPTZ NOT NULL,
  used_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_password_resets_user ON password_resets(user_id);


CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    token_hash TEXT NOT NULL UNIQUE,

    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS auth_identities CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS goals CASCADE;
DROP TABLE IF EXISTS goal_types CASCADE;
DROP TABLE IF EXISTS email_verifications CASCADE;
DROP TABLE IF EXISTS password_resets CASCADE;
DROP TABLE IF EXISTS goal_quiz_questions;
DROP TABLE IF EXISTS goal_quiz_user_input;
select * from users