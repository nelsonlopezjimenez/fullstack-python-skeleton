"""HTML pages (Chapter 3: the whole React client, MainRouter.jsx + the page components).

    GET  /                     Home
    GET  /users                all users                      (public)
    GET  /signup, POST /signup sign-up form
    GET  /signin, POST /signin sign-in form
    POST /signout              sign out
    GET  /users/{id}           profile                        (signed in)
    GET  /users/{id}/edit      edit form                      (signed in + owner)
    PATCH  /users/{id}         save the edit form (HTMX)      (signed in + owner)
    DELETE /users/{id}         delete the account (HTMX)      (signed in + owner)

[BEGINNER] How HTMX works here: a form with hx-post="/signin" sends its fields with fetch and
puts the HTML that comes back into the element named by hx-target (the error box). On success
the server answers with an "HX-Redirect: /" header instead, and HTMX loads that page. The
server returns HTML, never JSON, so the browser needs no JavaScript of our own.
"""
from urllib.parse import quote

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app import auth, user_service
from app.config import BASE_DIR
from app.errors import UserInputError, parse
from app.models.user import UserCreate, UserUpdate


def template_context(request: Request) -> dict:
    """Variables every template can use (the Menu needs them on every page)."""
    # [BEGINNER] Chapter 3's Menu asked auth-helper.js for the token in sessionStorage. Here the
    # token is in the cookie; decoding it needs no database call (it only holds the user id).
    token = request.cookies.get(auth.COOKIE_NAME)
    return {"auth": auth.decode_token(token) if token else None, "path": request.url.path}


# [BEGINNER] Jinja2 is the template engine: {{ value }} prints a value, {% if %} / {% for %} are
# control flow, {% extends %} / {% block %} build pages from a shared layout.
# [ADVANCED] Autoescaping is on for .html files: a user named <script>alert(1)</script> is
# printed as text, not run. React gave the same protection for {value} in JSX.
templates = Jinja2Templates(directory=BASE_DIR / "templates", context_processors=[template_context])

router = APIRouter(include_in_schema=False)


# --- Helpers -------------------------------------------------------------------------------
def is_htmx(request: Request) -> bool:
    return request.headers.get("hx-request") == "true"


def redirect(request: Request, url: str) -> Response:
    """Go to another page. HTMX requests need the HX-Redirect header instead of a 303."""
    # [ADVANCED] A normal 303 would be FOLLOWED by fetch inside HTMX, and the whole new page
    # would be swapped into the small error box. HX-Redirect tells HTMX to change the address.
    if is_htmx(request):
        return Response(status_code=200, headers={"HX-Redirect": url})
    return RedirectResponse(url, status_code=303)


def form_error(request: Request, message: str, status_code: int = 400) -> Response:
    """The error fragment that HTMX puts in <div id="form-error"> (Chapter 3: FormError.jsx)."""
    return templates.TemplateResponse(
        request, "_form_error.html", {"message": message}, status_code=status_code
    )


def safe_next(url: str | None) -> str:
    # [ADVANCED] Only redirect to our own pages. "//evil.example" is a full URL to another
    # site (an "open redirect"), so it must start with exactly one slash.
    if url and url.startswith("/") and not url.startswith("//"):
        return url
    return "/"


class SigninRequired(Exception):
    """Raised by page_user; main.py turns it into a redirect to /signin?next=..."""

    def __init__(self, next_url: str):
        self.next_url = next_url


async def page_user(request: Request) -> dict:
    """The signed-in user's token payload, or off to the sign-in page.

    [BEGINNER] Chapter 3's <PrivateRoute> did this in the browser: no token → <Navigate
    to="/signin" state={{ from: location }}>. Here the server decides before it renders anything.
    """
    token = auth.token_from_request(request)
    payload = auth.decode_token(token) if token else None
    if payload is None:
        raise SigninRequired(request.url.path)
    return payload


def signin_required_response(request: Request, exc: SigninRequired) -> Response:
    return redirect(request, f"/signin?next={quote(exc.next_url)}")


# --- Public pages --------------------------------------------------------------------------
@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "home.html")


