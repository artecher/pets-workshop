## Project Overview

Tailspin Shelter — a two-tier dog shelter web application used for GitHub workshop exercises. Flask REST API backend + Astro SSR frontend.

## Architecture

- **Backend** (`app/server/`): Flask API serving JSON from SQLite via SQLAlchemy ORM. Runs on port 5100.
- **Frontend** (`app/client/`): Astro SSR app with Tailwind CSS v4. Fetches data server-side from the Flask API. Runs on port 4321.
- API URL configured via `API_SERVER_URL` env var (defaults to `http://localhost:5100`).
- Seed data lives in `app/server/models/dogs.csv` and `app/server/models/breeds.csv`.
