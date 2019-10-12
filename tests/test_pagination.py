import pytest

from flaskr.blog import create_post


@pytest.fixture
def numbered_posts(app):
    with app.app_context():
        # The created posts are all newer then fixture in the db
        # The first created is the oldest!
        create_post("paged title 1", "some body", 1)
        create_post("paged title 2", "some body", 1)
        create_post("paged title 3", "some body", 1)
        create_post("paged title 4", "some body", 1)
        create_post("paged title 5", "some body", 1)
        create_post("paged title 6", "some body", 1)
        create_post("paged title 7", "some body", 1)
        create_post("paged title 8", "some body", 1)
        create_post("paged title 9", "some body", 1)
        create_post("paged title 10", "some body", 1)
        create_post("paged title 11", "some body", 1)
        create_post("paged title 12", "some body", 1)
        create_post("paged title 13", "some body", 1)
        create_post("paged title 14", "some body", 1)
        create_post("paged title 15", "some body", 1)
        # paged title 15 is the newest post!!


@pytest.mark.parametrize("path", (
    "/",
    "/?page=1",
))
def test_pagination_on_plain_index(numbered_posts, client, path):
    response = client.get(path)
    assert b"paged title 15" in response.data
    assert b"paged title 14" in response.data
    assert b"paged title 13" in response.data
    assert b"paged title 12" in response.data
    assert b"paged title 11" in response.data

    assert b"paged title 10" not in response.data
    assert b"paged title 9" not in response.data
    assert b"paged title 8" not in response.data
    assert b"paged title 7" not in response.data
    assert b"paged title 6" not in response.data


def test_pagination_on_second_index_page(numbered_posts, client):
    response = client.get("/?page=2")
    assert b"paged title 15" not in response.data
    assert b"paged title 14" not in response.data
    assert b"paged title 13" not in response.data
    assert b"paged title 12" not in response.data
    assert b"paged title 11" not in response.data

    assert b"paged title 10" in response.data
    assert b"paged title 9" in response.data
    assert b"paged title 8" in response.data
    assert b"paged title 7" in response.data
    assert b"paged title 6" in response.data
