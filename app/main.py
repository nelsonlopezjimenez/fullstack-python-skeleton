"""The FastAPI app: middleware, routes, error handlers (Chapter 3: server/express.js + server.js)."""
import logging
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pymongo import AsyncMongoClient
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import BASE_DIR, settings
from app.errors import UserInputError, validation_message
from app.models.user import User
from app.routes import api_auth, api_users, pages, react_client

# [BEGINNER] logging is built in (Chapter 3 wrote helpers/logger.js). INFO for every library,
# DEBUG only for our own "app" logger in development: PyMongo's DEBUG output is very chatty.
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("app")
logger.setLevel(logging.INFO if settings.is_production else logging.DEBUG)

# [BEGINNER] Every Beanie model must be listed here so init_beanie can create its indexes.
DOCUMENT_MODELS = [User]


# [BEGINNER] lifespan = code that runs once at startup (before `yield`) and once at shutdown
# (after it). Chapter 3 connected Mongoose in server.js before app.listen(); this is the same
# moment, but owned by the app, so the tests start and stop the database connection too.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # [ADVANCED] tz_aware=True: dates come back from MongoDB with their UTC timezone attached,
    # so comparing them with datetime.now(UTC) works (naive and aware datetimes cannot be compared).
    client = AsyncMongoClient(settings.mongodb_uri, tz_aware=True)
    # [BEGINNER] get_default_database() is the name in the URI: .../pythonskeleton?... → pythonskeleton
    await init_beanie(database=client.get_default_database(), document_models=DOCUMENT_MODELS)
    logger.info("Connected to MongoDB database %s", client.get_default_database().name)
    yield
    await client.close()


# [ADVANCED] docs_url=None turns off FastAPI's built-in Swagger page at /docs. It loads its
# JavaScript and CSS from a CDN, which does not work offline and is blocked by the
# Content-Security-Policy below. Use api.http (VS Code REST Client) instead, as in Chapter 3.
app = FastAPI(title="Python Skeleton", lifespan=lifespan, docs_url=None, redoc_url=None)

# --- Middleware ---------------------------------------------------------------------------
# [BEGINNER] Same jobs as app.use(compress()) and app.use(cors(...)) in express.js.
app.add_middleware(GZipMiddleware)
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"],
    )


STRICT_CSP = (
    "default-src 'self'; img-src 'self' data:; frame-ancestors 'none'; "
    "base-uri 'self'; form-action 'self'"
)
# [ADVANCED] The in-browser JSX demo (/react-jsx) runs code that Babel compiled a moment ago in
# the page, as blob: URLs. A strict policy blocks that, which is the point of a CSP: code that
# was not on the server cannot run. So the demo needs `blob:` in script-src. One more reason
# compiling in the browser is for teaching only; /react (htm) runs under STRICT_CSP.
JSX_DEMO_CSP = STRICT_CSP + "; script-src 'self' blob:"


def is_jsx_demo(request: Request) -> bool:
    path = request.url.path
    return path == "/react-jsx" or path.startswith("/react-jsx/")


# [ADVANCED] A small stand-in for helmet: a few security headers on every response.
# The CSP only allows files from this server, which is why htmx.min.js is vendored in
# app/static/ (no CDN), and why the templates use no inline <script> or style="" attributes.
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        JSX_DEMO_CSP if is_jsx_demo(request) else STRICT_CSP
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    return response


# [BEGINNER] Development only: "no-cache" makes the browser ask the server about every static
# file on every page load. Without it the browser may reuse an old copy, so you save a .js/.jsx/
# .css file, reload, and still see the old version. An unchanged file costs only a tiny
# "304 Not Modified" answer (StaticFiles compares the ETag), so reloads stay fast.
# [ADVANCED] "no-cache" does not mean "do not store"; it means "check before using" (that is
# "no-store"). In production this middleware does nothing and the browser's normal caching applies.
@app.middleware("http")
async def static_files_revalidate(request: Request, call_next):
    response = await call_next(request)
    if not settings.is_production and request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache"
    return response


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# [BEGINNER] app.include_router is app.use('/', userRoutes) in express.js.
app.include_router(api_users.router)
app.include_router(api_auth.router)
# The HTML pages (Chapter 3 had these in a separate React client).
app.include_router(pages.router)
# The same pages as a React client under /react (app/static/react/), for comparison,
# and in real JSX compiled in the browser under /react-jsx (app/static/react-jsx/, demo only).
app.include_router(react_client.router)


# --- Error handlers -----------------------------------------------------------------------
# [BEGINNER] Chapter 3 had ONE error handler at the end of express.js. FastAPI registers one
# handler per exception type. All of them answer {"error": "..."} like the Node server, so the
# same client code (and api.http) works with both. FastAPI's default is {"detail": ...}.

def is_api(request: Request) -> bool:
    return request.url.path.startswith("/api")


@app.exception_handler(UserInputError)
async def user_input_error(request: Request, exc: UserInputError):
    return JSONResponse({"error": exc.message}, status_code=400)


# [ADVANCED] FastAPI answers 422 when the body does not match the model. Chapter 3 answered
# 400 for validation errors, so we keep 400 (both are common; 422 is FastAPI's convention).
@app.exception_handler(RequestValidationError)
async def request_validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse({"error": validation_message(exc.errors())}, status_code=400)


@app.exception_handler(pages.SigninRequired)
async def signin_required(request: Request, exc: pages.SigninRequired):
    return pages.signin_required_response(request, exc)


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    # [BEGINNER] A page URL that matches no route gets the HTML "Page not found" page
    # (Chapter 3: React Router's path="*" → <NotFound />); an /api URL gets JSON.
    if exc.status_code == 404 and not is_api(request):
        return pages.templates.TemplateResponse(request, "not_found.html", status_code=404)
    if exc.status_code == 404 and exc.detail == "Not Found":
        # No route matched (FastAPI's own 404), like the app.use('/api', ...) catch-all.
        message = f"Route not found: {request.method} {request.url.path}"
    else:
        message = exc.detail
    return JSONResponse({"error": message}, status_code=exc.status_code, headers=exc.headers)


# [ADVANCED] Anything else is a bug or an outage: log the details here, send no stack trace.
@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    if not is_api(request):
        return PlainTextResponse("Internal server error", status_code=500)
    return JSONResponse({"error": "Internal server error"}, status_code=500)
