CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

CREATE TABLE IF NOT EXISTS users (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email            CITEXT NOT NULL UNIQUE,
  first_name       TEXT,
  last_name        TEXT,
  photo_url        TEXT,
  bounty_balance   INTEGER NOT NULL DEFAULT 0 CHECK (bounty_balance >= 0),
  timezone         TEXT NOT NULL DEFAULT 'UTC',
  email_verified   BOOLEAN NOT NULL DEFAULT FALSE,
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  role             TEXT NOT NULL CHECK (role IN ('admin', 'user')) DEFAULT 'user',
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_login_at    TIMESTAMPTZ,
  signup_ip        INET
);

CREATE TABLE IF NOT EXISTS auth_identities (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id              UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  provider             TEXT NOT NULL CHECK (provider IN ('password','google')),
  provider_user_id     TEXT,
  email                CITEXT NOT NULL,
  password_hash        TEXT,
  password_updated_at  TIMESTAMPTZ,
  password_needs_reset BOOLEAN NOT NULL DEFAULT FALSE,
  meta                 JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, provider)
);

CREATE TABLE IF NOT EXISTS goal_types (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              TEXT NOT NULL,
  description       TEXT,
  verification_type TEXT NOT NULL CHECK (verification_type IN ('photo', 'quiz')),
  question_count    INT DEFAULT NULL,
  gpt_prompt        TEXT,
  meta              JSONB DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS goals (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id              UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  goal_type_id         UUID REFERENCES goal_types(id),
  title                TEXT NOT NULL,
  user_input           TEXT,
  bounty_amount        INTEGER NOT NULL DEFAULT 0 CHECK (bounty_amount >= 0),
  deadline             TIMESTAMPTZ NOT NULL,
  notification_tone    TEXT NOT NULL DEFAULT 'harsh' CHECK (notification_tone IN ('harsh', 'normal', 'soft')),
  status               TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'validating', 'resolved', 'canceled')),
  quiz_question_status TEXT DEFAULT NULL CHECK (quiz_question_status IN ('pending', 'failed', 'created')),
  verification_status  TEXT NOT NULL DEFAULT 'not_started' CHECK (verification_status IN ('not_started', 'completed', 'failed')),
  completed_at         TIMESTAMPTZ,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS verifications (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  goal_id           UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
  type              TEXT NOT NULL CHECK (verification_type IN ('photo', 'quiz')),
  result            TEXT NOT NULL DEFAULT 'pending' CHECK (result IN ('pending', 'completed', 'failed')),
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS verification_photos (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  verification_id UUID NOT NULL UNIQUE REFERENCES verifications(id) ON DELETE CASCADE,
  image_url       TEXT NOT NULL,
  meta            JSONB NOT NULL DEFAULT '{}'::jsonb,
  s3_key          TEXT NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS quiz_questions (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  goal_id    UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
  question   TEXT NOT NULL,
  answer     TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS quiz_responses (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  verification_id UUID NOT NULL REFERENCES verifications(id) ON DELETE CASCADE,
  question_id     UUID NOT NULL REFERENCES quiz_questions(id),
  user_answer     TEXT NOT NULL,
  is_correct      BOOLEAN,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bounty_ledger (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  goal_id    UUID REFERENCES goals(id) ON DELETE SET NULL,
  amount     INTEGER NOT NULL,
  type       TEXT NOT NULL CHECK (type IN ('fund', 'hold', 'release', 'forfeit', 'refund')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bounty_transactions (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount            INTEGER NOT NULL,
  direction         TEXT NOT NULL CHECK (direction IN ('deposit', 'withdrawal')),
  status            TEXT NOT NULL CHECK (status IN ('pending', 'succeeded', 'failed')),
  payment_intent_id TEXT,
  charge_id         TEXT,
  transfer_id       TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS weekly_maintenance_costs (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_start        TIMESTAMPTZ NOT NULL,
  week_end          TIMESTAMPTZ NOT NULL,
  aws_cost_cents    INTEGER NOT NULL DEFAULT 0 CHECK (aws_cost_cents >= 0),
  openai_cost_cents INTEGER NOT NULL DEFAULT 0 CHECK (openai_cost_cents >= 0),
  fee_amount_cents  INTEGER NOT NULL DEFAULT 0 CHECK (fee_amount_cents >= 0),
  source            TEXT NOT NULL DEFAULT 'automated',
  notes             TEXT,
  meta              JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (week_start, week_end)
);

CREATE TABLE IF NOT EXISTS weekly_pool_distributions (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_start              TIMESTAMPTZ NOT NULL,
  week_end                TIMESTAMPTZ NOT NULL,
  failed_pool_cents       INTEGER NOT NULL DEFAULT 0 CHECK (failed_pool_cents >= 0),
  maintenance_fee_cents   INTEGER NOT NULL DEFAULT 0 CHECK (maintenance_fee_cents >= 0),
  net_pool_cents          INTEGER NOT NULL DEFAULT 0 CHECK (net_pool_cents >= 0),
  distributed_total_cents INTEGER NOT NULL DEFAULT 0 CHECK (distributed_total_cents >= 0),
  successful_goals_count  INTEGER NOT NULL DEFAULT 0 CHECK (successful_goals_count >= 0),
  meta                    JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (week_start, week_end)
);

CREATE TABLE IF NOT EXISTS weekly_pool_distribution_items (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  distribution_id UUID NOT NULL REFERENCES weekly_pool_distributions(id) ON DELETE CASCADE,
  goal_id         UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  goal_bounty_cents INTEGER NOT NULL CHECK (goal_bounty_cents > 0),
  payout_cents    INTEGER NOT NULL CHECK (payout_cents >= 0),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (distribution_id, goal_id)
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token      TEXT NOT NULL UNIQUE,
  expires_at TIMESTAMPTZ NOT NULL,
  revoked_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS email_verification_tokens (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token      TEXT NOT NULL UNIQUE,
  expires_at TIMESTAMPTZ NOT NULL,
  used_at    TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_email_verification_tokens_user ON email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id);
CREATE INDEX IF NOT EXISTS idx_verifications_goal_id ON verifications(goal_id);
CREATE INDEX IF NOT EXISTS idx_quiz_questions_goal_id ON quiz_questions(goal_id);
CREATE INDEX IF NOT EXISTS idx_bounty_tx_user_id ON bounty_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_bounty_tx_status ON bounty_transactions(status);
CREATE INDEX IF NOT EXISTS idx_bounty_tx_created_at ON bounty_transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_weekly_maintenance_costs_week_start ON weekly_maintenance_costs(week_start);
CREATE INDEX IF NOT EXISTS idx_weekly_pool_distribution_items_user_id ON weekly_pool_distribution_items(user_id);

COMMIT;


SELECT * FROM goal_types;
INSERT INTO goal_types(name, description, verification_type, gpt_prompt) 
VALUES('Read the Bible', 'User will choose the Bible passage and answer questions regarding the passage', 
'quiz', 'Return the response as JSON. Generate ${count} True/False questions with answers about this bible passage: ${passage}');

INSERT INTO goal_types(name, description, verification_type, gpt_prompt) 
VALUES('Go to the gym', 'User will upload a picture and the app will verify if the picture was taken at the gym', 
'photo', 'You are an image-verification classifier.

Task:
Determine whether the uploaded image was taken in a gym.

Return ONLY valid JSON in this exact schema:
{"is_true": boolean, "prob_true": integer, "prob_false": integer, "reason": string}

Rules:
- prob_true is the estimated probability (0-100) that the image was taken in a gym.
- prob_false must equal 100 - prob_true.
- is_true must be:
  - true if prob_true >= 75
  - false if prob_true < 75
- reason must be a short explanation based only on visible evidence.
- Do not mention anything not visible in the image.
- If evidence is weak/ambiguous (close-up, blurry, dark, cropped, little context), keep prob_true low.

Decision policy:
- Use high prob_true only when clear gym evidence is visible (e.g., weight machines, barbells, squat racks, benches, gym mirrors, rubber flooring, locker-room context).
- If the setting appears to be non-gym or cannot be verified from the image, return lower prob_true.

Consistency requirements:
- reason must agree with is_true and probabilities.
- Output integers only for prob_true/prob_false.
- Output only JSON. No markdown. No extra text.');

INSERT INTO goal_types(name, description, verification_type, gpt_prompt)
VALUES('Go to class', 'User will upload a picture, and the app will verify if the picture was taken in a college class',
'photo', 'You are an image-verification classifier.

Task:
Determine whether the uploaded image was taken in a college classroom.

Return ONLY valid JSON in this exact schema:
{"is_true": boolean, "prob_true": integer, "prob_false": integer, "reason": string}

Rules:
- prob_true is the estimated probability (0-100) that the image was taken in a college classroom.
- prob_false must equal 100 - prob_true.
- is_true must be:
  - true if prob_true >= 75
  - false if prob_true < 75
- reason must be a short explanation based only on visible evidence.
- Do not mention anything not visible in the image.
- If evidence is weak/ambiguous (close-up, blurry, dark, cropped, little context), keep prob_true low.

Decision policy:
- Use high prob_true only when clear classroom evidence is visible (e.g., lecture hall seating, desks, whiteboard/projector, podium, instructor with students in class layout).
- If the setting appears non-classroom or cannot be verified from the image, return lower prob_true.

Consistency requirements:
- reason must agree with is_true and probabilities.
- Output integers only for prob_true/prob_false.
- Output only JSON. No markdown. No extra text.');
COMMIT;
