from flaskr.db import get_db
from flaskr.likes import get_users_liking_post


def test_get_likes_for_post(app):
    # There is already one like in the db, created by user 2.
    with app.app_context():
        user_id = 2
        users_liking_post = get_users_liking_post(post_id=1)
        assert user_id in users_liking_post

        db = get_db()
        db.execute(
            "INSERT INTO like (user_id, post_id)"
            " VALUES (1, 1)"
        )
        db.commit()
        users_liking_post = get_users_liking_post(post_id=1)
        assert 1 in users_liking_post


def test_create(client, auth, app):
    auth.login()

    with app.app_context():
        db = get_db()
        likes_before = db.execute(
            "SELECT COUNT(id) FROM like WHERE post_id = 1").fetchone()[0]
        response = client.post("/likes/create", data={"post_id": 1})
        assert response.headers["Location"] == "http://localhost/1/detail"
        likes_after = db.execute(
            "SELECT COUNT(id) FROM like WHERE post_id = 1").fetchone()[0]
        assert likes_after == likes_before + 1


def test_no_double_like(client, auth, app):
    auth.login(username="other", password="other")

    with app.app_context():
        db = get_db()
        # Making sure that there is already a like by the user for the post
        like_count = db.execute(
            "SELECT COUNT(id) FROM like WHERE post_id = 1 AND user_id = 2"
        ).fetchone()[0]
        assert like_count == 1

    response = client.post("/likes/create", data={"post_id": 1})
    assert response.status_code == 403  #  Forbidden


def test_delete(client, auth, app):
    auth.login(username="other", password="other")

    with app.app_context():
        db = get_db()
        likes_before = db.execute(
            "SELECT COUNT(id) FROM like WHERE post_id = 1").fetchone()[0]
        response = client.post("/likes/delete", data={"post_id": 1})
        assert response.headers["Location"] == "http://localhost/1/detail"
        likes_after = db.execute(
            "SELECT COUNT(id) FROM like WHERE post_id = 1").fetchone()[0]
        assert likes_after == likes_before - 1


def test_logged_in_user_sees_like_link(client, auth, app):
    # No link when not logged in
    response = client.get("/1/detail")
    assert b"/likes/create" not in response.data

    with app.app_context():
        db = get_db()
        # Making sure that there is no like by the user for the post
        like_count = db.execute(
            "SELECT COUNT(id) FROM like WHERE post_id = 1 AND user_id = 1"
        ).fetchone()[0]
        assert like_count == 0

    auth.login()
    response = client.get("/1/detail")
    assert b"/likes/create" in response.data
    auth.logout()

    # User with existing like sees unlike link
    with app.app_context():
        db = get_db()
        # Making sure that there is a like by the user for the post
        like_count = db.execute(
            "SELECT COUNT(id) FROM like WHERE post_id = 1 AND user_id = 2"
        ).fetchone()[0]
        assert like_count == 1
    auth.login(username="other", password="other")
    response = client.get("/1/detail")
    assert b"/likes/delete" in response.data
    auth.logout()
