# Page Specifications

## Login Page

Path:

```text
/login
```

Features:

- Email/password form
- Error handling
- Redirect to dashboard after login

## Dashboard

Path:

```text
/dashboard
```

Respondent cards:

- Assigned assessment
- Start/Continue button
- Progress bar
- Completed result card

Manager/Admin cards:

- Licence summary
- Respondent progress
- Completed assessments
- Triggered flags overview

## Assessment Page

Path:

```text
/assessment/[sessionId]
```

Components:

- Question card
- Likert buttons 1–5
- Progress bar
- Area/SubArea label
- Back/Next buttons
- Autosave status

Rules:

- Save response immediately.
- Allow changing answers before completion.
- Do not allow editing after completion.

## Results Page

Path:

```text
/results/[sessionId]
```

Display:

- Domain score chart
- Threshold comparison
- Triggered domains
- Flags
- Insights
- Completion timestamp

## Admin Page

Path:

```text
/admin
```

Features:

- Organisation users
- Licence allocation
- Assessment completion status
- Result visibility
