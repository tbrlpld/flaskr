
from flaskr.db import get_db


def get_or_create_tag(name):
    """
    Get or create a tag with the given name and return the tag id
    """
    db = get_db()
    # Create the tag or ignore if it exists
    db.execute(
        "INSERT OR IGNORE INTO tag (name) VALUES (?)", (name,)
    )
    # Grab the id of the tag
    return db.execute(
        "SELECT (id) FROM tag WHERE name = ?", (name,)
    ).fetchone()["id"]



