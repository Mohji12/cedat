# Website (Vite + React)

Bulk email UI for the FastAPI backend (`POST /send-emails`).

## Local development

By default the UI talks to the **deployed Lambda** URL configured in `.env.development` / `.env.production` and in `src/lib/api.ts`.

**Frontend** (from this folder):

```bash
npm install
npm run dev
```

Open the URL Vite prints (default `http://localhost:5173`).

**Optional local API**: run FastAPI from the repo root and point the site at it:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Set `VITE_API_BASE_URL=http://127.0.0.1:8000` in `.env.development.local` (overrides `.env.development`; not committed) or edit `.env.development`.

## Configuration

- `VITE_API_BASE_URL`: API base URL with **no** trailing slash. Defaults to the Lambda URL in `.env.development`, `.env.production`, and in code if the variable is unset.

## Build

```bash
npm run build
```

Static output is in `dist/`.
