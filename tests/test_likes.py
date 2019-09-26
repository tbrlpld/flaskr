from flaskr.db import get_db


def test_create(client, auth, app):
    auth.login()

    with app.app_context():
        db = get_db()
        likes_before = db.execute(
            "SELECT COUNT(post_id) FROM like WHERE post_id = 1").fetchone()[0]
        response = client.post("/likes/create", data={"post_id": 1})
        assert response.headers["Location"] == "http://localhost/1/detail"
        likes_after = db.execute(
            "SELECT COUNT(post_id) FROM like WHERE post_id = 1").fetchone()[0]
        assert likes_after == likes_before + 1


def test_no_double_like(client, auth, app):
    auth.login(username="other", password="other")

    with app.app_context():
        db = get_db()
        # Making sure that there is already a like by the user for the post
        like_count = db.execute(
            "SELECT COUNT(post_id) FROM like WHERE post_id = 1 AND user_id = 2"
        ).fetchone()[0]
        assert like_count == 1

    response = client.post("/likes/create", data={"post_id": 1})
    assert response.status_code == 403  #  Forbidden


def test_logged_in_user_sees_like_link(client, auth, app):
    # No link when not logged in
    response = client.get("/1/detail")
    assert b"/likes/create" not in response.data

    with app.app_context():
        db = get_db()
        # Making sure that there is no like by the user for the post
        like_count = db.execute(
            "SELECT COUNT(post_id) FROM like WHERE post_id = 1 AND user_id = 1"
        ).fetchone()[0]
        assert like_count == 0

    auth.login()
    response = client.get("/1/detail")
    assert b"/likes/create" in response.data
