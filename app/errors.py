"""Turn validation and database errors into one readable message.

Chapter 3: server/helpers/dbErrorHandler.js
"""
from pydantic import ValidationError


class UserInputError(Exception):
    """The client sent something we refuse (bad field, duplicate email). Becomes a 400.

    [BEGINNER] A custom exception class lets the JSON API and the HTML pages share the same
    checks: the API turns it into {"error": ...}, a page shows it in the form.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def validation_message(errors: list[dict]) -> str:
    """Join every validation error into one sentence, like getErrorMessage for a ValidationError.

    `errors` is ValidationError.errors() or RequestValidationError.errors(): a list of dicts
    with "type", "loc" (where the error is, e.g. ("body", "email")) and "msg".
    """
    messages = []
    for error in errors:
        field = error["loc"][-1] if error["loc"] else "body"
        if error["type"] == "missing":
            # [BEGINNER] f-strings: the {...} parts are evaluated and inserted into the text,
            # like `${...}` in a JavaScript template literal.
            messages.append(
                f"{str(field).capitalize()} is required." if field != "body"
                else "Request body is required."
            )
        elif error["type"] == "json_invalid":
            messages.append("Malformed JSON in request body.")
        else:
            # Our own checks (see models/user.py) put the finished message in "msg".
            messages.append(error["msg"])
    return " ".join(messages)


def parse(model, data: dict):
    """Validate `data` with a Pydantic model; raise UserInputError with every message."""
    try:
        return model.model_validate(data)
    except ValidationError as err:
        # [ADVANCED] `from None` hides the original traceback chain: the message is all
        # the caller needs, and the 400 is not a server bug.
        raise UserInputError(validation_message(err.errors())) from None


def duplicate_key_message(err) -> str:
    """'Email already exists' from PyMongo's DuplicateKeyError (MongoDB error code 11000)."""
    # [BEGINNER] `or {}` is the Python version of `?? {}` for a missing details dict.
    key_value = (err.details or {}).get("keyValue") or {}
    field = next(iter(key_value), None)  # first key, or None
    if field is None:
        return "Unique field already exists"
    return f"{field.capitalize()} already exists"
