import pytest

from flaskr.blog import create_post, update_post
from flaskr.pagination import Pagination


@pytest.fixture
def numbered_posts(app):
    with app.app_context():
        # The first created is the oldest/lowest id!
        update_post(1, "paged title 01", "some body")
        # The created posts are all newer then fixture in the db
        create_post("paged title 02", "some body", 1)
        create_post("paged title 03", "some body", 1)
        create_post("paged title 04", "some body", 1)
        create_post("paged title 05", "some body", 1)
        create_post("paged title 06", "some body", 1)
        create_post("paged title 07", "some body", 1)
        create_post("paged title 08", "some body", 1)
        create_post("paged title 09", "some body", 1)
        create_post("paged title 10", "some body", 1)
        create_post("paged title 11", "some body", 1)
        create_post("paged title 12", "some body", 1)
        create_post("paged title 13", "some body", 1)
        create_post("paged title 14", "some body", 1)
        create_post("paged title 15", "some body", 1)
        # paged title 15 is the newest post/ highest id!!


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
    assert b"paged title 09" not in response.data
    assert b"paged title 08" not in response.data
    assert b"paged title 07" not in response.data
    assert b"paged title 06" not in response.data

    assert b"paged title 05" not in response.data
    assert b"paged title 04" not in response.data
    assert b"paged title 03" not in response.data
    assert b"paged title 02" not in response.data
    assert b"paged title 01" not in response.data


def test_pagination_on_second_index_page(numbered_posts, client):
    response = client.get("/?page=2")
    assert b"paged title 15" not in response.data
    assert b"paged title 14" not in response.data
    assert b"paged title 13" not in response.data
    assert b"paged title 12" not in response.data
    assert b"paged title 11" not in response.data

    assert b"paged title 10" in response.data
    assert b"paged title 09" in response.data
    assert b"paged title 08" in response.data
    assert b"paged title 07" in response.data
    assert b"paged title 06" in response.data

    assert b"paged title 05" not in response.data
    assert b"paged title 04" not in response.data
    assert b"paged title 03" not in response.data
    assert b"paged title 02" not in response.data
    assert b"paged title 01" not in response.data


def test_pagination_on_third_index_page(numbered_posts, client):
    response = client.get("/?page=3")
    assert b"paged title 15" not in response.data
    assert b"paged title 14" not in response.data
    assert b"paged title 13" not in response.data
    assert b"paged title 12" not in response.data
    assert b"paged title 11" not in response.data

    assert b"paged title 10" not in response.data
    assert b"paged title 09" not in response.data
    assert b"paged title 08" not in response.data
    assert b"paged title 07" not in response.data
    assert b"paged title 06" not in response.data

    assert b"paged title 05" in response.data
    assert b"paged title 04" in response.data
    assert b"paged title 03" in response.data
    assert b"paged title 02" in response.data
    assert b"paged title 01" in response.data


@pytest.mark.parametrize(
    ("page", "has_previous_expected"), (
        (1, False),
        (2, True),
        (3, True),
    ))
def test_pagination_object_has_previous(page, has_previous_expected):
    pagination = Pagination(
        total_items=20,
        items_per_page=5,
        current_page=page
    )
    assert pagination.has_previous == has_previous_expected
