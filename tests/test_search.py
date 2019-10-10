from flask import url_for

from flaskr.blog import create_post
from flaskr.db import get_db


def test_filtered_index_by_url(app, client):
    with app.test_request_context():
        create_post("other title", "other body", 2)
        response = client.get(
            url_for("search.display_search_filtered_index", title="test title")
        )
        assert response.status_code == 200
        assert b"test title" in response.data
        assert b"other title" not in response.data
