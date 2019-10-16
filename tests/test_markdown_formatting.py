from flask import url_for

import pytest

from flaskr.db import get_db


@pytest.mark.parametrize(("post_path", "post_id"), (
    ("/create", 2),
    ("/1/update", 1)
))
def test_post_body_html_available_in_DB(
        client, auth, app, post_path, post_id):
    auth.login()
    with app.test_request_context():
        form_data = {
            "title": "Post with markdown body",
            "body": "## Test Heading"
        }
        client.post(post_path, data=form_data)

    with app.app_context():
        db = get_db()
        row = db.execute(
            "SELECT body_html FROM post WHERE id = ?",
            (post_id,)
        ).fetchone()
        assert "<h2>Test Heading</h2>" in row["body_html"]


@pytest.mark.parametrize(("post_path", "post_id"), (
    ("/create", 2),
    ("/1/update", 1)
))
def test_post_body_html_in_DB_is_safe(
        client, auth, app, post_path, post_id):
    """
    When the user adds HTML in the body, this html should be sanitized during
    form submission. That means that the html tag brackets are replaced with
    `&lt;` and `&gt;`. The html generated from the markdown should be contained
    though.
    """
    auth.login()
    with app.test_request_context():
        form_data = {
            "title": "Post with markdown body",
            "body": "## Test Heading\n<i>This should not be html</i>"
        }
        client.post(post_path, data=form_data)

    with app.app_context():
        db = get_db()
        row = db.execute(
            "SELECT body_html FROM post WHERE id = ?",
            (post_id,)
        ).fetchone()
        assert "<h2>Test Heading</h2>" in row["body_html"]
        assert "<i>This should not be html</i>" not in row["body_html"]
        assert "&lt;i&gt;This should not be html&lt;/i&gt;" not in row["body_html"]


@pytest.mark.parametrize("get_path", (
    "/2/detail",
    "/"
))
def test_markdown_shown_as_html(client, auth, app, get_path):
    auth.login()
    with app.test_request_context():
        form_data = {
            "title": "Post with markdown body",
            "body": "## Test Heading"
        }
        client.post(url_for("blog.create"), data=form_data)

        response = client.get(get_path)
        assert response.status_code == 200
        print(response.data)
        assert b"<h2>Test Heading</h2>" in response.data


@pytest.mark.parametrize("get_path", (
    "/2/detail",
    "/"
))
def test_html_in_markdown_is_escaped(client, auth, app, get_path):
    auth.login()
    with app.test_request_context():
        form_data = {
            "title": "Post with markdown body",
            "body": "<i>This HTML should be escaped</i>"
        }
        client.post(get_path, data=form_data)

        response = client.get("/")
        assert response.status_code == 200
        assert b"<i>This HTML should be escaped</i>" not in response.data
        assert b"&lt;i&gt;This HTML should be escaped&lt;/i&gt;" in response.data
