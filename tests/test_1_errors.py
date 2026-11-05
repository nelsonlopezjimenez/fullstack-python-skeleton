"""app/errors.py (Chapter 3: tests/1-dbErrorHandler.test.js). No database needed."""
import pytest

from app.errors import UserInputError, duplicate_key_message, parse, validation_message
from app.models.user import UserCreate


class FakeDuplicateKeyError:
    """Only the attribute duplicate_key_message reads; a real DuplicateKeyError needs a server."""
    def __init__(self, details):
        self.details = details


def test_duplicate_key_message_names_the_field():
    err = FakeDuplicateKeyError({"code": 11000, "keyValue": {"email": "a@b.io"}})
    assert duplicate_key_message(err) == "Email already exists"


def test_duplicate_key_message_without_details():
    assert duplicate_key_message(FakeDuplicateKeyError(None)) == "Unique field already exists"


def test_validation_message_joins_every_problem():
    # [BEGINNER] pytest.raises checks that the block raises this exception (Jest: toThrow).
    with pytest.raises(UserInputError) as caught:
        parse(UserCreate, {"name": "", "email": "nope", "password": "1"})
    assert caught.value.message == (
        "Name is required. Please fill a valid email address. "
        "Password must be at least 6 characters."
    )


def test_missing_fields_are_named():
    with pytest.raises(UserInputError) as caught:
        parse(UserCreate, {})
    assert caught.value.message == "Name is required. Email is required. Password is required."


def test_whitespace_is_trimmed_before_checking():
    with pytest.raises(UserInputError, match="Name is required."):
        parse(UserCreate, {"name": "   ", "email": "a@b.io", "password": "secret1"})


def test_unknown_error_types_keep_their_message():
    errors = [{"type": "string_type", "loc": ("body", "name"), "msg": "Input should be a valid string"}]
    assert validation_message(errors) == "Input should be a valid string"
