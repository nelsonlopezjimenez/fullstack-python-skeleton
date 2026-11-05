"""Shared test setup. pytest loads conftest.py by itself before the test files.

[BEGINNER] A *fixture* is a function that prepares something a test needs. A test asks for it
by naming it as a parameter: `def test_x(client):` gets the TestClient below. Jest/Vitest used
beforeAll/afterAll for the same job.
"""
import os
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Must happen BEFORE `import app...`: app/config.py reads the environment when it is imported.
# A separate database, so the tests never touch the data of the app you run by hand.
TEST_DB = "pythonskeleton_test"
os.environ["MONGODB_URI"] = f"mongodb://localhost:27017/{TEST_DB}?directConnection=true"
# At least 32 bytes: PyJWT warns (InsecureKeyLengthWarning) about shorter HS256 secrets.
os.environ["JWT_SECRET"] = "test-secret-0123456789abcdef-0123456789"
os.environ["ENV"] = "development"


def mongo_is_running() -> bool:
    try:
        MongoClient(os.environ["MONGODB_URI"], serverSelectionTimeoutMS=1500).admin.command("ping")
        return True
    except PyMongoError:
        return False


MONGO_UP = mongo_is_running()
# [BEGINNER] A marker for tests that need the database: they are SKIPPED (not failed) when
# MongoDB is not running, so the unit tests still run on a machine without it.
needs_mongo = pytest.mark.skipif(not MONGO_UP, reason="MongoDB is not running on localhost:27017")


# [BEGINNER] scope="session": built once for the whole test run (like beforeAll), then the code
# after `yield` runs at the end (like afterAll).
@pytest.fixture(scope="session")
def app_client():
    from fastapi.testclient import TestClient

    from app.main import app

    sync_client = MongoClient(os.environ["MONGODB_URI"])
    sync_client.drop_database(TEST_DB)
    # `with` runs the app's lifespan: connect to MongoDB at the start, disconnect at the end.
    with TestClient(app) as client:
        yield client
    sync_client.drop_database(TEST_DB)


@pytest.fixture
def client(app_client):
    """The shared client, with no cookies left over from the previous test."""
    app_client.cookies.clear()
    return app_client


@pytest.fixture
def new_user(client):
    """Sign up a fresh user; returns a function so a test can make several."""
    def make(name="Ann", password="secret1"):
        # uuid4().hex is random, so every test gets its own email (no duplicates between tests).
        email = f"{name.lower().replace(' ', '.')}.{uuid.uuid4().hex[:8]}@test.io"
        response = client.post("/api/users", json={"name": name, "email": email, "password": password})
        assert response.status_code == 201, response.text
        signin = client.post("/api/auth/sessions", json={"email": email, "password": password})
        client.cookies.clear()  # the test decides itself whether to send the token
        body = signin.json()
        return {"email": email, "password": password, "id": body["user"]["_id"], "token": body["token"]}
    return make
