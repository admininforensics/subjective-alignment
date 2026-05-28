# API Contracts

Use Django REST Framework.

## Authentication

### POST `/api/auth/login/`

Request:

```json
{
  "email": "person@example.com",
  "password": "password"
}
```

Response:

```json
{
  "access": "...",
  "refresh": "...",
  "user": {
    "id": 1,
    "email": "person@example.com",
    "role": "RESPONDENT",
    "organisation_id": 1
  }
}
```

## Dashboard

### GET `/api/dashboard/`

Respondent response:

```json
{
  "assigned_licence": {
    "id": 1,
    "status": "IN_PROGRESS"
  },
  "session": {
    "id": 1,
    "status": "IN_PROGRESS",
    "progress": 0.42
  },
  "latest_result": null
}
```

## Assessment

### GET `/api/assessment/current/`

Returns the active assessment for the respondent's assigned licence.

### POST `/api/sessions/start/`

Starts a session for the assigned licence.

### GET `/api/sessions/{id}/`

Returns session details, questions, existing responses and progress.

### POST `/api/sessions/{id}/responses/`

Request:

```json
{
  "question_id": 123,
  "raw_likert_score": 4
}
```

Response:

```json
{
  "question_id": 123,
  "raw_likert_score": 4,
  "effective_likert_score": 4,
  "saved": true
}
```

### POST `/api/sessions/{id}/complete/`

Completes and locks the assessment.

Response:

```json
{
  "session_id": 1,
  "status": "COMPLETED",
  "domain_results": [],
  "triggered_flags": []
}
```

## Results

### GET `/api/results/{session_id}/`

Response:

```json
{
  "session": {},
  "domain_results": [
    {
      "domain": "Burnout Risk",
      "score": 280.5,
      "threshold": 267,
      "triggered": true
    }
  ],
  "flags": [
    {
      "flag": "Energy Leak",
      "insight": "You may be draining energy..."
    }
  ]
}
```

## Admin / Organisation

### GET `/api/organisation/respondents/`

### POST `/api/licences/assign/`

Request:

```json
{
  "licence_id": 1,
  "user_id": 5
}
```

### GET `/api/organisation/results/`

Returns result summaries for users visible to the current manager/admin.
