"""The React client (Chapter 3: client/, without Vite and without Node).

    GET /react, /react/...           the same index.html for every URL; React Router picks the page
    GET /react-jsx, /react-jsx/...   the same pages in real JSX, compiled IN THE BROWSER (demo only)

[BEGINNER] A "single-page app" has ONE HTML page. When you open /react/users/123 directly
(or press F5 there), the server must still answer with index.html, and React Router reads the
URL in the browser to decide what to show. Vite's dev server did this for Chapter 3's client;
here this route does it. The components themselves are plain files in app/static/react/.

[ADVANCED] The HTMX pages (app/routes/pages.py) and this client share the same /api routes and
the same database. Compare app/templates/profile.html with app/static/react/user/Profile.js.
"""
from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.config import BASE_DIR

router = APIRouter(include_in_schema=False)

INDEX = BASE_DIR / "static" / "react" / "index.html"
JSX_INDEX = BASE_DIR / "static" / "react-jsx" / "index.html"


# [BEGINNER] Two decorators, one function: /react and anything below it.
# {path:path} matches the rest of the URL, slashes included (Express: '/react/{*splat}').
@router.get("/react")
@router.get("/react/{path:path}")
async def react_client(path: str = ""):
    return FileResponse(INDEX)


# [ADVANCED] The in-browser JSX demo (app/static/react-jsx/jsx-loader.js). It gets a weaker
# Content-Security-Policy than every other page: see JSX_DEMO_CSP in app/main.py.
@router.get("/react-jsx")
@router.get("/react-jsx/{path:path}")
async def react_jsx_demo(path: str = ""):
    return FileResponse(JSX_INDEX)
