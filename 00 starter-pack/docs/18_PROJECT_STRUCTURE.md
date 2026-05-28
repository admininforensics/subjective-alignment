# Project Structure

Recommended monorepo:

```text
subjective-alignment/
├── README.md
├── docs/
├── seed_data/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   └── apps/
│       ├── accounts/
│       ├── organisations/
│       ├── licensing/
│       ├── assessments/
│       ├── scoring/
│       ├── rules/
│       ├── results/
│       └── imports/
└── frontend/
    ├── package.json
    ├── app/
    ├── components/
    ├── hooks/
    └── lib/
```

## Build Order

1. Backend project setup
2. Models and migrations
3. Seed importer
4. Scoring service
5. Rule service
6. API endpoints
7. API tests
8. Frontend shell
9. Assessment flow
10. Results dashboard
11. Manager/admin views
12. Render deployment
