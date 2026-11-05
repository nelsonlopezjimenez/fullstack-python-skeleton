# Full-stack Python skeleton

Chapter 3's MERN skeleton (users, sign up, sign in, profile, edit, delete), rebuilt with
**FastAPI + MongoDB + Jinja2/HTMX**. It needs no Node.js and works fully offline.

| | MERN (Chapter 3) | Here |
|---|---|---|
| Database | MongoDB + Mongoose | MongoDB + **Beanie** |
| Server | Express on Node | **FastAPI** on Python 3.13 |
| Frontend | React + Vite + MUI | **Jinja2** templates + **HTMX** (one vendored JS file, no build) |
| Packages | npm, `node_modules/`, Verdaccio | pip, `.venv/`, a wheelhouse folder or devpi/pypiserver |

The `/api` routes, their JSON and their error messages are the same as Chapter 3's, so
[api.http](api.http) works against both servers. Password hashes are compatible too.

- **What maps to what** (packages, files, concepts): [docs/mern-to-python.md](docs/mern-to-python.md)
- **No internet in the lab**: [instructions/offline-setup.md](instructions/offline-setup.md)

## Quick start (online)

```powershell
python -m venv .venv                          # the Python version of node_modules
.\.venv\Scripts\Activate.ps1                  # Git Bash: source .venv/Scripts/activate
python -m pip install -r requirements-dev.txt # npm install
copy .env.example .env                        # then set JWT_SECRET
python -m pytest                              # npm test (MongoDB on localhost:27017)
python -m uvicorn app.main:app --reload --port 8000   # npm run dev
```

Open http://localhost:8000.

## Quick start (offline)

On a machine with internet: `powershell -ExecutionPolicy Bypass -File tools\build-wheelhouse.ps1 -Zip`.
Copy the zip to the lab machine, unzip it as `wheelhouse\` in the repo, then run
`powershell -ExecutionPolicy Bypass -File tools\install-offline.ps1`.
Details: [instructions/offline-setup.md](instructions/offline-setup.md).

## Layout

```
app/
  __main__.py          python -m app            (server.js)
  main.py              app, middleware, errors  (express.js)
  config.py            settings from .env       (config/config.js)
  errors.py            readable error messages  (helpers/dbErrorHandler.js)
  auth.py              JWT, require_signin, has_authorization (auth.controller.js)
  user_service.py      user operations shared by the API and the pages
  models/user.py       User document + request/response models (models/user.model.js)
  routes/api_users.py  /api/users               (user.routes.js + user.controller.js)
  routes/api_auth.py   /api/auth/sessions       (auth.routes.js)
  routes/pages.py      HTML pages               (the React client)
  templates/           Jinja2 pages and fragments
  static/              htmx.min.js (vendored), style.css, seashell.jpg
tests/                 pytest: unit tests + API + pages (MongoDB tests skip if it is down)
tools/                 build-wheelhouse.ps1, install-offline.ps1
```

Code comments marked `[BEGINNER]` explain Python and FastAPI basics; `[ADVANCED]` comments explain
design decisions and compare them with the Node version.

## Settings (.env)

| Variable | Default | |
|---|---|---|
| `PORT` | 8000 | for `python -m app` |
| `MONGODB_URI` | `mongodb://localhost:27017/pythonskeleton?directConnection=true` | |
| `JWT_SECRET` | a development value | **required in production**, at least 32 characters |
| `JWT_EXPIRES_IN_SECONDS` | 86400 | token and cookie lifetime |
| `CORS_ORIGIN` | empty (off) | comma-separated origins allowed to call `/api` |
| `ENV` | development | `production` turns on Secure cookies and the secret check |
