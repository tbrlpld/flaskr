import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    assert client.get("/auth/register").status_code == 200

    response = client.post(
        "/auth/register",
        data={"username": "a", "password": "a"}
    )
    # When redirecting, then there will be a Location entry in the header
    # containing the redirection URL.
    assert "http://localhost/auth/login" == response.headers["Location"]

    # Check that the registered user is available in the database.
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(("username", "password", "message"), (
    ("", "", b"Username is required."),
    ("a", "", b"Password is required."),
    ("test", "test", b"already registered"),
))  # Running the same test function with different inputs
def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register",
        data={"username": username, "password": password}
    )
    assert message in response.data


def test_login(client, auth):
    # Login site can successfully be reached
    assert client.get("/auth/login").status_code == 200

    # Post with wrong info leads to error messages
    response = client.post("/auth/login", data={
        "username": "not", "password": "not"})
    assert b"Incorrect user name." in response.data
    response = client.post("/auth/login", data={
        "username": "test", "password": "not"})
    assert b"Incorrect password." in response.data

    # Successful login redirects to the home/index.
    response = auth.login()
    assert response.headers["Location"] == "http://localhost/"

    # Using client in a with block allows accessing context variables such as
    # session after the response is returned. Normally, accessing session
    # outside of a request would raise an error.
    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
