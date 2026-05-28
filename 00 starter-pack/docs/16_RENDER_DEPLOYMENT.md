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

```env
SECRET_KEY=
DEBUG=False
DATABASE_URL=
ALLOWED_HOSTS=
CORS_ALLOWED_ORIGINS=
JWT_SECRET=
```

## Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=
```

## Seed Command

After first deployment:

```bash
python manage.py seed_assessment   --questions seed_data/sa-questions-likert.csv   --thresholds seed_data/domain-thresholds.csv   --rules seed_data/rules-bank.csv   --assessment-name "Subjective Alignment Assessment"   --assessment-version "1.0"
```
