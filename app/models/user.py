"""The User document and the request/response shapes (Chapter 3: server/models/user.model.js)."""
import hashlib
import hmac
import re
import secrets
from datetime import UTC, datetime
from typing import Annotated

from beanie import Document, Indexed
from pydantic import AfterValidator, BaseModel, ConfigDict, Field
from pydantic_core import PydanticCustomError

# --- Password hashing ----------------------------------------------------------------------
# [ADVANCED] Same algorithm and parameters as Chapter 3's crypto.scryptSync(password, salt, 64):
# N=16384, r=8, p=1, 64-byte key, and the hex salt STRING (not its bytes) as the salt. So a
# user who signed up on the Node server can sign in here if both use the same database.
# scrypt is a password hash: deliberately slow and memory-hungry, unlike SHA1 in the book.


def make_salt() -> str:
    # [BEGINNER] secrets is the standard library module for security-sensitive random values
    # (Node: crypto.randomBytes(16).toString('hex')). Never use the `random` module for this.
    return secrets.token_hex(16)


def encrypt_password(password: str, salt: str) -> str:
    if not password:
        return ""
    return hashlib.scrypt(
        password.encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=64
    ).hex()


# --- Field checks, shared by sign-up and update --------------------------------------------
# [BEGINNER] Annotated[str, AfterValidator(check)] = "a str, then run check() on it". The same
# type can be reused in several models, like a Mongoose schema path's options.
# [ADVANCED] PydanticCustomError(type, message) puts our exact text in the error's "msg".
# A plain ValueError would be reported as "Value error, Name is required."

EMAIL_PATTERN = re.compile(r".+@.+\..+")  # the same pattern as user.model.js


def check_name(value: str) -> str:
    if not value:
        raise PydanticCustomError("name", "Name is required.")
    return value


def check_email(value: str) -> str:
    if not value:
        raise PydanticCustomError("email", "Email is required.")
    if not EMAIL_PATTERN.fullmatch(value):
        raise PydanticCustomError("email", "Please fill a valid email address.")
    return value


def check_password(value: str) -> str:
    if len(value) < 6:
        raise PydanticCustomError("password", "Password must be at least 6 characters.")
    return value


Name = Annotated[str, AfterValidator(check_name)]
Email = Annotated[str, AfterValidator(check_email)]
Password = Annotated[str, AfterValidator(check_password)]


# --- The document stored in MongoDB --------------------------------------------------------
# [BEGINNER] A Beanie Document is a Pydantic model that is also a MongoDB collection.
# Each annotated attribute is a field; `= ...` gives a default. Beanie adds `id` (MongoDB _id).
class User(Document):
    name: str
    # [ADVANCED] As in Mongoose, "unique" is an index, not a validator: MongoDB rejects the
    # second insert with error 11000 (DuplicateKeyError), and errors.py turns it into
    # "Email already exists". Indexes are created by init_beanie at startup.
    email: Annotated[str, Indexed(unique=True)]
    hashed_password: str = ""
    salt: str = ""
    updated: datetime | None = None
    # [BEGINNER] default_factory runs for each new document (default=datetime.now(UTC) would
    # run ONCE at import, giving every user the same date). Mongoose: default: Date.now.
    created: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "users"  # collection name (Mongoose pluralised 'User' to 'users' itself)

    # [BEGINNER] Chapter 3 used a `password` virtual whose setter hashed the value. A plain
    # method says what it does; Python has setters too (@property), but they hide the work.
    def set_password(self, password: str) -> None:
        self.salt = make_salt()
        self.hashed_password = encrypt_password(password, self.salt)

    def authenticate(self, plain_text: str) -> bool:
        if not plain_text or not self.hashed_password:
            return False
        # [ADVANCED] compare_digest takes the same time wherever the strings differ, so the hash
        # cannot be guessed byte by byte from response times (Node: crypto.timingSafeEqual).
        return hmac.compare_digest(encrypt_password(plain_text, self.salt), self.hashed_password)


# --- What the API accepts and returns ------------------------------------------------------
class UserCreate(BaseModel):
    """Sign-up body: POST /api/users."""
    # [BEGINNER] str_strip_whitespace trims every string (Mongoose: trim: true).
    model_config = ConfigDict(str_strip_whitespace=True)
    name: Name
    email: Email
    password: Password


class UserUpdate(BaseModel):
    """PATCH /api/users/{id}: every field optional; only these three can change.

    [ADVANCED] Pydantic drops unknown fields (salt, created, hashed_password ...) by default,
    which closes the mass-assignment hole of the book's _.extend(user, req.body), the same
    job as UPDATABLE_FIELDS in user.controller.js.
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    name: Name | None = None
    email: Email | None = None
    password: Password | None = None


class UserOut(BaseModel):
    """What leaves the server. No hashed_password or salt.

    [BEGINNER] Chapter 3 deleted the secret fields in a toJSON transform. Here each route
    declares response_model=UserOut, and FastAPI sends only the fields listed here.
    """
    # [ADVANCED] alias="_id" keeps the Node server's JSON key; validate_by_name lets Python
    # code still write UserOut(id=...).
    model_config = ConfigDict(validate_by_name=True)
    id: str = Field(alias="_id")
    name: str
    email: str
    created: datetime
    updated: datetime | None = None

    @classmethod
    def from_user(cls, user: User) -> "UserOut":
        return cls(id=str(user.id), name=user.name, email=user.email,
                   created=user.created, updated=user.updated)
