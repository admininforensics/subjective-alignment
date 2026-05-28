# Backend Architecture

Recommended Django app structure:

```text
backend/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/
│   ├── organisations/
│   ├── licensing/
│   ├── assessments/
│   ├── scoring/
│   ├── rules/
│   ├── results/
│   └── imports/
└── seed_data/
```

## Service Layer

Business logic should not live in views.

Use:

```text
apps/scoring/services.py
apps/rules/services.py
apps/imports/services.py
apps/licensing/services.py
```

## Backend Principles

- Models define persistence.
- Serializers define API shape.
- Services define business logic.
- Views should be thin.
- Permissions must be enforced on every endpoint.
- Scoring must be deterministic and testable.
