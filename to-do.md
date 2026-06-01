# Subjective Alignment — TODO

This file is meant to stay **continuously updated** as we progress.

## Done

- **Spec review**: Read and followed `00 starter-pack/docs/*` build order and constraints (data-driven, CSV-seeded).
- **Repo scaffolding**: Created `backend/`, `frontend/`, and top-level `seed_data/` populated from the starter pack CSVs.
- **Backend foundation**:
  - Django 5 project (`backend/config`)
  - DRF + SimpleJWT auth wired in settings
  - Postgres-ready DB config via `DATABASE_URL` (fallback sqlite for local)
  - CORS enabled for local dev
- **Backend data model**: Implemented core models + migrations:
  - Organisation, custom User + roles, ManagerAssignment
  - Assessment content (Assessment/Area/SubArea/Domain/Question/Weights)
  - Licensing + sessions (Licence, AssessmentSession)
  - Auditability + results snapshots (Response, DomainScoreResult, TriggeredFlag)
  - Rules (pairwise + `rule_type`)
- **CSV import (idempotent)**:
  - `python manage.py seed_assessment ...` uses `mac_roman`, domain normalization, blank-weight parsing
- **Scoring + rule engines**:
  - Reverse-likert and weighted scoring persisted at completion time
  - Pairwise AND rule triggering persisted as flagged insight snapshots
- **Backend APIs (MVP)**: Implemented endpoints from `12_API_CONTRACTS.md`:
  - Auth login, dashboard, current assessment, session start/detail/save/complete, results detail
  - Org respondents/results listing, licence assignment (basic)
- **Backend tests**:
  - Import normalization/idempotency
  - Scoring (reverse + threshold)
  - Rule triggering
- **Frontend (MVP)**:
  - Next.js App Router + TS + Tailwind + shadcn/ui + TanStack Query + Recharts
  - Pages: `/login`, `/dashboard`, `/assessment/[sessionId]`, `/results/[sessionId]`, `/admin`
  - API client + localStorage auth
- **Verification**:
  - Backend test suite passing
  - Frontend lint passing; build passing
- **Admin visibility for CSV source files**:
  - Added a custom admin page to view/preview/download CSVs from `/data`
- **UI refresh (light clinical theme)**:
  - Light calm palette, Elms Sans headings + Source Sans 3 body
  - App shell (top nav, user menu, sign out)
  - Split-screen auth layout (login/signup/forgot/reset)
  - Login background image path documented under `frontend/public/images/`

## Still to do

- **Render + HTTPS go-live checklist**:
  - **Blueprint setup**:
    - Create Render Blueprint from `admininforensics/subjective-alignment` (uses `render.yaml`).
    - Set frontend `NEXT_PUBLIC_API_URL` to `https://<backend>.onrender.com/api` (must include `/api`).
  - **Backend env (Render → backend service → Environment)**:
    - Ensure `DEBUG=False`, `SECURE_SSL_REDIRECT=True`.
    - Add `CORS_ALLOWED_ORIGINS=https://<frontend>.onrender.com` (comma-separated if multiple).
    - Add `CSRF_TRUSTED_ORIGINS=https://<frontend>.onrender.com` (comma-separated if multiple).
    - Ensure `ALLOWED_HOSTS` includes `.onrender.com` and any custom domains.
  - **Frontend deploy**:
    - Redeploy frontend after setting `NEXT_PUBLIC_API_URL` (it’s baked in at build time).
    - If build still fails, use “Clear build cache & deploy”.
  - **Custom domain (optional)**:
    - Add custom domain(s) to the **frontend** service in Render.
    - Create DNS records at your registrar (as shown by Render).
    - Wait for Render to provision SSL cert; confirm HTTPS works and HTTP redirects.
  - **Smoke test**:
    - Confirm login + signup works.
    - Confirm API calls go to `https://<backend>.onrender.com/api/...` in browser Network tab.

- **Onboarding (signup)**:
  - Add `/signup` page and `POST /api/auth/signup/` to create a respondent + organisation for local/demo use.
  - Later: replace with invitation-based onboarding (org admin issues invites) and stronger password policy / email verification.

- **Licensing (purchase + PayFast)**:
  - Add basic “Get a licence” flow in the UI (stubbed purchase endpoint).
  - Integrate PayFast for real payments (webhook/ITN verification), then gate licence creation behind successful payment.
  - Add admin UI for licence inventory + assignment + revocation.

- **Permissions hardening (backend)**:
  - Enforce manager/admin visibility rules consistently across all session/result endpoints (currently focused on results; session access is respondent-only in the main flow).
  - Add explicit permission classes (instead of inline checks) for consistency and testability.
- **Admin/org workflows (backend + frontend)**:
  - Admin UI for licence inventory and assignment (frontend currently only lists respondents).
  - Endpoints for listing licences and their statuses (available/assigned/in_progress/consumed).
  - Better manager views (assigned respondents + progress summaries).
- **Assessment UX polish (frontend)**:
  - Better navigation (question index, “unanswered” indicator), and clearer autosave state.
  - Likert labels (Strongly disagree → Strongly agree) instead of numbers only.
- **Results UX polish (frontend)**:
  - Refine radar chart styling for light theme; insight card typography.
  - Improve copy to match “insightful, not clinical” tone.
- **Deployment readiness**:
  - Document Render setup (backend + frontend env vars) in repo docs (starter pack has guidance; we should mirror it here).
  - Production settings tightening (DEBUG false defaults, allowed hosts, CORS origins required in prod).
- **Seed/import robustness**:
  - Add stronger validation (required columns, row counts, domain column detection).
  - Add logging improvements and/or `--dry-run`.
- **Testing expansion**:
  - API permission tests (respondent vs manager vs org admin vs super admin)
  - Session start/resume/locking edge cases (cannot complete twice, cannot edit after completion)

## Next recommended step

- **Implement full licence/admin workflow** (licence inventory + assignment UI + API), then **permission tests** to lock in visibility rules.

