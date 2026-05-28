# Cursor Master Prompt

Use this prompt as the first instruction in Cursor.

---

You are building a full-stack assessment platform called Subjective Alignment.

Read every markdown file in the `/docs` folder before coding.

Build the project using:

- Django 5
- Django REST Framework
- PostgreSQL
- SimpleJWT authentication
- Next.js 15 App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- Recharts

The application must be data-driven. Do not hardcode questions, domains, thresholds, flags or insights into application logic. These must be seeded from the CSV files in `/seed_data`.

First build the backend and database models. Then build the CSV import management command. Then build the scoring engine and rule engine. Then expose DRF APIs. Finally build the frontend dashboard, assessment flow and results screens.

Important business rules:

1. Organisations buy licences.
2. Respondents are assigned licences.
3. A respondent can pause and resume an assessment.
4. A respondent may complete the assessment once per assigned licence.
5. Managers and administrators can view respondent results according to role permissions.
6. A domain is triggered when its final weighted score is greater than or equal to its threshold.
7. A rule is triggered if and only if both domains in the rule are triggered.
8. Store raw responses permanently for auditability.
9. Store computed domain scores and triggered flags at completion time.
10. Make imports idempotent.

Implement in small, testable steps. Create tests for import logic, scoring logic, rule logic and API permissions.
