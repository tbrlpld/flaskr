from flask import Blueprint, render_template

from flaskr.db import get_db


bp = Blueprint("tags", __name__, url_prefix="/tags")


def get_or_create_tag(name):
    """
    Get or create a tag with the given name and return the tag id

    :param name: Name or word that the tag is made of
    :type name: string

    :returns: Id of the tag created in the database or None if id not found.
    :rtype: int or None
    """
    db = get_db()
    name = name.strip()
    if name:
        # Create the tag or ignore if it exists
        db.execute("INSERT OR IGNORE INTO tag (name) VALUES (?)", (name,))
        db.commit()
        # Grab the id of the tag
        tag_id = db.execute(
            "SELECT (id) FROM tag WHERE name = ?", (name,)
        ).fetchone()["id"]
        return tag_id
    return None


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
    return tuple([get_or_create_tag(t) for t in tag_names if t.strip()])


def get_tags_for_post(post_id):
    """
    Get the tag ids associated with the post.

    :param post_id: Id of the post for which the tags should be retrieved.
    :type post_id: int

    :returns: List of tag names which are associated with the post.
    :rtype: list
    """
    db = get_db()
    associated_tag_rows = db.execute(
        "SELECT (t.name) FROM tag t JOIN post_tag pt ON t.id = pt.tag_id"
        " WHERE pt.post_id = ?",
        (post_id,)
    ).fetchall()
    return [row["name"] for row in associated_tag_rows]


def associate_tag_with_post(tag_id, post_id):
    """
    Create an association/relationship between a given tag id and post id.

    :param tag_id: Id of the tag which shall be associated with the post.
    :type tag_id: int

    :param post_id: Id of the post with which the tag shall be associated.
    :type post_id: int
    """
    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO post_tag (tag_id, post_id)"
        " VALUES (?, ?)", (tag_id, post_id)
    )
    db.commit()


def disassociate_tag_from_post(tag_id, post_id):
    """
    Remove an association/relationship between a given tag id and post id.

    :param tag_id: Id of the tag which shall be disassociated from the post.
    :type tag_id: int

    :param post_id: Id of the post from which the tag shall be disassociated.
    :type post_id: int
    """
    db = get_db()
    db.execute(
        "DELETE FROM post_tag WHERE post_id = ? AND tag_id = ?",
        (post_id, tag_id)
    )
    db.commit()


def remove_tag_associations_for_post(post_id):
    """
    Remove all tag association for a post.

    :param post_id: Id of the post for which the associations should be removed
    :type post_id: int
    """
    db = get_db()
    db.execute("DELETE FROM post_tag WHERE post_id = ?", (post_id,))
    db.commit()


def update_tag_associations_for_post(tag_string, post_id):
    """
    Update tag associations for a post.

    Tags are given as space separated words in a string. If a tag does not
    exist in the DB it is created first.

    Associations in the DB with tags that are not contained in the `tag_string`
    are removed. This allows to delete all tag association by passing an empty
    string as the `tag_string`.

    :param tag_string: String containing the tags to be associated with the
                       post.
    :type tag_string: str

    :param post_id: Id of the post the tags shall be associated with.
    :type post_id: int
    """
    current_associated_tags = get_tags_for_post(post_id)
    desired_associated_tags = tag_string.strip().split()

    tags_to_add = [tag for tag in desired_associated_tags
                   if tag not in current_associated_tags]
    tags_to_remove = [tag for tag in current_associated_tags
                      if tag not in desired_associated_tags]

    for tag in tags_to_add:
        tag_id = get_or_create_tag(tag)
        associate_tag_with_post(tag_id=tag_id, post_id=post_id)

    for tag in tags_to_remove:
        tag_id = get_or_create_tag(tag)
        disassociate_tag_from_post(tag_id=tag_id, post_id=post_id)


@bp.route("/<string:tag>")
def display_tagged_posts(tag):
    db = get_db()
    posts = db.execute(
        "SELECT p.id, p.title, p.body, p.created, p.author_id, u.username"
        # " GROUP_CONCAT(t.name, ' ') AS tag_string"
        " FROM post p"
        " JOIN user u ON p.author_id = u.id"
        " JOIN post_tag pt ON p.id = pt.post_id"
        " JOIN tag t ON pt.tag_id = t.id"
        " WHERE t.name = ?"
        " ORDER BY p.created DESC",
        (tag,)
    ).fetchall()
    return render_template("blog/index.html", posts=posts, tag=tag)
