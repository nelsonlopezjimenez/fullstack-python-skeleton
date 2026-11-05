"""The JSON API against a real MongoDB (Chapter 3: tests/4-api.test.js and api.http)."""
from conftest import needs_mongo

# [BEGINNER] pytestmark applies the marker to every test in this file.
pytestmark = needs_mongo


def bearer(user):
    return {"Authorization": f"Bearer {user['token']}"}


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_signup_and_duplicate_email(client, new_user):
    user = new_user()
    response = client.post("/api/users", json={"name": "Ann", "email": user["email"], "password": "secret1"})
    assert response.status_code == 400
    assert response.json() == {"error": "Email already exists"}


def test_signup_validation_lists_every_problem(client):
    response = client.post("/api/users", json={"name": "", "email": "not-an-email", "password": "1"})
    assert response.status_code == 400
    assert response.json()["error"] == (
        "Name is required. Please fill a valid email address. "
        "Password must be at least 6 characters."
    )


def test_signin_returns_token_user_and_httponly_cookie(client, new_user):
    user = new_user()
    response = client.post("/api/auth/sessions", json={"email": user["email"], "password": "secret1"})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"token", "user"}
    assert set(body["user"]) == {"_id", "name", "email"}
    cookie = response.headers["set-cookie"].lower()
    assert cookie.startswith("t=") and "httponly" in cookie and "samesite=strict" in cookie


def test_signin_failures(client, new_user):
    user = new_user()
    wrong = client.post("/api/auth/sessions", json={"email": user["email"], "password": "nope!!"})
    unknown = client.post("/api/auth/sessions", json={"email": "who@test.io", "password": "nope!!"})
    empty = client.post("/api/auth/sessions")
    # Same answer for a wrong password and an unknown email (no account enumeration).
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json() == {"error": "Email and password don't match."}
    assert (empty.status_code, empty.json()) == (400, {"error": "Email and password are required"})


def test_list_never_sends_password_fields(client, new_user):
    new_user()
    users = client.get("/api/users").json()
    assert users
    for user in users:
        assert set(user) == {"_id", "name", "email", "created", "updated"}


def test_read_needs_a_token(client, new_user):
    user = new_user()
    assert client.get(f"/api/users/{user['id']}").status_code == 401
    assert client.get(f"/api/users/{user['id']}", headers={"Authorization": "Bearer junk"}).status_code == 401
    response = client.get(f"/api/users/{user['id']}", headers=bearer(user))
    assert response.status_code == 200
    assert response.json()["email"] == user["email"]


def test_the_cookie_works_too(client, new_user):
    user = new_user()
    client.cookies.set("t", user["token"])
    assert client.get(f"/api/users/{user['id']}").status_code == 200


def test_token_is_checked_before_the_database(client):
    # Without a token, an unknown id and a malformed id both give 401: nothing is revealed.
    assert client.get("/api/users/000000000000000000000000").status_code == 401
    assert client.get("/api/users/not-an-id").status_code == 401


def test_unknown_and_invalid_ids(client, new_user):
    user = new_user()
    missing = client.get("/api/users/000000000000000000000000", headers=bearer(user))
    invalid = client.get("/api/users/not-an-id", headers=bearer(user))
    assert (missing.status_code, missing.json()) == (404, {"error": "User not found"})
    assert (invalid.status_code, invalid.json()) == (400, {"error": "Invalid _id: not-an-id"})


def test_patch_changes_only_allowed_fields(client, new_user):
    user = new_user()
    response = client.patch(
        f"/api/users/{user['id']}", headers=bearer(user),
        json={"name": "Ann Updated", "salt": "ignored", "created": "2000-01-01"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Ann Updated"
    assert body["email"] == user["email"]  # not sent, not changed
    assert body["updated"] is not None
    assert not body["created"].startswith("2000")


def test_patch_password_then_sign_in_with_it(client, new_user):
    user = new_user()
    client.patch(f"/api/users/{user['id']}", headers=bearer(user), json={"password": "newpass1"})
    old = client.post("/api/auth/sessions", json={"email": user["email"], "password": "secret1"})
    new = client.post("/api/auth/sessions", json={"email": user["email"], "password": "newpass1"})
    assert (old.status_code, new.status_code) == (401, 200)


def test_patch_validation_and_duplicate(client, new_user):
    ann, bob = new_user("Ann"), new_user("Bob")
    short = client.patch(f"/api/users/{ann['id']}", headers=bearer(ann), json={"password": "1"})
    taken = client.patch(f"/api/users/{ann['id']}", headers=bearer(ann), json={"email": bob["email"]})
    assert short.json() == {"error": "Password must be at least 6 characters."}
    assert (taken.status_code, taken.json()) == (400, {"error": "Email already exists"})


def test_only_the_owner_can_change_or_delete(client, new_user):
    ann, bob = new_user("Ann"), new_user("Bob")
    patch = client.patch(f"/api/users/{bob['id']}", headers=bearer(ann), json={"name": "hacked"})
    delete = client.delete(f"/api/users/{bob['id']}", headers=bearer(ann))
    assert patch.status_code == delete.status_code == 403


def test_delete_own_account(client, new_user):
    user = new_user()
    response = client.delete(f"/api/users/{user['id']}", headers=bearer(user))
    assert response.status_code == 200
    assert response.json()["_id"] == user["id"]
    assert client.get(f"/api/users/{user['id']}", headers=bearer(user)).status_code == 404


def test_signout_clears_the_cookie(client):
    response = client.delete("/api/auth/sessions")
    assert response.json() == {"message": "signed out"}
    assert response.headers["set-cookie"].startswith('t="";')


def test_unknown_api_route_is_json(client):
    response = client.get("/api/nope")
    assert (response.status_code, response.json()) == (404, {"error": "Route not found: GET /api/nope"})


def test_security_headers(client):
    headers = client.get("/api/health").headers
    assert "default-src 'self'" in headers["content-security-policy"]
    assert headers["x-content-type-options"] == "nosniff"
