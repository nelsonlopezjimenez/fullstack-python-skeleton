"""The React client's server side: the single-page-app route and its static files.

[BEGINNER] The components run in the browser, so pytest cannot click through them. It checks
what the server is responsible for: every /react URL gets index.html, the files exist, and the
strict Content-Security-Policy still applies. The /api the components call is tested in test_4_api.py.
"""
import re

from conftest import needs_mongo

pytestmark = needs_mongo


def test_every_react_url_gets_the_same_index_html(client):
    for path in ["/react", "/react/", "/react/users", "/react/users/123/edit", "/react/no-such-page"]:
        response = client.get(path)
        assert response.status_code == 200, path
        assert '<div id="root"></div>' in response.text, path
        assert 'src="/static/react/main.js"' in response.text, path


def test_csp_stays_strict(client):
    # No 'unsafe-inline' / 'unsafe-eval': the client is external ES modules only.
    csp = client.get("/react").headers["content-security-policy"]
    assert "default-src 'self'" in csp and "unsafe" not in csp


def test_every_imported_file_is_served(client):
    """Follow the import lines from main.js, like the browser does, and fetch each file."""
    seen, todo = set(), ["/static/react/main.js"]
    while todo:
        url = todo.pop()
        if url in seen:
            continue
        seen.add(url)
        response = client.get(url)
        assert response.status_code == 200, url
        assert "javascript" in response.headers["content-type"], url
        if url.endswith("react-all.js"):
            continue  # the vendored bundle imports nothing
        base = url.rsplit("/", 1)[0]
        for spec in re.findall(r"""(?:from|import\()\s*['"]([^'"]+)['"]""", response.text):
            if spec.startswith("/"):
                todo.append(spec)
            else:  # './x.js' or '../x.js', relative to this file
                parts = base.split("/")
                for piece in spec.split("/"):
                    if piece == "..":
                        parts.pop()
                    elif piece != ".":
                        parts.append(piece)
                todo.append("/".join(parts))
    assert "/static/vendor/react-all.js" in seen
    assert len(seen) > 15  # all pages, including the lazy() ones


def test_htmx_home_links_to_the_react_client(client):
    assert 'href="/react"' in client.get("/").text


def test_static_files_are_revalidated_in_development(client):
    """Edit a component, reload, see the change: the browser must not reuse an old copy."""
    first = client.get("/static/react/user/Users.js")
    assert first.headers["cache-control"] == "no-cache"
    # Unchanged file: the browser's check is answered with an empty 304.
    again = client.get("/static/react/user/Users.js", headers={"If-None-Match": first.headers["etag"]})
    assert again.status_code == 304 and again.content == b""
    # Pages and the API are not touched by this rule.
    assert "cache-control" not in client.get("/api/health").headers
