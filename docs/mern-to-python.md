# MERN → Python: what maps to what

This repo is **Chapter 3's `mern-skeleton`** (users + sign up / sign in / profile / edit / delete)
rewritten in Python. The `/api` routes, the JSON they return and the error messages are the same,
so `api.http` works against both servers. Only the frontend is different: there is no React,
because the lab machines have no Node.js.

## The stack

| MERN | Here | Why this one |
|---|---|---|
| **M**ongoDB | MongoDB | Unchanged: same server, same URI, same `?directConnection=true`. |
| Mongoose | **Beanie** (ODM, built on Pydantic + PyMongo's async driver) | Models are classes with typed fields. They validate and define indexes, like a Mongoose schema. |
| **E**xpress | **FastAPI** (on Starlette) | Routes are decorated `async` functions. Middleware such as `requireSignin` becomes `Depends(...)`. |
| **R**eact | **Jinja2 templates + HTMX** | Server-rendered HTML. A ~50 KB vendored JS file sends `hx-post` / `hx-patch` / `hx-delete` requests and swaps the HTML that comes back. No build step and no Node. |
| **N**ode | CPython 3.13 | |

## The tools

| npm world | Python world |
|---|---|
| `node_modules/` | `.venv/` (a virtual environment, one per project) |
| `package.json` | `pyproject.toml` |
| `package-lock.json` | `requirements.txt` (every version pinned) |
| `devDependencies` | `requirements-dev.txt` / `[project.optional-dependencies] dev` |
| `npm install` | `python -m pip install -r requirements-dev.txt` |
| `npm run dev` (nodemon) | `python -m uvicorn app.main:app --reload --port 8000` |
| `npm start` | `python -m app` |
| `npm test` (Jest/Vitest) | `python -m pytest` |
| Verdaccio | devpi / pypiserver, or a `wheelhouse/` folder (see [instructions/offline-setup.md](../instructions/offline-setup.md)) |
| `.npmrc` `registry=` | `pip.ini` `index-url =`, or `PIP_INDEX_URL` |
| `--env-file=.env` / dotenv | `pydantic-settings` (reads `.env` itself) |

## The packages

| Chapter 3 (Node) | Here (Python) | Built in? |
|---|---|---|
| `express` | `fastapi` + `uvicorn` (the server process) | |
| `mongoose` | `beanie` (+ `pymongo`) | |
| `jsonwebtoken`, `express-jwt` | `PyJWT` + a `require_signin` dependency | |
| `node:crypto` `scryptSync`, `timingSafeEqual`, `randomBytes` | `hashlib.scrypt`, `hmac.compare_digest`, `secrets.token_hex` | ✅ standard library, same as Node |
| `cookie-parser` | `request.cookies` / `response.set_cookie` | ✅ Starlette |
| `compression` | `GZipMiddleware` | ✅ Starlette |
| `cors` | `CORSMiddleware` | ✅ Starlette |
| `helmet` | a small middleware in `app/main.py` | hand-written |
| `lodash` `_.extend` | `model_dump(exclude_unset=True)` + `setattr` | ✅ Pydantic |
| React Router | FastAPI page routes in `app/routes/pages.py` | |
| MUI | `app/static/style.css` (plain CSS) | |
| `fetch` + `useState` | `hx-post` / `hx-patch` / `hx-delete` + `hx-target` | HTMX |
| `sessionStorage` JWT + Bearer header | httpOnly cookie `t` (the browser sends it by itself) | |

## File by file

| Chapter 3 `mern-skeleton/` | This repo |
|---|---|
| `server/server.js` | `app/__main__.py` (starts uvicorn) |
| `server/express.js` | `app/main.py` (app, middleware, error handlers, lifespan/DB connect) |
| `server/config/config.js` | `app/config.py` |
| `server/models/user.model.js` | `app/models/user.py` |
| `server/helpers/dbErrorHandler.js` | `app/errors.py` |
| `server/controllers/auth.controller.js` | `app/auth.py` |
| `server/routes/auth.routes.js` | `app/routes/api_auth.py` |
| `server/controllers/user.controller.js` + `routes/user.routes.js` | `app/routes/api_users.py` (FastAPI keeps the route and the handler together) |
| `server/api.http` | `api.http` (same requests, port 8000) |
| `server/tests/*.test.js` | `tests/test_*.py` |
| `client/src/MainRouter.jsx` | `app/routes/pages.py` |
| `client/src/core/Menu.jsx` | `app/templates/_menu.html` |
| `client/src/core/Home.jsx`, `NotFound.jsx` | `app/templates/home.html`, `not_found.html` |
| `client/src/auth/Signin.jsx` | `app/templates/signin.html` |
| `client/src/auth/PrivateRoute.jsx` | the `page_user` dependency in `app/routes/pages.py` |
| `client/src/user/Signup.jsx`, `Users.jsx`, `Profile.jsx`, `EditProfile.jsx`, `DeleteUser.jsx` | `app/templates/signup.html`, `users.html`, `profile.html`, `edit_profile.html` (delete is a button on the profile) |
| `client/src/core/FormError.jsx` | `app/templates/_form_error.html` |

## The biggest differences

1. **Where the HTML is made.** React builds pages in the browser from JSON. Here the server returns
   HTML: full pages for normal navigation, and small fragments (`_form_error.html`) for HTMX requests.
2. **Where the token lives.** The React client kept the JWT in `sessionStorage` and sent it as
   `Authorization: Bearer`. Here the browser keeps it in the httpOnly cookie `t`, and page
   JavaScript cannot read it. `require_signin` accepts **both**, so `api.http` and other API clients
   still use the Bearer header.
3. **Validation.** Mongoose validated when the document was saved. Here Pydantic validates the
   *request body* before the handler runs (`UserCreate`, `UserUpdate`), and the response model
   (`UserOut`) decides which fields leave the server, instead of the `toJSON` transform.
4. **Middleware order.** Express runs middleware left to right. FastAPI resolves `Depends()`
   as a tree: `user_by_id` depends on `require_signin`, so the token is always checked before the
   database is queried. That is the same order Chapter 3 had to fix (the `router.param` note in
   `user.routes.js`).
5. **Password hashes are compatible.** Both versions use scrypt (N=16384, r=8, p=1, 64 bytes) with
   the hex salt string as the salt. If you point this app at the `mernskeleton` database, users who
   signed up on the Node server can sign in here.
