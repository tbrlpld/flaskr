
from flaskr.db import get_db
from flaskr.tags import get_or_create_tag


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
