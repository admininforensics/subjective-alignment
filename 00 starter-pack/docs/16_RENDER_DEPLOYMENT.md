# Render Deployment

## Services

Use Render for:

- PostgreSQL database
- Django API web service
- Next.js frontend static/web service

## Backend Build Command

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

## Backend Start Command

```bash
gunicorn config.wsgi:application
```

## Backend Environment Variables

Set these on the **backend** service (not the frontend). In `render.yaml` they live under `subjective-alignment-backend` → `envVars`.

```env
SECRET_KEY=
DEBUG=False
DATABASE_URL=
ALLOWED_HOSTS=.onrender.com
FRONTEND_URL=https://subjective-alignment-frontend.onrender.com
CORS_ALLOWED_ORIGINS=https://subjective-alignment-frontend.onrender.com
CSRF_TRUSTED_ORIGINS=https://subjective-alignment-frontend.onrender.com
```

`CORS_ALLOWED_ORIGINS` must be the full frontend origin (scheme + host, no trailing slash). Comma-separate multiple origins if needed.

## Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=
```

## Seed Command

After first deployment:

```bash
python manage.py seed_assessment   --questions seed_data/sa-questions-likert.csv   --thresholds seed_data/domain-thresholds.csv   --rules seed_data/rules-bank.csv   --assessment-name "Subjective Alignment Assessment"   --assessment-version "1.0"
```
