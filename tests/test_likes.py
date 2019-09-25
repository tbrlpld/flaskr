from flaskr.db import get_db


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