@router.get("/users")
async def users(request: Request):
    return templates.TemplateResponse(
        request, "users.html", {"users": await user_service.list_users()}
    )


@router.get("/signup")
async def signup_form(request: Request):
    return templates.TemplateResponse(request, "signup.html")


@router.post("/signup")
async def signup(request: Request):
    # [BEGINNER] await request.form() reads the fields of a submitted HTML form
    # (Content-Type application/x-www-form-urlencoded; parsing needs python-multipart).
    form = dict(await request.form())
    try:
        # The SAME UserCreate model as POST /api/users, so the rules and messages match.
        await user_service.create_user(parse(UserCreate, form))
    except UserInputError as err:
        return form_error(request, err.message)
    # Chapter 3 showed a "New account successfully created" dialog with a Sign in button.
    return redirect(request, "/signin?created=1")


@router.get("/signin")
async def signin_form(request: Request, next: str = "/", created: bool = False):
    return templates.TemplateResponse(
        request, "signin.html", {"next": safe_next(next), "created": created}
    )


@router.post("/signin")
async def signin(request: Request):
    form = await request.form()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", ""))
    if not email or not password:
        return form_error(request, "Email and password are required")
    user = await auth.signin(email, password)
    if user is None:
        return form_error(request, "Email and password don't match.", status_code=401)
    response = redirect(request, safe_next(str(form.get("next", "/"))))
    auth.set_auth_cookie(response, auth.create_token(user))
    return response


@router.post("/signout")
async def signout(request: Request):
    response = redirect(request, "/")
    auth.clear_auth_cookie(response)
    return response


# --- Signed-in pages -----------------------------------------------------------------------
async def load_user_or_404(request: Request, user_id: str):
    try:
        user = await user_service.find_user(user_id)
    except UserInputError:  # not an ObjectId: for a page that is simply "no such page"
        user = None
    if user is None:
        return None, templates.TemplateResponse(request, "not_found.html", status_code=404)
    return user, None


@router.get("/users/{user_id}")
async def profile(request: Request, user_id: str, me: dict = Depends(page_user)):
    user, not_found = await load_user_or_404(request, user_id)
    if not_found:
        return not_found
    return templates.TemplateResponse(
        request, "profile.html", {"user": user, "is_owner": me["_id"] == str(user.id)}
    )


@router.get("/users/{user_id}/edit")
async def edit_form(request: Request, user_id: str, me: dict = Depends(page_user)):
    if me["_id"] != user_id:
        return redirect(request, f"/users/{user_id}")  # only your own profile can be edited
    user, not_found = await load_user_or_404(request, user_id)
    if not_found:
        return not_found
    return templates.TemplateResponse(request, "edit_profile.html", {"user": user})


# [BEGINNER] HTML forms can only send GET and POST. HTMX can send any method, so the edit form
# uses hx-patch and the delete button hx-delete: the same verbs as the JSON API.
@router.patch("/users/{user_id}")
async def edit(request: Request, user_id: str, me: dict = Depends(page_user)):
    if me["_id"] != user_id:
        return form_error(request, "User is not authorized", status_code=403)
    user, not_found = await load_user_or_404(request, user_id)
    if not_found:
        return form_error(request, "User not found", status_code=404)
    # [BEGINNER] A dict comprehension: keep only the fields that are not blank, so an empty
    # password box means "keep my password" (the API gets the same effect by leaving it out).
    form = {key: value for key, value in (await request.form()).items() if str(value).strip()}
    try:
        await user_service.update_user(user, parse(UserUpdate, form))
    except UserInputError as err:
        return form_error(request, err.message)
    return redirect(request, f"/users/{user_id}")


@router.delete("/users/{user_id}")
async def delete(request: Request, user_id: str, me: dict = Depends(page_user)):
    if me["_id"] != user_id:
        return form_error(request, "User is not authorized", status_code=403)
    user, not_found = await load_user_or_404(request, user_id)
    if not_found:
        return form_error(request, "User not found", status_code=404)
    await user.delete()
    # Chapter 3's DeleteUser.jsx signed out and went home after deleting the account.
    response = redirect(request, "/")
    auth.clear_auth_cookie(response)
    return response
