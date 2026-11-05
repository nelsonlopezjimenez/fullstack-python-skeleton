"""/api/auth/sessions (Chapter 3: server/routes/auth.routes.js).

    POST   /api/auth/sessions  → create a session  (sign in)
    DELETE /api/auth/sessions  → end the session   (sign out)

Same REST naming as Chapter 3 (signing out is never a GET).
"""
import logging

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

from app import auth

logger = logging.getLogger("app.auth")
router = APIRouter(prefix="/api/auth", tags=["auth"])


# [BEGINNER] Defaults of "" make both fields optional, so this function can answer the
# friendly "Email and password are required" itself instead of a validation error.
class SigninBody(BaseModel):
    email: str = ""
    password: str = ""


@router.post("/sessions")
async def signin(response: Response, body: SigninBody | None = None):
    # [BEGINNER] `body or SigninBody()`: no body at all counts as empty fields (Node: ?? {}).
    body = body or SigninBody()
    if not body.email or not body.password:
        raise HTTPException(400, "Email and password are required")

    user = await auth.signin(body.email.strip(), body.password)
    if user is None:
        raise HTTPException(401, "Email and password don't match.")

    token = auth.create_token(user)
    logger.debug("JWT issued for %s: %s", user.email, token)  # development: paste it at jwt.io
    # [BEGINNER] `response: Response` is the response FastAPI will send; setting a cookie on it
    # works like res.cookie(...) in Express, and the returned dict becomes the JSON body.
    auth.set_auth_cookie(response, token)
    # Same shape as Chapter 3: the token in the body too, for API clients that use the header.
    return {"token": token, "user": {"_id": str(user.id), "name": user.name, "email": user.email}}


@router.delete("/sessions")
async def signout(response: Response):
    auth.clear_auth_cookie(response)
    return {"message": "signed out"}
