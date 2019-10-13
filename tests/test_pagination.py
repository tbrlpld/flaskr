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
def test_pagination_of_posts_on_first_index_page(numbered_posts, client, path):
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


def test_pagination_of_posts_on_second_index_page(numbered_posts, client):
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


def test_pagination_of_posts_on_third_index_page(numbered_posts, client):
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
    ("total_items", "items_per_page", "total_pages_expected"), (
        (12, 5, 3),
        (50, 10, 5),
        (51, 10, 6),
    ))
def test_pagination_object_total_pages_property(
        total_items,
        items_per_page,
        total_pages_expected):
    pagination = Pagination(
        total_items=total_items,
        items_per_page=items_per_page,
        current_page=1
    )
    assert pagination.total_pages == total_pages_expected


@pytest.mark.parametrize(
    ("page", "has_previous_expected"), (
        (1, False),
        (2, True),
        (3, True),
    ))
def test_pagination_object_has_previous_property(page, has_previous_expected):
    pagination = Pagination(
        total_items=15,
        items_per_page=5,
        current_page=page
    )
    assert pagination.has_previous == has_previous_expected


@pytest.mark.parametrize(
    ("page", "previous_expected"), (
        (1, None),
        (2, 1),
        (3, 2),
    ))
def test_pagination_object_previous_property(page, previous_expected):
    pagination = Pagination(
        total_items=15,
        items_per_page=5,
        current_page=page
    )
    assert pagination.previous == previous_expected


@pytest.mark.parametrize(
    ("page", "has_next_expected"), (
        (1, True),
        (2, True),
        (3, False),
    ))
def test_pagination_object_has_next_property(page, has_next_expected):
    pagination = Pagination(
        total_items=15,
        items_per_page=5,
        current_page=page
    )
    assert pagination.has_next == has_next_expected


def test_pagination_object_has_next_property_when_no_items():
    pagination = Pagination(
        total_items=0,
        items_per_page=5,
        current_page=1
    )
    assert pagination.has_next is False


@pytest.mark.parametrize(
    ("page", "next_expected"), (
        (1, 2),
        (2, 3),
        (3, None),
    ))
def test_pagination_object_next_property(page, next_expected):
    pagination = Pagination(
        total_items=15,
        items_per_page=5,
        current_page=page
    )
    assert pagination.next == next_expected


@pytest.mark.parametrize(
    ("page", "is_first_expected"), (
        (1, True),
        (2, False),
        (3, False),
    ))
def test_pagination_object_is_first_property(page, is_first_expected):
    pagination = Pagination(
        total_items=15,
        items_per_page=5,
        current_page=page
    )
    assert pagination.is_first == is_first_expected


@pytest.mark.parametrize(
    ("total_items", "items_per_page", "first_expected"), (
        (12, 5, 1),
        (50, 10, 1),
        (51, 10, 1),
    ))
def test_pagination_object_first_property(
        total_items,
        items_per_page,
        first_expected):
    pagination = Pagination(
        total_items=total_items,
        items_per_page=items_per_page,
        current_page=1
    )
    assert pagination.first == first_expected


@pytest.mark.parametrize(
    ("page", "is_last_expected"), (
        (1, False),
        (2, False),
        (3, True),
    ))
def test_pagination_object_is_last_property(page, is_last_expected):
    pagination = Pagination(
        total_items=15,
        items_per_page=5,
        current_page=page
    )
    assert pagination.is_last == is_last_expected


@pytest.mark.parametrize(
    ("total_items", "items_per_page", "last_expected"), (
        (12, 5, 3),
        (50, 10, 5),
        (51, 10, 6),
    ))
def test_pagination_object_last_property(
        total_items,
        items_per_page,
        last_expected):
    pagination = Pagination(
        total_items=total_items,
        items_per_page=items_per_page,
        current_page=1
    )
    assert pagination.last == last_expected


@pytest.mark.parametrize(
    ("page", "items_per_page", "item_offset_expected"), (
        (1, 5, 0),
        (2, 5, 5),
        (3, 3, 6),
    ))
def test_pagination_object_item_offset_property(
        page, items_per_page, item_offset_expected):
    pagination = Pagination(
        total_items=15,
        items_per_page=items_per_page,
        current_page=page
    )
    assert pagination.item_offset == item_offset_expected


def test_pagination_links_on_index_pages(numbered_posts, client):
    response = client.get("/?page=1")
    assert b"/?page=0" not in response.data
    assert b"/?page=2" in response.data

    response = client.get("/?page=2")
    assert b"/?page=1" in response.data
    assert b"/?page=3" in response.data

    response = client.get("/?page=3")
    assert b"/?page=2" in response.data
    assert b"/?page=4" not in response.data


def test_pagination_links_on_search_result_index_page(numbered_posts, client):
    response = client.get("/search/?q=paged&page=1")
    assert b"/search/?q=paged&page=0" not in response.data
    assert b"/search/?q=paged&page=2" in response.data

    response = client.get("/search/?q=paged&page=2")
    assert b"/search/?q=paged&page=1" in response.data
    assert b"/search/?q=paged&page=3" in response.data

    response = client.get("/search/?q=paged&page=3")
    assert b"/search/?q=paged&page=2" in response.data
    assert b"/search/?q=paged&page=4" not in response.data
