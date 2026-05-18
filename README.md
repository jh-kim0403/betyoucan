# BetYouCan

BetYouCan is a goal-accountability app for people who struggle to keep the
promises they make to themselves. You put **real money on the line** behind a
goal. If you follow through and verify it, you keep your bounty and earn a share
of the pot from people who failed the same type of goal. If you fail, your
bounty is redistributed to the users who created and successfully verified that
goal type.

> **Project status:** No longer in active development. The app was rejected
> under App Store policy (real-money "betting" / wagering mechanics), which
> blocked publishing. The code remains here as a reference and portfolio
> project.

## How it works

1. **Add a goal** — pick a goal type, a deadline, a notification tone, and how
   much bounty you want to wager on it.
2. **Verify before the deadline** — each goal type has its own verification:
   - **Read the Bible** — choose a book and chapter range, then answer an
     auto-generated true/false quiz about the passage.
   - **Go to the gym** — upload a photo; the app verifies it was taken at a gym.
   - **Go to class** — upload a photo; the app verifies it was taken in a
     college class.
3. **Settlement** — a weekly job sweeps overdue goals, deducts a small
   maintenance cost, and redistributes failed bounties to users who succeeded at
   the same goal type. Funds are added via Stripe ("Purchase Bounty") and can be
   withdrawn.

### Screens

<table>
  <tr>
    <td align="center"><img src="docs/screenshots/home.PNG" width="220" alt="Home"><br><sub>Home — goals &amp; bounty</sub></td>
    <td align="center"><img src="docs/screenshots/add-new-goal.PNG" width="220" alt="Add New Goal"><br><sub>Add New Goal</sub></td>
    <td align="center"><img src="docs/screenshots/verification-quiz.PNG" width="220" alt="Verification quiz"><br><sub>Verification (quiz)</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/past-goals.PNG" width="220" alt="Past Goals"><br><sub>Past Goals</sub></td>
    <td align="center"><img src="docs/screenshots/purchase-bounty.PNG" width="220" alt="Purchase Bounty"><br><sub>Purchase Bounty</sub></td>
    <td align="center"><img src="docs/screenshots/payment-success.PNG" width="220" alt="Payment success"><br><sub>Payment success (Stripe)</sub></td>
  </tr>
</table>

## Architecture

| Component | Stack |
|-----------|-------|
| `BetYouCan_FE` | React Native + Expo (TypeScript), Google Sign-In, Stripe React Native, Expo SecureStore for token storage |
| `BetYouCan_BE` | FastAPI, SQLAlchemy, PostgreSQL, Celery, OpenAI (quiz generation / photo evaluation), Stripe, AWS S3 + SES |
| Async work | Celery worker + Celery beat. **RabbitMQ** is the Celery broker; PostgreSQL is the result backend; **Redis** backs SlowAPI rate limiting |

Scheduled Celery jobs:

- Sweep overdue goals — every minute
- Clean up abandoned photo verifications — hourly
- Weekly maintenance cost + bounty distribution — Mondays 00:05 UTC

---

## Getting started

### Prerequisites

- Python 3.13+ and [Poetry](https://python-poetry.org/)
- Node.js 20+ and the [Expo CLI](https://docs.expo.dev/)
- PostgreSQL
- Redis (SlowAPI rate limiting)
- RabbitMQ (Celery broker)
- API credentials: OpenAI, Stripe, AWS (S3 + SES), Google OAuth client

### Clone

```bash
git clone <repo-url> BetYouCan
cd BetYouCan
```

### Backend (`BetYouCan_BE`)

```bash
cd BetYouCan_BE
poetry install
```

Create an environment file. The app loads `.env.<ENVIRONMENT>` (default
`ENVIRONMENT=dev`, so `.env.dev`). Required variables:

```bash
# .env.dev

SECRET_KEY=your-jwt-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

GOOGLE_CLIENT_ID_WEB=...
GOOGLE_CLIENT_SECRET_WEB=...

OPENAI_API_KEY=...
# Optional admin/cost-reporting keys
OPENAI_ADMIN_API_KEY=
OPENAI_ORG_ID=
SERP_API_KEY=

# Celery broker (RabbitMQ) and SlowAPI rate-limit store (Redis)
RABBITMQ_URL=amqp://guest:guest@localhost:5672//
SLOWAPI_REDIS_URL=redis://localhost:6379/0

AWS_REGION=us-east-1
S3_BUCKET=your-bucket
AWS_ACCESS_KEY=...
AWS_SECRET_KEY=...

STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

SES_ACCESS_KEY=...
SES_SECRET_KEY=...
SENDER_EMAIL=you@example.com

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=betyoucan
```

Create the database and load the schema:

```bash
createdb betyoucan
psql -d betyoucan -f sql/table_creation.sql
```

Start Redis and RabbitMQ (examples):

```bash
# Redis
redis-server
# or: brew services start redis  /  sudo systemctl start redis

# RabbitMQ
sudo systemctl start rabbitmq-server
# or: brew services start rabbitmq
```

Run the API server:

```bash
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

In separate terminals, run the Celery worker and the beat scheduler:

```bash
# Worker
poetry run celery -A src.celery_app.celery_app worker --loglevel=info

# Beat (periodic tasks: deadline sweep, cleanup, weekly distribution)
poetry run celery -A src.celery_app.celery_app beat --loglevel=info
```

API docs are then available at `http://localhost:8000/docs`.

### Frontend (`BetYouCan_FE`)

```bash
cd BetYouCan_FE
npm install
```

Set the API base URL via an Expo public env var (e.g. in `.env` or your shell):

```bash
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000
```

Start the app (pick an environment):

```bash
npm run start:dev      # or start:test / start:prod
# then press i (iOS) or a (Android), or scan the QR with Expo Go / a dev client
```

Run directly on a device/simulator:

```bash
npm run ios
npm run android
```

### Tests

```bash
# Backend
cd BetYouCan_BE && poetry run pytest

# Frontend
cd BetYouCan_FE && npm test
```

## Repository layout

```
BetYouCan/
├── BetYouCan_BE/      FastAPI backend + Celery tasks
│   ├── src/routes/    auth, goals, verifications, payments, user
│   ├── src/tasks/     deadline sweep, distribution, evaluations, quiz, cleanup
│   ├── src/gpt/       OpenAI calls (quiz generation, photo evaluation)
│   └── sql/           schema (table_creation.sql)
├── BetYouCan_FE/      React Native + Expo app
│   └── src/screens/   Home, AddNewGoal, Verification, PastGoals, PurchaseBounty…
└── DreamStudio_BE/    Earlier scaffold the backend evolved from
```
