# Build log: Chapter 3 skeleton in Python

Checklist: [build-checklist.md](build-checklist.md). One entry per commit.

## 1. Scaffold (`chore: scaffold ...`)
- **Changed:** pyproject.toml, requirements.txt (every version pinned), requirements-dev.txt, .gitignore,
  .env.example, docs/mern-to-python.md, vendored `htmx.org@2.0.4` (50 KB) and Chapter 3's seashell.jpg.
- **Why:** the lock was produced in a clean venv with only the runtime packages, then `pip freeze`.
- **Surprises:**
  - `uvicorn[standard]` pulls 5 compiled extras (httptools, watchfiles, websockets, PyYAML; uvloop on
    Linux only). Plain `uvicorn` keeps the offline wheelhouse at 3 compiled wheels.
  - A venv inside the session's temp folder failed with `[WinError 206] The filename or extension is too
    long` (httptools license path). Long paths → documented in offline-setup.md.

## 2. App, settings, MongoDB (`feat: FastAPI app, settings, ...`)
- **Changed:** app/config.py, app/errors.py, app/main.py, app/__main__.py.
- **Verified:** TestClient: /api/health 200, /api/nope → `{"error": "Route not found: GET /api/nope"}`, CSP header present.
- **Surprises:** root DEBUG logging floods with PyMongo's structured logs → only the `app` logger is DEBUG.
  FastAPI's `/docs` loads Swagger UI from a CDN (fails offline, blocked by CSP) → turned off, api.http instead.

## 3. User model + public API (`feat: User model ...`)
- **Changed:** app/models/user.py, app/user_service.py, app/routes/api_users.py.
- **Verified:** sign up 201, duplicate 400 "Email already exists", invalid → all three messages joined
  (same text as Node), missing body, malformed JSON, list without password fields.
  `hashlib.scrypt('secret1', 'abc123')` == Node's `crypto.scryptSync` output, byte for byte.
- **Notes:** Pydantic `PydanticCustomError` gives the exact message (a plain ValueError adds "Value error, ").
  `UserOut` uses `alias="_id"` + `validate_by_name` to keep the Node JSON key.

## 4. Auth (`feat: sign in/out, JWT, ...`)
- **Changed:** app/auth.py, app/routes/api_auth.py, protected routes in api_users.py.
- **Verified:** 14 requests from api.http: 200/400/401/403/404 exactly as the Node server.
- **Decision:** `require_signin` accepts the Bearer header **or** the httpOnly cookie (the pages have no JS
  to send a header). `user_by_id` depends on `require_signin`, so no DB query without a token.

## 5. HTMX + Jinja2 pages (`feat: HTMX + Jinja2 pages ...`)
- **Changed:** app/routes/pages.py, app/templates/*, app/static/style.css; BASE_DIR moved to config.py.
- **Verified:** TestClient with `HX-Request: true`, then headless Edge (playwright-core from
  `Full-Stack-React-Projects-shama-hoque/tools/node_modules`, throwaway script, not committed): sign up
  errors → sign up → wrong password → sign in → profile → edit error → save → users → sign out →
  protected redirect with `next` → back after sign in → delete → 404. No console errors.
- **Surprises:**
  - HTMX 2 does not swap 4xx responses by default → `responseHandling` in the `htmx-config` meta tag.
  - HTMX injects an inline `<style>` (blocked by our CSP) → `includeIndicatorStyles: false`.
  - A Jinja comment that mentions the comment syntax ends early → reworded.
  - Browser asked for /favicon.ico (404) → `<link rel="icon" href="data:,">`.

## 6. Tests (`test: pytest suite ...`)
- **Changed:** tests/ (49 tests: errors, config, auth units incl. a Node-computed hash, API, pages), api.http.
- **Verified:** `python -m pytest` → 49 passed, 0 warnings.
- **Surprises:** Starlette 1.10's TestClient warns "install httpx2 instead" → dev dependency httpx → httpx2
  (pydantic/httpx2, same API). PyJWT warns about HS256 secrets under 32 bytes → longer test secret,
  note in .env.example.

## 7. Offline tools (`feat(tools): offline wheelhouse ...`)
- **Changed:** tools/build-wheelhouse.ps1, tools/install-offline.ps1, instructions/offline-setup.md.
- **Verified:** wheelhouse for cp313/win_amd64 = 34 wheels, 9 MB zip; for manylinux2014_x86_64 = 34 wheels.
  Fresh copy of the repo + unzip + `venv --without-pip` → install-offline → pip repaired from the wheel →
  49 tests pass. Second run without any .venv → venv created with pip → 49 pass.
- **Surprises:**
  - Windows PowerShell 5.1 + `$ErrorActionPreference = "Stop"` + `2>$null` on a native command = the
    stderr line ("No suitable Python runtime found" from `py -3.13`) ends the script → `Test-Command` helper.
  - `python pip.whl/pip install pip.whl` is refused on Windows ("To modify pip, please run ... -m pip")
    → put the wheel on PYTHONPATH and run `python -m pip install pip.whl`.

## 8. README + this log (`docs: README and build log`)
