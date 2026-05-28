# System Overview

Subjective Alignment is a licensed personality/workplace assessment platform.

A respondent answers 132 Likert-scale questions. Each question can contribute weighted points to one or more psychological/organisational domains. At the end of the assessment, domain totals are compared against thresholds. Triggered domain combinations activate flags and insights.

## Current Seed Data

| Item | Count |
|---|---:|
| Questions | 132 |
| Domains | 8 |
| Rules | 28 |
| Areas | 5 |
| SubAreas | 22 |

## Primary Roles

| Role | Description |
|---|---|
| Respondent | Person completing the assessment |
| Manager | Person who can view results for assigned respondents |
| Organisation Admin | Manages organisation users, licences and assignments |
| Super Admin | Internal platform owner/admin |

## Core Flow

```text
Organisation buys licences
        ↓
Admin invites/respondent is created
        ↓
Licence is assigned
        ↓
Respondent logs in
        ↓
Respondent starts or resumes assessment
        ↓
Responses are autosaved
        ↓
Respondent completes assessment
        ↓
Scoring engine calculates domain totals
        ↓
Threshold engine marks triggered domains
        ↓
Rule engine activates flags and insights
        ↓
Results are visible according to permissions
```
