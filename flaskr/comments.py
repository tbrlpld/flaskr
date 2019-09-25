from flask import (
    Blueprint, flash, g, redirect, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("comments", __name__, url_prefix="/comments")


def get_comments_for_post(post_id=None):
    """
    Get all comments for a post with given id.
    """
    if post_id is not None:
        db = get_db()
        comments = db.execute(
            "SELECT c.id, body, created, post_id, author_id, username"
            " FROM comment c JOIN user u ON c.author_id = u.id"
            " WHERE post_id = ?",
            (post_id,)
        ).fetchall()
        return comments


@bp.route("/create", methods=("POST",))
@login_required
def create():
    post_id = request.form["post_id"]
    body = request.form["body"]
    error = None

    if not body:
        error = "Comment text required."

    if error is not None:
        flash(error)
    else:
        # Create the comment in the db
        db = get_db()
        db.execute(
            "INSERT INTO comment (author_id, post_id, body)"
            " VALUES (?, ?, ?)",
            (g.user["id"], post_id, body)
        )
        db.commit()
    return redirect(url_for("blog.detail", id=post_id))


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    db = get_db()

    # Only the author of the *post* can delete comments to that post.
    post_info = db.execute(
        "SELECT p.author_id, p.id "
        "FROM comment c JOIN post p"
        " WHERE c.id = ?", (id,)
    ).fetchone()
    if not post_info["author_id"] == g.user["id"]:
        abort(403)  # Forbidden is returned

    db.execute("DELETE FROM comment WHERE id = ?", (id, ))
    db.commit()

    return redirect(url_for("blog.detail", id=post_info["id"]))
