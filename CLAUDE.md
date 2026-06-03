# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tailspin Shelter — a two-tier dog shelter web application used for GitHub workshop exercises. Flask REST API backend + Astro SSR frontend.

## Architecture

- **Backend** (`app/server/`): Flask API serving JSON from SQLite via SQLAlchemy ORM. Runs on port 5100.
- **Frontend** (`app/client/`): Astro SSR app with Tailwind CSS v4. Fetches data server-side from the Flask API. Runs on port 4321.
- API URL configured via `API_SERVER_URL` env var (defaults to `http://localhost:5100`).
- Seed data lives in `app/server/models/dogs.csv` and `app/server/models/breeds.csv`.

## Common Commands

### Start the full application
```bash
cd app/scripts && ./start-app.sh
```

### Backend (Flask)
```bash
cd app/server
python3 app.py                        # start server on :5100
```

### Frontend (Astro)
```bash
cd app/client
npm install
npm run dev                           # dev server on :4321
npm run build                         # production build
```

### Run Tests

**Backend unit tests (pytest):**
```bash
cd app/server
pytest test_app.py -v                                          # all tests
pytest test_app.py::TestGetDogs::test_returns_200 -v           # single test
```

**Frontend E2E tests (Playwright):**
```bash
cd app/client
npm run test:e2e                       # all E2E tests (auto-starts Flask + Astro)
npm run test:e2e:ui                    # interactive UI mode
npm run test:e2e:debug                 # debug mode
npx playwright test e2e-tests/homepage.spec.ts                 # single file
npx playwright test -g "should load homepage"                  # single test by name
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dogs` | List all dogs |
| GET | `/api/dogs/<id>` | Get dog by ID |
| GET | `/api/breeds` | List all breeds |

## Key Technical Details

- Python 3.12, Node.js 24 (per CI workflow)
- Astro uses `@astrojs/node` adapter for SSR — `astro.config.mjs` sets `output: "server"`
- Backend models use `@validates` decorators for field validation
- E2E tests auto-start both servers via Playwright's `webServer` config
- Docker support exists for the client only (`app/client/Dockerfile`)
