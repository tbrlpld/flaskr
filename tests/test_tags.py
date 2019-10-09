from flask import url_for

from flaskr.db import get_db
from flaskr.tags import (
    get_or_create_tag, get_or_create_tags_from_string,
    get_tags_for_post,
    associate_tag_with_post,
    disassociate_tag_from_post,
    remove_tag_associations_for_post,
    update_tag_associations_for_post
)


def test_get_or_create_tag(app):
    with app.app_context():
        db = get_db()

        tag_id = get_or_create_tag("testtag")
        assert tag_id == 1
        tags_in_db = db.execute("SELECT COUNT(id) FROM tag").fetchone()[0]
        assert tags_in_db == 1

        tag_id = get_or_create_tag("")
        assert tag_id == None

        tag_id = get_or_create_tag(" ")
        assert tag_id == None

        tag_id = get_or_create_tag("newtag")
        assert tag_id != 1
        tags_in_db = db.execute("SELECT COUNT(id) FROM tag").fetchone()[0]
        assert tags_in_db == 2

        tag_rows = db.execute("SELECT (name) FROM tag").fetchall()
        tags = [row["name"] for row in tag_rows]
        assert "testtag" in tags
        assert "newtag" in tags


def test_get_or_create_tags_from_string(app):
    with app.app_context():
        db = get_db()

        tag_count = db.execute("SELECT COUNT(id) FROM tag").fetchone()[0]
        assert tag_count == 1

        # Passing an empty string should return an empty tuple
        tag_ids = get_or_create_tags_from_string("")
        assert tag_ids == tuple()

        # Passing a string with only whitespace should return an empty tuple
        tag_ids = get_or_create_tags_from_string(" ")
        assert tag_ids == tuple()

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


def test_disassociate_tag_from_post(app):
    with app.app_context():
        tags = get_tags_for_post(post_id=1)
        assert "testtag" in tags

        tag_id = get_or_create_tag("testtag")
        disassociate_tag_from_post(tag_id=tag_id, post_id=1)

        tags = get_tags_for_post(post_id=1)
        assert "testtag" not in tags
        assert tags == []


def test_remove_tag_associations_for_post(app):
    with app.app_context():
        tags = get_tags_for_post(post_id=1)
        assert "testtag" in tags

        remove_tag_associations_for_post(post_id=1)
        tags = get_tags_for_post(post_id=1)
        assert "testtag" not in tags
        assert tags == []


def test_update_tag_associations_for_post(app):
    """
    Updating the tag associations for a post can be used as a convenience
    function, which takes care of adding new tags associations and deletes
    removed tag associations.

    If a tag does not exist before, it is created.
    """
    with app.app_context():
        tags = get_tags_for_post(post_id=1)
        assert tags == ["testtag"]

        # Adding association
        update_tag_associations_for_post(
            tag_string="testtag newtag", post_id=1)
        tags = get_tags_for_post(post_id=1)
        assert "testtag" in tags
        assert "newtag" in tags

        # Removing association
        update_tag_associations_for_post(
            tag_string="newtag", post_id=1)
        tags = get_tags_for_post(post_id=1)
        assert "testtag" not in tags
        assert "newtag" in tags

        # Delete all associations with empty string
        update_tag_associations_for_post(
            tag_string="", post_id=1)
        tags = get_tags_for_post(post_id=1)
        assert "testtag" not in tags
        assert "newtag" not in tags
        assert tags == []


def test_display_of_tagged_posts(client, app):
    with app.test_request_context():
        response = client.get(
            url_for("tags.display_tagged_posts", tag="testtag"))
        assert b"test title" in response.data
        assert b"other" not in response.data


def test_link_to_tagged_posts(client, app):
    with app.test_request_context():
        response = client.get(
            url_for("index", tag="testtag"))
        assert b"test title" in response.data
        assert b"testtag" in response.data
        assert bytes(url_for("tags.display_tagged_posts", tag="testtag"),
                     encoding="utf8") in response.data


