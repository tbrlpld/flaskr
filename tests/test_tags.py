from flask import url_for

from flaskr.db import get_db
from flaskr.tags import get_or_create_tag, get_or_create_tags_from_string


def test_get_or_create_tag(app):
    with app.app_context():
        db = get_db()

        tag_id = get_or_create_tag("testtag")
        assert tag_id == 1
        tags_in_db = db.execute("SELECT COUNT(id) FROM tag").fetchone()[0]
        assert tags_in_db == 1

        tag_id = get_or_create_tag("newtag")
        assert tag_id != 1
        tags_in_db = db.execute("SELECT COUNT(id) FROM tag").fetchone()[0]
        assert tags_in_db == 2


def test_get_or_create_tag_from_string(app):
    with app.app_context():
        db = get_db()

        tags_in_db = db.execute("SELECT COUNT(id) FROM tag").fetchone()[0]
        assert tags_in_db == 1

        tag_ids = get_or_create_tags_from_string("testtag newtag anothertag")

        tags_in_db = db.execute("SELECT COUNT(id) FROM tag").fetchone()[0]
        assert tags_in_db == 3


def test_create_tag_through_create_post(client, auth, app):
    auth.login()

    # The test_request_context allows to use `url_for` outside of a request
    # context
    with app.test_request_context("/"):

        db = get_db()

        tags_in_db = db.execute("SELECT COUNT(id) FROM tag").fetchone()[0]
        assert tags_in_db == 1

        client.post(url_for("blog.create"), data={
            "title": "A new Post",
            "body": "This is the content of the new post.",
            "tags": "testtag newtag"
        })

        tags_in_db = db.execute("SELECT COUNT(id) FROM tag").fetchone()[0]
        assert tags_in_db == 2
