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
