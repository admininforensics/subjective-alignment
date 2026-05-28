# Testing Strategy

## Backend Tests

Create tests for:

- CSV import
- Domain name normalization
- Reverse Likert scoring
- Weighted scoring
- Threshold triggering
- Pairwise rule triggering
- Licence assignment
- Session start/resume
- Completion locking
- API permissions

## Critical Test Cases

### Reverse Scoring

```text
raw=1, reverse=True => effective=5
raw=5, reverse=True => effective=1
raw=3, reverse=True => effective=3
```

### Rule Trigger

Given:

```text
Burnout Risk triggered = True
Authenticity Strain triggered = True
```

Then:

```text
Energy Leak triggered = True
```

Given either domain is false:

```text
Energy Leak triggered = False
```

### Licence

- Cannot start without assigned licence.
- Cannot complete twice on same licence.
- Completed session consumes licence.
