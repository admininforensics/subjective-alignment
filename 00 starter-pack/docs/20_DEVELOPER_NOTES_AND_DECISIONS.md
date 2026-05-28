# Developer Notes and Decisions

## Key Product Decisions

- Organisation-based licensing.
- Respondents can pause and resume.
- One completed assessment per assigned licence.
- Managers and admins may view results subject to permissions.
- Pairwise rule engine for MVP.
- Future-proof rule engine using `rule_type` field.

## Why Pairwise Rules for MVP

The current rules-bank CSV is pairwise:

```text
Domain A + Domain B => Flag + Insight
```

A generic expression parser would add unnecessary complexity now.

The service layer should, however, make it possible to add expression-based rules later.

## Do Not Do This

- Do not hardcode questions in React.
- Do not hardcode thresholds in Python.
- Do not hardcode flags in code.
- Do not allow completed sessions to be edited.
- Do not recalculate historical insight text dynamically.
- Do not rely on frontend permissions only.

## Good Engineering Practices

- Use transactions for session completion.
- Use database constraints for uniqueness.
- Use tests for scoring and rule evaluation.
- Store snapshots of final results.
- Keep business logic out of views.
