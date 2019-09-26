
from flaskr.db import get_db


def get_or_create_tag(name):
    """
    Get or create a tag with the given name and return the tag id

    :param name: Name or word that the tag is made of
    :type name: string

    :returns: Id of the tag created in the database
    :rtype: int
    """
    db = get_db()
    # Create the tag or ignore if it exists
    db.execute(
        "INSERT OR IGNORE INTO tag (name) VALUES (?)", (name,)
    )
    # Grab the id of the tag
    tag_id = db.execute(
        "SELECT (id) FROM tag WHERE name = ?", (name,)
    ).fetchone()["id"]
    db.commit()
    return tag_id


def get_or_create_tags_from_string(tag_string):
    """
    Get or create tags from a string of space separated tags.

    Takes a string of space separated words. Each word is considered a tag.
    Returns a tuple containing ids of the tags in the database.

    If the tag does not exist in the database, it is created.

    :param tag_string: String of space separated words.
    :type tag_string: str

    :returns: Tuple of ids of the tags in the database
    :rtype: tuple
    """
    tag_names = tag_string.split(" ")
    return tuple([get_or_create_tag(t) for t in tag_names])

