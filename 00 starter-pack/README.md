# Subjective Alignment — Cursor Handoff Pack

This folder is the final Cursor-ready specification pack for building the Subjective Alignment assessment platform.

## What to do in Cursor

1. Create a new repository/project.
2. Copy this entire folder into the project root.
3. Open the project in Cursor.
4. Start with: `docs/00_CURSOR_MASTER_PROMPT.md`.
5. Ask Cursor to build the backend first, then the CSV import pipeline, then the scoring/rule engine, then the frontend.

## Included

```text
docs/
seed_data/
```

The `seed_data` folder includes the three source CSVs:

- `sa-questions-likert.csv`
- `domain-thresholds.csv`
- `rules-bank.csv`

## Architecture Decision

Recommended stack:

- Django 5
- Django REST Framework
- PostgreSQL
- SimpleJWT
- Next.js 15 App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- Recharts
- Render hosting

## Business Decisions Captured

- Licensing model: organisation buys licences for respondents.
- Users may pause and resume assessments.
- A respondent may complete the assessment once per assigned licence.
- Results visible to respondent, manager and administrator, subject to role permissions.
- A flag triggers if and only if both domains in a rule are above threshold.
