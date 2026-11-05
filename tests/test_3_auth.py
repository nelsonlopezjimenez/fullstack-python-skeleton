"""Passwords, tokens and has_authorization (Chapter 3: tests/3-hasAuthorization.test.js).

No database needed: User objects are built in memory and never saved.
"""
import asyncio

import pytest
from beanie import PydanticObjectId
from fastapi import HTTPException

from app import auth
from app.models.user import User, encrypt_password

# Computed with Node: crypto.scryptSync('secret1', 'abc123', 64).toString('hex')
NODE_SCRYPT_SECRET1_ABC123 = (
    "fb84bd345f24d08f2c84fbd8423e7fd51e2084614f5eb36272be224482e79051"
    "6436b6fd87a2d7646df203738641a411efede88528497f424d118a79e7843950"
)


def make_user(name="Ann") -> User:
    # [ADVANCED] User(...) refuses to build before init_beanie() has connected the model to a
    # database. model_construct() builds the object without that check (and without
    # validation), which is enough for code that never touches MongoDB.
    user = User.model_construct(id=PydanticObjectId(), name=name, email=f"{name}@test.io")
    user.set_password("secret1")
    return user


def test_hash_matches_node_chapter_3():
    assert encrypt_password("secret1", "abc123") == NODE_SCRYPT_SECRET1_ABC123


def test_authenticate():
    user = make_user()
    assert user.authenticate("secret1")
    assert not user.authenticate("secret2")
    assert not user.authenticate("")


def test_every_user_gets_a_new_salt():
    assert make_user().salt != make_user().salt


def test_token_round_trip():
    user = make_user()
    payload = auth.decode_token(auth.create_token(user))
    assert payload["_id"] == str(user.id)
    assert "exp" in payload


def test_tampered_token_is_rejected():
    token = auth.create_token(make_user())
    assert auth.decode_token(token[:-2] + "xx") is None
    assert auth.decode_token("not-a-token") is None


# [BEGINNER] has_authorization is an `async def`: asyncio.run() runs it to the end and returns
# its result (or raises its exception), so a plain test function can call it.
def test_owner_is_authorized():
    user = make_user()
    assert asyncio.run(auth.has_authorization(profile=user, auth={"_id": str(user.id)})) is user


def test_someone_else_gets_403():
    ann, bob = make_user("Ann"), make_user("Bob")
    with pytest.raises(HTTPException) as caught:
        asyncio.run(auth.has_authorization(profile=ann, auth={"_id": str(bob.id)}))
    assert caught.value.status_code == 403
    assert caught.value.detail == "User is not authorized"
