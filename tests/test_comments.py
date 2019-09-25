from flaskr.comments import get_comments_for_post
from flaskr.db import get_db


def test_create(client, auth, app):
    auth.login()

    # Response shows an error when the comment body is missing
    response = client.post(
        "/comments/create", data={"post_id": 1, "body": ""},
        follow_redirects=True)
    assert b"Comment text required" in response.data

    with app.app_context():
        db = get_db()
        # So far, there should only be one comment in the db (from the fixture)
        count = db.execute("SELECT COUNT(id) FROM comment").fetchone()[0]
        assert count == 1
        # Creating a new comment
        response = client.post(
            "/comments/create", data={"post_id": 1, "body": "test comment"})
        # New there should be two comments in the db
        count = db.execute("SELECT COUNT(id) FROM comment").fetchone()[0]
        assert count == 2


def test_get_comments(app):
    with app.app_context():
        comments = get_comments_for_post(post_id=1)
        assert len(comments) == 1
        assert "test comment body" in comments[0]["body"]
        assert comments[0]["username"] == "other"


def test_comments_shown_on_detail(client):
    response = client.get(
        "/1/detail", data={"post_id": 1, "body": ""}
    )
    assert b"test comment body" in response.data


def test_delete(client, auth, app):
    # Redirection when not logged in
    response = client.post("/comments/1/delete")
    assert response.headers["Location"] == "http://localhost/auth/login"

    # Comment deletion forbidden when not the author of the post the comment
    # belongs to.
    # Other is the author of the comment but not of the post, thus can not
    # delete the comment.
    auth.login(username="other", password="other")
    response = client.post("/comments/1/delete")
    assert response.status_code == 403  # Forbidden
    auth.logout()

    # Logging in in the author of the post
    auth.login()
    with app.app_context():
        db = get_db()
        count_before_deletion = db.execute(
            "SELECT COUNT(id) FROM comment"
        ).fetchone()[0]
        response = client.post("/comments/1/delete")
        count_after_deletion = db.execute(
            "SELECT COUNT(id) FROM comment"
        ).fetchone()[0]
        assert count_after_deletion == count_before_deletion - 1
        assert response.headers["Location"] == "http://localhost/1/detail"


def test_post_author_sees_delete_button_on_detail(client, auth):
    response = client.get("/1/detail")
    assert 'href="/comments/1/delete"' not in response.data

    # auth.login()
