"""User operations shared by the JSON API (routes/api_users.py) and the HTML pages (routes/pages.py).

[BEGINNER] In Chapter 3 only the API touched the database, and React called the API. Here the
pages are rendered on the server, so they call these functions directly instead of making an
HTTP request to our own API. The rules (validation, duplicate email, which fields may change)
live in ONE place.
"""
from datetime import UTC, datetime

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.errors import UserInputError, duplicate_key_message
from app.models.user import User, UserCreate, UserUpdate


async def save(user: User) -> User:
    # [BEGINNER] try/except is Python's try/catch. Chapter 3 let Express 5 send the rejected
    # promise to the central error handler; here we turn the one error we expect into a 400.
    try:
        await user.save()
    except DuplicateKeyError as err:
        raise UserInputError(duplicate_key_message(err)) from None
    return user


async def create_user(data: UserCreate) -> User:
    user = User(name=data.name, email=data.email)
    user.set_password(data.password)
    return await save(user)


async def find_user(user_id: str) -> User | None:
    """None when no such user. An id that is not an ObjectId raises UserInputError (→ 400)."""
    # [BEGINNER] Mongoose raised a CastError for "not-an-id"; we check it ourselves.
    if not ObjectId.is_valid(user_id):
        raise UserInputError(f"Invalid _id: {user_id}")
    return await User.get(ObjectId(user_id))


async def update_user(user: User, data: UserUpdate) -> User:
    # [BEGINNER] exclude_unset=True keeps only the fields the client actually SENT, so a PATCH
    # with just a new name does not touch the email (Chapter 3: Object.fromEntries + filter).
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    password = changes.pop("password", None)
    for field, value in changes.items():
        setattr(user, field, value)  # [BEGINNER] setattr(user, "name", v) is user.name = v
    if password:
        user.set_password(password)
    user.updated = datetime.now(UTC)
    return await save(user)


async def list_users() -> list[User]:
    return await User.find_all().to_list()
