# Business Requirements

## Licensing

The platform is organisation-based.

An organisation purchases licences. A licence allows one assigned respondent to complete one assessment.

### Rules

- A licence belongs to an organisation.
- A licence can be assigned to one respondent.
- A respondent can only start an assessment if they have an assigned active licence.
- Once the assessment is completed, the licence is consumed.
- A respondent cannot complete the same assigned assessment multiple times.
- If the business later requires retesting, issue a new licence or create a new assessment assignment.

## Assessment Progress

Users may pause and resume.

### Rules

- Responses must be saved as the respondent progresses.
- A respondent can leave and return later.
- The dashboard must show the current progress.
- Completed sessions cannot be edited unless a super admin explicitly resets them.

## Results Visibility

Results may be visible to:

- Respondent
- Assigned manager
- Organisation admin
- Super admin

Permissions must be enforced server-side.

## Rules and Flags

A rule triggers if and only if:

```text
Domain A score >= Domain A threshold
AND
Domain B score >= Domain B threshold
```

## Auditability

The system must retain:

- Original questions
- Assessment version
- Raw responses
- Effective Likert scores
- Weighted domain contributions
- Final domain totals
- Triggered flags
- Insight text at time of completion
