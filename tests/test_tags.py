from flask import url_for

from flaskr.db import get_db
from flaskr.tags import (
    get_or_create_tag, get_or_create_tags_from_string,
    get_tags_for_post, associate_tag_with_post,
    remove_tag_associations_for_post
)


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

        tag_rows = db.execute("SELECT (name) FROM tag").fetchall()
        tags = [row["name"] for row in tag_rows]
        assert "testtag" in tags
        assert "newtag" in tags


def test_get_or_create_tag_from_string(app):
    with app.app_context():
        db = get_db()

        tag_count = db.execute("SELECT COUNT(id) FROM tag").fetchone()[0]
        assert tag_count == 1

        tag_ids = get_or_create_tags_from_string("testtag newtag anothertag")

        tag_count = db.execute("SELECT COUNT(id) FROM tag").fetchone()[0]
        assert tag_count == 3

        tag_rows = db.execute("SELECT (name) FROM tag").fetchall()
        tags = [row["name"] for row in tag_rows]
        assert "testtag" in tags
        assert "newtag" in tags
        assert "anothertag" in tags


def test_associate_tag_with_post(app):
    with app.app_context():
        new_tag_id = get_or_create_tag("newtag")
        associate_tag_with_post(tag_id=new_tag_id, post_id=1)
        tags = get_tags_for_post(post_id=1)
        assert "testtag" in tags
        assert "newtag" in tags


def test_remove_tag_associations_for_post(app):
    with app.app_context():
        tags = get_tags_for_post(post_id=1)
        assert "testtag" in tags
        tag_id = get_or_create_tag("testtag")
        remove_tag_associations_for_post(post_id=1)
        tags = get_tags_for_post(post_id=1)
        assert "testtag" not in tags


def test_get_tags_for_post(auth, client, app):
    auth.login()
    with app.test_request_context():
        # Test existing post-tag association
        tags_post_1 = get_tags_for_post(post_id=1)
        assert "testtag" in tags_post_1
        assert tags_post_1 == ["testtag"]

        # Create new tag and new post-tag association and test it
        new_tag_id = get_or_create_tag("newtag")
        associate_tag_with_post(tag_id=new_tag_id, post_id=1)
        tags_post_1 = get_tags_for_post(post_id=1)
        assert "newtag" in tags_post_1
        assert "testtag" in tags_post_1

        # Create a new post and new post-tag association and test it
        client.post(url_for("blog.create"), data={
            "title": "A new Post",
            "body": "This is the content of the new post.",
        })
        associate_tag_with_post(tag_id=new_tag_id, post_id=2)
        tags_post_2 = get_tags_for_post(post_id=2)
        assert "newtag" in tags_post_2
        assert tags_post_2 == ["newtag"]


def test_create_tag_through_create_post(client, auth, app):
    auth.login()  # Only logged-in users can create posts
    # The test_request_context allows to use `url_for` outside of a request
    # context.
    with app.test_request_context("/"):
        db = get_db()

        assert db.execute("SELECT COUNT(id) FROM tag").fetchone()[0] == 1

        client.post(url_for("blog.create"), data={
            "title": "A new Post",
            "body": "This is the content of the new post.",
            "tags": "atag newtag"
        })

        assert db.execute("SELECT COUNT(id) FROM tag").fetchone()[0] == 3
        new_post_id = db.execute(
            "SELECT (id) FROM post WHERE title = 'A new Post'").fetchone()[0]
        assert new_post_id == 2

        # Check association of tag with post
        tags = get_tags_for_post(post_id=2)
        assert "atag" in tags
        assert "newtag" in tags


def test_create_tag_through_update_post(client, auth, app):
    auth.login()  # Only logged-in users can update posts
    # The test_request_context allows to use `url_for` outside of a request
    # context.
    with app.test_request_context("/"):
        db = get_db()

        tags_in_db = db.execute("SELECT COUNT(id) FROM tag").fetchone()[0]
        assert tags_in_db == 1

        client.post(url_for("blog.update", id=1), data={
            "title": "A title",
            "body": "This is the new content of the new post.",
            "tags": "testtag newtag"
        })

        tags_in_db = db.execute("SELECT COUNT(id) FROM tag").fetchone()[0]
        assert tags_in_db == 2

        # Check association of tag with post
        tags = get_tags_for_post(post_id=1)
        assert "testtag" in tags
        assert "newtag" in tags


def test_tags_input_field_shows_existing_tags(client, auth, app):
    auth.login()

    with app.test_request_context("/"):
        response = client.get(url_for("blog.update", id=1))
        assert b"testtag" in response.data