def test_deleting_post_removes_tag_associations(client, auth, app):
    auth.login()
    with app.test_request_context():
        tags = get_tags_for_post(post_id=1)
        assert "testtag" in tags

        client.post(url_for("blog.delete", id=1))
        tags = get_tags_for_post(post_id=1)
        assert "testtag" not in tags
        assert tags == []


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


def test_remove_tag_association_through_update_post(client, auth, app):
    auth.login()  # Only logged-in users can update posts
    # The test_request_context allows to use `url_for` outside of a request
    # context.
    with app.test_request_context("/"):
        db = get_db()

        tags = get_tags_for_post(post_id=1)
        assert "testtag" in tags

        client.post(url_for("blog.update", id=1), data={
            "title": "A title",
            "body": "This is the new content of the new post.",
            "tags": ""
        })

        tags = get_tags_for_post(post_id=1)
        assert "testtag" not in tags


def test_tags_input_field_shows_existing_tags(client, auth, app):
    auth.login()

    with app.test_request_context("/"):
        response = client.get(url_for("blog.update", id=1))
        assert b"testtag" in response.data


def test_tags_shown_on_index(client, auth, app):
    auth.login()

    with app.test_request_context("/"):
        response = client.get(url_for("blog.index"))
        assert b"testtag" in response.data


def test_tags_shown_on_detail(client, auth, app):
    auth.login()

    with app.test_request_context("/"):
        response = client.get(url_for("blog.detail", id=1))
        assert b"testtag" in response.data


def test_post_without_tags_shown_on_index(client, auth, app):
    """
    When the solution to add the tags to the post object was added to the
    SQL statement which retrieves the post, this broke something so that no
    posts without tags would be retrievable anymore!
    This test is to check the functionality of not tagged posts.
    """
    auth.login()

    with app.test_request_context("/"):
        # Post without tags also in index
        client.post("/create", data={
            "title": "Without Tags", "body": "some body"})

        response = client.get(url_for("blog.index"))
        assert b"Without Tags" in response.data


def test_detail_of_post_without_tag_still_works(client, auth, app):
    """
    When the solution to add the tags to the post object was added to the
    SQL statement which retrieves the post, this broke something so that no
    posts without tags would be retrievable anymore!
    This test is to check the functionality of not tagged posts.
    """
    auth.login()

    with app.test_request_context("/"):
        # Post without tags can be retrieved on detail page
        client.post("/create", data={
            "title": "Without Tags", "body": "some body"})
        response = client.get(url_for("blog.detail", id=2))
        assert b"Without Tags" in response.data


def test_editing_a_post_without_tags_does_show_none_as_tag(client, auth, app):
    """
    When a post has no tags SQL will return NULL for the tag_string column.
    But None (the Python NULL value) should not be printed in the tag_string.
    """
    auth.login()

    with app.test_request_context("/"):
        # Post without tags can be retrieved on detail page
        client.post("/create", data={
            "title": "Without Tags", "body": "some body"})
        response = client.get(url_for("blog.update", id=2))
        assert b"None" not in response.data


# def test_something(app):
#     with app.app_context():
#         new_tag_id = get_or_create_tag("newtag")
#         associate_tag_with_post(tag_id=new_tag_id, post_id=1)

#         db = get_db()
#         row = db.execute(
#             "SELECT p.id, p.title, GROUP_CONCAT(t.name) AS tag_list"
#             " FROM post p"
#             " JOIN post_tag pt ON p.id = pt.post_id"
#             " JOIN tag t ON pt.tag_id = t.id"
#             " WHERE pt.post_id = 1"
#         ).fetchone()
#         print(tuple(row))
#         print(row['tag_list'].split(","))

#         rows = db.execute(
#             "SELECT p.id, p.title, GROUP_CONCAT(t.name) AS tag_list"
#             " FROM post p"
#             " JOIN post_tag pt ON p.id = pt.post_id"
#             " JOIN tag t ON pt.tag_id = t.id"
#         ).fetchall()
#         print(tuple(rows))
#         for r in rows:
#             print(tuple(r))
#             print(r['tag_list'].split(","))
