# NetSecure Frontend

React + TypeScript + Vite + Tailwind CSS v4 dashboard for NetSecure.

Setup and commands: see **Frontend Setup** in [`docs/CONTRIBUTING.md`](../docs/CONTRIBUTING.md).

## Layout

| Path | Purpose |
|------|---------|
| `src/main.tsx` | Entry point; creates the browser router |
| `src/routes.tsx` | Route table (shared with tests) |
| `src/layouts/DashboardLayout.tsx` | Sidebar navigation, header, page outlet |
| `src/pages/` | One component per route |
| `src/components/` | Shared UI pieces |
| `src/api/client.ts` | Fetch wrapper for the Django API (`/api/...`) |
| `src/test/setup.ts` | Vitest setup (jest-dom matchers, cleanup) |

Tests sit next to the code they cover as `*.test.tsx`.
