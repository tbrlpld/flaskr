from flask import url_for

from flaskr.blog import create_post


def test_filtered_index_by_url(app, client):
    with app.test_request_context():
        create_post("other title", "other body", 2)
        response = client.get(
            url_for("search.display_search_filtered_index", q="test")
        )
        assert response.status_code == 200
        assert b"test title" in response.data
        assert b"other title" not in response.data


def test_search_bar_displayed_on_index(app, client):
    with app.test_request_context():
        response = client.get(url_for("index"))
        assert (bytes(
            'action="' + url_for('search.display_search_filtered_index'),
            encoding='utf8')
            in response.data)
