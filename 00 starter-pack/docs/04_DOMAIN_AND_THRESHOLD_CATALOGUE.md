# Domain and Threshold Catalogue

A domain is a scored dimension of the assessment.

A domain is triggered when:

```python
domain_score >= threshold
```

## Current Domains

| Domain                 |   Threshold |
|:-----------------------|------------:|
| Burnout Risk           |         267 |
| Authenticity Strain    |         257 |
| Suppressed Influence   |         118 |
| Internal Contradiction |         188 |
| Structural Misfit      |         188 |
| Old Wounds New Systems |         173 |
| Emotional Containment  |         210 |
| Values Misalignment    |         137 |

## Weight Summary from Question Bank

| Domain                 |   Non-zero Question Weights |   Max Weight |   Total Raw Weight |   Max Possible Score |
|:-----------------------|----------------------------:|-------------:|-------------------:|---------------------:|
| Burnout Risk           |                         106 |            1 |               73   |                  365 |
| Authenticity Strain    |                          98 |            1 |               70   |                  350 |
| Suppressed Influence   |                          51 |            1 |               32.4 |                  162 |
| Internal Contradiction |                          70 |            1 |               51.4 |                  257 |
| Structural Misfit      |                          80 |            1 |               51.4 |                  257 |
| Old Wounds New Systems |                          75 |            1 |               47.2 |                  236 |
| Emotional Containment  |                          93 |            1 |               57.2 |                  286 |
| Values Misalignment    |                          68 |            1 |               37.6 |                  188 |

## Implementation Notes

- Thresholds are stored on the `Domain` model.
- Domain names must be unique after normalization.
- Domain scores must be stored per completed session.
- Do not recalculate historical results dynamically unless explicitly performing a controlled re-score.
