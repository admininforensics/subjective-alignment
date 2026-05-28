# Frontend Architecture

Use Next.js 15 App Router.

```text
frontend/
├── app/
│   ├── login/
│   ├── dashboard/
│   ├── assessment/[sessionId]/
│   ├── results/[sessionId]/
│   └── admin/
├── components/
│   ├── dashboard/
│   ├── assessment/
│   ├── results/
│   └── layout/
├── lib/
│   ├── api.ts
│   ├── auth.ts
│   └── types.ts
└── hooks/
```

## Libraries

- Tailwind CSS
- shadcn/ui
- TanStack Query
- Recharts
- Zod

## UX Principles

- Dashboard feel.
- Minimal clutter.
- Clear progress.
- Autosave feedback.
- Mobile responsive.
- Results should feel insightful, not clinical.
