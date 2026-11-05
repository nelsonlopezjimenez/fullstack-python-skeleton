# Build checklist: Chapter 3 skeleton in Python (FastAPI + MongoDB + HTMX/Jinja2)

Decisions (2026-11-04): new repo, not a chapter in Full-Stack-React-Projects. Frontend: HTMX +
Jinja2 (no Node on the lab machines). Port Chapter 3's `mern-skeleton`. Target Python 3.13 on
win_amd64. One commit per step. Running log in [build-log.md](build-log.md).

| # | Step | Status |
|---|---|---|
| 1 | Scaffold: pyproject, pinned requirements, .gitignore, .env.example, MERN → Python mapping, vendored htmx + image | done |
| 2 | App + config + MongoDB connection (Beanie) + JSON error handlers + security headers | done |
| 3 | User model (scrypt like Ch03) + users API (`/api/users`, `/api/users/{id}`) | done |
| 4 | Auth: `/api/auth/sessions` (POST/DELETE), JWT, `require_signin`, `has_authorization` | done |
| 5 | HTMX + Jinja2 pages: home, users, sign up, sign in, profile, edit, delete, 404 | done |
| 6 | Tests (pytest) + `api.http` | todo |
| 7 | Offline: wheelhouse build + offline install scripts + instructions | todo |
| 8 | README + build log | todo |
| later | Teaching ladder (stacked `teach/…` branches like Ch03) | open |
| later | Push to GitHub, then Gitea via the bridge | open (user) |
| later | Port Chapter 5 (mern-social) | open |
