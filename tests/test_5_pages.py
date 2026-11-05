"""The HTML pages, as HTMX calls them (Chapter 3 tested the React client with Vitest).

[BEGINNER] HTMX marks its requests with the header HX-Request: true. Sending that header here
makes the server answer exactly as it does in the browser (HX-Redirect, error fragments).
"""
import re

from conftest import needs_mongo

pytestmark = needs_mongo

HTMX = {"HX-Request": "true"}


def sign_in_browser(client, user):
    response = client.post("/signin", data={"email": user["email"], "password": user["password"]}, headers=HTMX)
    assert response.headers["HX-Redirect"] == "/"


def test_public_pages_render(client):
    for path, text in [("/", "Home Page"), ("/users", "All Users"), ("/signup", "Sign Up"), ("/signin", "Sign In")]:
        response = client.get(path)
        assert response.status_code == 200 and text in response.text, path


def test_menu_changes_after_sign_in(client, new_user):
    user = new_user()
    assert "My Profile" not in client.get("/").text
    sign_in_browser(client, user)
    assert f'href="/users/{user["id"]}"' in client.get("/").text


def test_signup_errors_come_back_as_a_fragment(client):
    response = client.post("/signup", data={"name": "", "email": "x", "password": "1"}, headers=HTMX)
    assert response.status_code == 400
    assert response.text.strip().startswith('<p class="error"')
    assert "<html" not in response.text  # a fragment, not a whole page


def test_signup_success_redirects_to_signin(client):
    data = {"name": "Page User", "email": "page.user@test.io", "password": "secret1"}
    response = client.post("/signup", data=data, headers=HTMX)
    assert response.headers["HX-Redirect"] == "/signin?created=1"
    assert "successfully created" in client.get("/signin?created=1").text


def test_names_are_escaped(client):
    data = {"name": "<script>alert(1)</script>", "email": "xss@test.io", "password": "secret1"}
    client.post("/signup", data=data, headers=HTMX)
    page = client.get("/users").text
    assert "&lt;script&gt;" in page and "<script>alert" not in page


def test_protected_page_redirects_to_signin_with_next(client, new_user):
    user = new_user()
    normal = client.get(f"/users/{user['id']}", follow_redirects=False)
    assert normal.status_code == 303
    assert normal.headers["location"] == f"/signin?next=/users/{user['id']}"
    htmx = client.get(f"/users/{user['id']}", headers=HTMX)
    assert htmx.headers["HX-Redirect"] == f"/signin?next=/users/{user['id']}"


def test_signin_goes_back_to_next_but_never_off_site(client, new_user):
    user = new_user()
    data = {"email": user["email"], "password": "secret1"}
    to_profile = client.post("/signin", data={**data, "next": f"/users/{user['id']}"}, headers=HTMX)
    off_site = client.post("/signin", data={**data, "next": "//evil.example"}, headers=HTMX)
    assert to_profile.headers["HX-Redirect"] == f"/users/{user['id']}"
    assert off_site.headers["HX-Redirect"] == "/"


def test_owner_sees_edit_and_delete_others_do_not(client, new_user):
    ann, bob = new_user("Ann"), new_user("Bob")
    sign_in_browser(client, ann)
    assert "Delete account" in client.get(f"/users/{ann['id']}").text
    assert "Delete account" not in client.get(f"/users/{bob['id']}").text
    # Someone else's edit page sends you to their profile instead.
    assert client.get(f"/users/{bob['id']}/edit", follow_redirects=False).headers["location"] == f"/users/{bob['id']}"


def test_edit_keeps_password_when_blank(client, new_user):
    user = new_user()
    sign_in_browser(client, user)
    form = {"name": "Renamed", "email": user["email"], "password": ""}
    response = client.patch(f"/users/{user['id']}", data=form, headers=HTMX)
    assert response.headers["HX-Redirect"] == f"/users/{user['id']}"
    assert "Renamed" in client.get(f"/users/{user['id']}").text
    client.cookies.clear()
    sign_in_browser(client, user)  # the old password still works


def test_edit_errors_and_other_users(client, new_user):
    ann, bob = new_user("Ann"), new_user("Bob")
    sign_in_browser(client, ann)
    bad = client.patch(f"/users/{ann['id']}", data={"email": "bad"}, headers=HTMX)
    other = client.patch(f"/users/{bob['id']}", data={"name": "hacked"}, headers=HTMX)
    assert bad.status_code == 400 and "Please fill a valid email address." in bad.text
    assert other.status_code == 403


def test_delete_signs_out_and_goes_home(client, new_user):
    user = new_user()
    sign_in_browser(client, user)
    response = client.delete(f"/users/{user['id']}", headers=HTMX)
    assert response.headers["HX-Redirect"] == "/"
    assert response.headers["set-cookie"].startswith('t="";')
    assert not re.search(user["id"], client.get("/users").text)


def test_signout_is_a_post(client, new_user):
    sign_in_browser(client, new_user())
    assert client.get("/signout").status_code == 405  # never a GET
    response = client.post("/signout", follow_redirects=False)
    assert (response.status_code, response.headers["location"]) == (303, "/")


def test_unknown_pages_and_ids_show_not_found(client, new_user):
    sign_in_browser(client, new_user())
    for path in ["/nope", "/users/not-an-id", "/users/000000000000000000000000"]:
        response = client.get(path)
        assert response.status_code == 404 and "Page not found" in response.text, path


def test_static_files_are_revalidated_in_development(client):
    """Edit style.css, reload, see the change: the browser must not reuse an old copy."""
    first = client.get("/static/style.css")
    assert first.headers["cache-control"] == "no-cache"
    # Unchanged file: the browser's check is answered with an empty 304.
    again = client.get("/static/style.css", headers={"If-None-Match": first.headers["etag"]})
    assert again.status_code == 304 and again.content == b""
    # Pages and the API are not touched by this rule.
    assert "cache-control" not in client.get("/api/health").headers
