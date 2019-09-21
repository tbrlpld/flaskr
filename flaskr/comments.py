from flask import (
    Blueprint, flash, g, redirect, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.blog import get_post
from flaskr.db import get_db

bp = Blueprint("comments", __name__, url_prefix="/comments")


@bp.route("/create", methods=("POST",))
@login_required
def create():
    post = get_post(request.form["post_id"])
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
            (g.user["id"], post["id"], body)
        )
        db.commit()
    return redirect(url_for("blog.detail", id=post["id"]))
