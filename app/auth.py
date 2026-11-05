"""Tokens and the sign-in checks (Chapter 3: server/controllers/auth.controller.js).

[BEGINNER] Express middleware (req, res, next) becomes a FastAPI *dependency*: a function that
a route asks for with Depends(...). It either returns a value (the decoded token, the user) or
raises an HTTPException, which stops the request, like calling next(err).
"""
import logging
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, Request, Response

from app import user_service
from app.config import settings
from app.models.user import User

logger = logging.getLogger("app.auth")

COOKIE_NAME = "t"  # same name as Chapter 3


# --- Tokens --------------------------------------------------------------------------------
def create_token(user: User) -> str:
    # [BEGINNER] The payload only holds the user id (never the password). It is signed, not
    # encrypted: paste a token at https://jwt.io to see that anyone can READ it.
    payload = {
        "_id": str(user.id),
        "exp": datetime.now(UTC) + timedelta(seconds=settings.jwt_expires_in_seconds),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    """The payload, or None when the token is missing, tampered with or expired."""
    try:
        # [ADVANCED] algorithms=[...] is required, as in express-jwt: never let the token's
        # own header choose the algorithm (the "alg: none" family of attacks).
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:  # covers ExpiredSignatureError, bad signature, garbage
        return None


def token_from_request(request: Request) -> str | None:
    # [ADVANCED] Chapter 3's API read only "Authorization: Bearer ...", because the React
    # client stored the token itself. Here the HTML pages have no JavaScript to do that: the
    # browser sends the httpOnly cookie on its own. So we accept both: the header for API
    # clients (api.http, scripts, a future React client) and the cookie for the pages.
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return request.cookies.get(COOKIE_NAME)


# --- Cookie --------------------------------------------------------------------------------
def set_auth_cookie(response: Response, token: str) -> None:
    # [ADVANCED] httponly: page JavaScript cannot read it (limits XSS damage).
    # samesite="strict": the browser does not send it on requests started by other sites,
    # which is our CSRF protection for the forms. secure: HTTPS only, in production.
    response.set_cookie(
        COOKIE_NAME, token, max_age=settings.jwt_expires_in_seconds,
        httponly=True, samesite="strict", secure=settings.is_production,
    )


def clear_auth_cookie(response: Response) -> None:
    # [BEGINNER] A cookie is only removed when the same options are given.
    response.delete_cookie(
        COOKIE_NAME, httponly=True, samesite="strict", secure=settings.is_production
    )


# --- Dependencies (the middleware) ---------------------------------------------------------
async def require_signin(request: Request) -> dict:
    """401 unless the request carries a valid token. Returns the payload (Chapter 3: req.auth)."""
    token = token_from_request(request)
    if not token:
        raise HTTPException(401, "UnauthorizedError: No authorization token was found")
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(401, "UnauthorizedError: invalid token")
    return payload


# [ADVANCED] user_by_id DEPENDS ON require_signin, so FastAPI always checks the token before
# it queries the database. Chapter 3 had to move userByID out of router.param() to get this
# order (an unauthenticated request could tell which ids exist: 404 vs 401).
# `user_id` is filled from the {user_id} part of the route path.
async def user_by_id(user_id: str, auth: dict = Depends(require_signin)) -> User:
    user = await user_service.find_user(user_id)
    if user is None:
        raise HTTPException(404, "User not found")
    return user


# [BEGINNER] FastAPI runs require_signin only ONCE per request even though two dependencies
# ask for it: the result is cached for the request.
async def has_authorization(
    profile: User = Depends(user_by_id), auth: dict = Depends(require_signin)
) -> User:
    """403 unless the signed-in user is the profile in the URL. Returns that user."""
    if str(profile.id) != auth.get("_id"):
        raise HTTPException(403, "User is not authorized")
    return profile


async def signin(email: str, password: str) -> User | None:
    """The user when email and password match, else None."""
    user = await User.find_one(User.email == email)
    # [ADVANCED] One answer for "no such email" and "wrong password" (no account enumeration).
    if user is None or not user.authenticate(password):
        return None
    return user
