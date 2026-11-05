# The React client (no Node, no build)

The same five pages as the HTMX version (home, users, sign up, sign in, profile, edit, delete),
written as **React 19 components** that the browser loads directly. It runs on the same FastAPI
server, under **http://localhost:8000/react**, and calls the same `/api` routes. Students need
nothing beyond Python: no Node.js, no npm, no Vite.

```
Browser ──► uvicorn :8000
              ├── /react, /react/...  → app/static/react/index.html  (one page; React Router picks the view)
              ├── /static/react/*.js  → the components (plain ES modules)
              ├── /static/vendor/react-all.js → React + ReactDOM + React Router + htm, vendored
              └── /api/...            → JSON, the same routes the HTMX pages and api.http use
```

## Where to look

| Chapter 3 `client/src/` | React client here | HTMX version |
|---|---|---|
| `main.jsx`, `App.jsx`, `MainRouter.jsx` | `app/static/react/main.js`, `App.js`, `MainRouter.js` | `app/routes/pages.py` |
| `core/Menu.jsx` | `core/Menu.js` | `templates/_menu.html` |
| `core/request.js`, `auth/api-auth.js`, `user/api-user.js` | the same files, same code | (none: forms post to the server) |
| `auth/auth-helper.js` | the same file, same code (sessionStorage + Bearer) | httpOnly cookie |
| `auth/PrivateRoute.jsx` | `auth/PrivateRoute.js` | `page_user()` in `pages.py` |
| `auth/Signin.jsx`, `user/Signup.jsx` | `auth/Signin.js`, `user/Signup.js` (React 19 `useActionState`) | `signin.html`, `signup.html` |
| `user/Users.jsx`, `Profile.jsx`, `EditProfile.jsx`, `DeleteUser.jsx` | the same names, `.js` | `users.html`, `profile.html`, `edit_profile.html` |
| `vite.config.js` proxy + history fallback | `app/routes/react_client.py` | |
| MUI | `app/static/style.css` (shared with the HTMX pages) | |

## What is different from the Chapter 3 code

Only two things. The components, hooks, router and API calls are the same.

**1. Imports name a file.** There is no bundler to resolve package names, so:

```js
// Chapter 3 (Vite)
import { useState } from 'react'
import { Link } from 'react-router'
// here (browser)
import { useState, Link, html } from '/static/vendor/react-all.js'
```

**2. No JSX.** Browsers don't understand JSX; it always needs a compiler (Vite/Babel). The
[htm](https://github.com/developit/htm) library offers an almost identical syntax using
JavaScript's own tagged template literals:

| JSX | htm |
|---|---|
| `<Profile />` | `` html`<${Profile} />` `` |
| `<Link to="/users">Users</Link>` | `` html`<${Link} to="/users">Users</${Link}>` `` |
| `<p className="muted">{user.email}</p>` | `` html`<p className="muted">${user.email}</p>` `` |
| `onClick={() => setOpen(true)}` | `onClick=${() => setOpen(true)}` |
| `{users.map((u) => <li key={u._id}>{u.name}</li>)}` | `` ${users.map((u) => html`<li key=${u._id}>${u.name}</li>`)} `` |

The rules are React's, not HTML's, in both: `className`, `htmlFor`, `autoComplete`, `defaultValue`.
Lowercase tags are HTML elements, `${Component}` is a component.

## Things worth showing in class

- **DevTools > Network:** open `/react`, then click *Sign In*. `Signin.js` downloads only then:
  `lazy(() => import(...))` code splitting, done by the browser instead of Vite.
- **Users page, both versions:** the HTMX page arrives with the list already in the HTML. The React
  page arrives empty, then `useEffect` fetches `/api/users` and renders. Same data, opposite places.
- **View source:** `/users` shows the users in the HTML; `/react/users` shows only `<div id="root">`.
- **Sign in on `/react`, then open `/`:** you are signed in there too. The sign-in API sets the
  httpOnly cookie that the HTMX pages use, and returns the token that the React client keeps in
  sessionStorage. `app/auth.py` accepts either.
- **StrictMode:** this is React's development build, so effects run twice in development (watch the
  doubled `/api/users/...` requests). Same behaviour as `npm run dev`.
- **Security headers unchanged:** the Content-Security-Policy still forbids inline scripts and
  `eval`, and the client needs neither: every script is a file from this server.

## Where react-all.js comes from (maintainer only)

React 19 is only published for bundlers, so `app/static/vendor/react-all.js` is built **once** by
the maintainer, on a machine with Node and internet, and committed like `htmx.min.js`:

```powershell
cd tools\vendor-react
npm ci
npm run build      # esbuild: react, react-dom/client, react-router, htm → one ES module
```

Versions are pinned in `tools/vendor-react/package.json` (with `package-lock.json`).
`tools/vendor-react/entry.js` lists what the file exports; add a name there if a component needs
another React function. Students and lab machines never run any of this.

## The in-browser JSX demo (`/react-jsx`, demo only)

The same pages again, this time in **real JSX** with Chapter 3's import lines
(`import { useState } from 'react'`, `import { Link } from 'react-router'`), in
`app/static/react-jsx/*.jsx`. The browser compiles them with **Babel standalone**
(`app/static/vendor/babel.min.js`) when the page loads. Open **http://localhost:8000/react-jsx**.

How it works, in `app/static/react-jsx/jsx-loader.js` (about 60 lines, the job Vite does):

1. fetch `main.jsx` → `Babel.transform()` → JavaScript;
2. rewrite its imports: `'react'`, `'react-router'`, `'react-dom/client'` → `/static/vendor/react-all.js`,
   and other `.jsx` files → compile those first (step 1), recursively;
3. run the result as an ES module (from a `blob:` URL). `lazy(() => import('./x.jsx'))` compiles
   that page the first time it is opened.

The usual tutorial approach, `<script type="text/babel" src="App.jsx">`, can't do this: each file
becomes a separate script, so `import` between `.jsx` files fails.

**Why it is for demos only** (worth saying in class):

| | `/react` (htm) | `/react-jsx` (Babel in the browser) | Chapter 3 (Vite) |
|---|---|---|---|
| Syntax | `` html`<${Link} to="/">` `` | JSX, same as the book | JSX |
| Who compiles | nobody | **every visitor's browser, on every load** | the developer, once (`vite build`) |
| Extra download | none | Babel, 2.4 MB | none |
| First load on the lab PC (measured, headless Edge) | ~1.9 s | ~6.2 s | |
| Content-Security-Policy | strict (`script-src 'self'`) | weaker: `script-src 'self' blob:` (only on `/react-jsx`) | strict |
| JSX syntax error | (no JSX) | shown on the page when it loads | shown in the terminal before you run it |

So it is good for showing JSX exactly as the book writes it, on machines without Node. For
anything students build on, `/react` (or Vite, where Node is allowed) is the honest choice.

A syntax error in a `.jsx` file appears on the page with Babel's code frame, a bit like Vite's
error overlay. Try deleting a `</section>` in `user/Users.jsx` and reloading `/react-jsx/users`.
