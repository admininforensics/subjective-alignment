# Subjective Alignment — User Manual

This repo contains:

- `backend/` — Django 5 + DRF API (SimpleJWT)
- `frontend/` — Next.js App Router UI
- `seed_data/` — CSV source of truth for questions/domains/rules (do not hardcode these)

## Backend: setup + run

### 1) Create venv and install dependencies

From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r backend/requirements.txt
```

### 2) Configure environment variables

Backend reads `backend/.env` (optional for local dev).

Create `backend/.env`:

```bash
cat > backend/.env <<'EOF'
# Local dev defaults are OK for most values.
DEBUG=True
SECRET_KEY=dev-insecure-secret-key

# For Postgres (recommended):
# DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DBNAME

# For CORS when running frontend on a different origin:
# CORS_ALLOWED_ORIGINS=http://localhost:3000
EOF
```

### 3) Migrate the database

```bash
cd backend
source ../.venv/bin/activate
python manage.py migrate
```

### 4) Seed the assessment data (idempotent)

Runs safely multiple times; updates/creates as needed.

**Quick command (uses `/data` CSVs):**

```bash
cd backend
source ../.venv/bin/activate
python manage.py seed_default_assessment
```

**Explicit paths:**

```bash
cd backend
source ../.venv/bin/activate
python manage.py seed_assessment \
  --questions ../data/sa-questions-likert.csv \
  --thresholds ../data/domain-thresholds.csv \
  --rules ../data/rules-bank.csv \
  --assessment-name "Subjective Alignment Assessment" \
  --assessment-version "1.0"
```

**Render:** the backend runs `seed_default_assessment` automatically on each deploy (after migrations).

### 5) Run the API server

```bash
cd backend
source ../.venv/bin/activate
python manage.py runserver 8000
```

API base URL: `http://localhost:8000/api`

## Frontend: setup + run

### 1) Install dependencies

```bash
cd frontend
npm install
```

### 2) Set API URL

Create `frontend/.env.local`:

```bash
cat > frontend/.env.local <<'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api
EOF
```

### 3) Run the frontend

```bash
cd frontend
npm run dev
```

Frontend URL: `http://localhost:3000`

## Login background image

Place your login screen artwork here:

```text
frontend/public/images/login-background.jpg
```

(PNG or WebP also work: name the file `login-background.png` or `login-background.webp` and update the path in `AuthLayout` if needed.)

See `frontend/public/images/README.md` for details. Refresh the browser after adding the file.

## Creating users / organisations / licences

### Create a Django superuser (admin UI)

```bash
cd backend
source ../.venv/bin/activate
python manage.py createsuperuser
```

Admin UI: `http://localhost:8000/admin/`

### Create an organisation + users (shell)

```bash
cd backend
source ../.venv/bin/activate
python manage.py shell
```

In the shell:

```python
from apps.organisations.models import Organisation
from apps.accounts.models import User, UserRole

org = Organisation.objects.create(name="Example Org")

org_admin = User.objects.create_user(
    email="admin@example.com",
    username="admin",
    password="password",
    organisation=org,
    role=UserRole.ORG_ADMIN,
)

respondent = User.objects.create_user(
    email="respondent@example.com",
    username="respondent",
    password="password",
    organisation=org,
    role=UserRole.RESPONDENT,
)

manager = User.objects.create_user(
    email="manager@example.com",
    username="manager",
    password="password",
    organisation=org,
    role=UserRole.MANAGER,
)
```

### (Optional) Assign a manager to a respondent (shell)

```python
from apps.accounts.models import ManagerAssignment
ManagerAssignment.objects.create(manager=manager, respondent=respondent)
```

### Create a licence for a respondent (shell)

```python
from apps.assessments.models import Assessment
from apps.licensing.models import Licence

assessment = Assessment.objects.get(name="Subjective Alignment Assessment", version="1.0")

licence = Licence.objects.create(
    organisation=org,
    assessment=assessment,
)
```

### Assign licence to respondent (API)

1) Login as an org admin (get JWT)
2) Call `POST /api/licences/assign/` with:

```json
{ "licence_id": 1, "user_id": 5 }
```

## Common maintenance commands

### Re-run imports after updating seed CSVs

```bash
cd backend
source ../.venv/bin/activate
python manage.py seed_assessment \
  --questions ../seed_data/sa-questions-likert.csv \
  --thresholds ../seed_data/domain-thresholds.csv \
  --rules ../seed_data/rules-bank.csv \
  --assessment-name "Subjective Alignment Assessment" \
  --assessment-version "1.0"
```

### Run backend tests

```bash
cd backend
source ../.venv/bin/activate
python manage.py test
```

### Run frontend lint/build

```bash
cd frontend
npm run lint
npm run build
```

