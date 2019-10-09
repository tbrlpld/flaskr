from flask import url_for

from flaskr.db import get_db


def test_filtered_index_by_url(app, client):
    with app.test_request_context():
        response = client.get(
            url_for("search.display_search_filtered_index", title="test title")
        )

