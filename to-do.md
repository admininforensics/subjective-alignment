# Subjective Alignment — TODO

This file is meant to stay **continuously updated** as we progress.

## MVP status

**Core product loop is built and working:** sign up → activate licence (or dev bypass) → paginated assessment → scored results → full SUBAL narrative report (SUBAL wheel, focus areas, print/PDF).

Deployed on Render (`subjective-alignment-frontend` / `subjective-alignment-backend`). Remaining work is mostly **production hardening**, **org/admin workflows**, and **polish** — not greenfield features.

---

## Done

### Foundation
- **Spec review**: Read and followed `00 starter-pack/docs/*` build order and constraints (data-driven, CSV-seeded).
- **Repo scaffolding**: `backend/`, `frontend/`, `data/` / `seed_data/` CSVs.
- **Backend foundation**: Django 5, DRF, SimpleJWT, Postgres via `DATABASE_URL`, CORS, WhiteNoise, `render.yaml` blueprint.
- **Backend data model**: Organisation, User + roles, ManagerAssignment, assessment content, licensing/sessions, results snapshots, rules.
- **CSV import (idempotent)**: `seed_assessment` / `seed_default_assessment` (auto-runs on Render deploy).
- **Scoring + rule engines**: Reverse-likert, weighted domain scores, pairwise rule flags at completion.
- **Backend tests**: Import, scoring, rules, licensing session management, password reset, report generation (template provider).

### APIs
- Auth: login, signup, refresh, password reset request + confirm.
- Respondent flow: dashboard, current assessment, session start/detail/save/complete, results detail.
- Licensing: activate by code, assign, stub purchase.
- Session management: restart in-progress, delete latest completed.
- Dev-only: `POST /api/sessions/simulate-complete/` (random 1–5 scores, `DEBUG=True` only).
- Org: respondents + results listing (basic).

### Frontend
- Pages: `/login`, `/signup`, `/forgot-password`, `/reset-password`, `/dashboard`, `/assessment/[sessionId]`, `/results/[sessionId]`, `/admin`.
- API client + auth (localStorage JWT, refresh-on-401).
- TanStack Query wired via root `Providers`.
- **UI refresh**: Light clinical theme, Elms Sans + Source Sans 3, `AppShell`, `AuthLayout`, login background image support.
- **Assessment UX**: 5 questions per page, page-gated Next, autosave, **Save and exit**, progress bar.
- **Dashboard**: licence activation, continue/start, restart assessment, delete previous assessment, dev simulate button.
- **Results**: Full SUBAL report sections, alignment wheel, print-to-PDF download.
- **Admin**: Respondent list (read-only).

### Auth & licensing (recent)
- Password reset flow (email link; console backend locally, SMTP needed on Render).
- Licence activation by code on dashboard.
- `SKIP_LICENCE_REQUIREMENT` + dev org auto-assignment for local/testing (must be **off** in production).
- `ensure_superuser` on Render deploy.

### Reports (recent)
- `AssessmentReport` model + `generate_report()` pipeline.
- LLM narratives: OpenAI, Ollama, or template fallback (`REPORT_LLM_PROVIDER`).
- Frontend report page with SUBAL wheel and section layout.

### Ops & docs
- `USER_MANUAL.md` (local run, licences, env vars).
- Django admin: licences (incl. code generation), CSV preview page.

---

## Still to do

### 1. Production go-live (recommended first)

- [ ] **Turn off licence bypass on Render**: ensure `SKIP_LICENCE_REQUIREMENT` is unset/false on backend; do not set `NEXT_PUBLIC_SKIP_DEV_TOOLS` on frontend.
- [ ] **Fix Render CORS env**: `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` belong on the **backend** service (currently duplicated on frontend in `render.yaml` — move/add on backend).
- [ ] **SMTP for password reset**: set `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` on backend.
- [ ] **Report LLM on Render**: set `REPORT_LLM_PROVIDER=openai` + `OPENAI_API_KEY`, or `template` for deterministic copy without an LLM. Ollama is local-only.
- [ ] **Smoke test on production**: signup/login, licence activate, full assessment, report generation, password reset email.
- [ ] **Custom domain (optional)**: DNS + SSL on Render frontend; update `FRONTEND_URL`, CORS, and `NEXT_PUBLIC_API_URL` if URLs change.

### 2. Assessment & results polish

- [ ] **Likert labels** on assessment buttons (e.g. Strongly disagree → Strongly agree), not numbers only.
- [ ] **Clearer autosave state** (saved / saving / error per page).
- [ ] **Results copy pass**: tone check against “insightful, not clinical”; refine template/LLM prompts if needed.
- [ ] **Radar / wheel styling** tweaks for print layout (page breaks, margins).

### 3. Permissions & testing

- [ ] **Permission hardening**: consistent manager/org-admin access on session + result endpoints (results partially covered via `can_view_session`; session detail is respondent-only).
- [ ] **DRF permission classes** instead of scattered inline checks.
- [ ] **API permission tests**: respondent vs manager vs org admin vs super admin.
- [ ] **Session edge-case tests**: cannot complete twice, cannot edit after completion, restart/delete flows.

### 4. Org / admin workflows

- [ ] **Licence inventory API**: list licences by org with status (available / assigned / in progress / consumed).
- [ ] **Admin UI**: create/assign/revoke licences, view respondent progress (beyond read-only list).
- [ ] **Manager dashboard**: assigned respondents + progress summaries.

### 5. Seed / import robustness

- [ ] Stronger CSV validation (required columns, row counts).
- [ ] `--dry-run` on `seed_assessment`.

---

## Later / post-MVP

- **PayFast payment gate**: real purchase flow + ITN webhook; gate `purchase_licence_for_user` behind verified payment. Stub endpoint exists today.
- **Invitation-based onboarding**: replace open signup with org-admin invites; email verification; stronger password policy.
- **Super-admin reset**: explicit admin action to reset a completed session (per business rules doc) instead of respondent self-delete.
- **Dedicated PDF export** (server-side or improved print CSS) if print-to-PDF is not enough.
- **Rate limiting** on auth and simulate endpoints.
- **Monitoring**: error tracking (e.g. Sentry), uptime checks on Render.

---

## Next recommended steps

1. **Production hardening checklist** (§1 above) — especially CORS on backend, disable licence bypass, configure SMTP + report LLM.
2. **Likert labels** — quick UX win before wider user testing.
3. **Permission tests + licence inventory API** — unlocks real org-admin use without Django admin.

---

## Notes

- Local dev: see `USER_MANUAL.md`. Default API `http://localhost:8000/api`, frontend `http://localhost:3000`.
- Dev simulate button: frontend shows in `development` or when `NEXT_PUBLIC_SHOW_DEV_TOOLS=true`; backend requires `DEBUG=True`.
- Do not commit `backend/.env` or `frontend/.env.local`.
