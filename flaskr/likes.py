from flask import Blueprint, request, redirect, url_for, g

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("likes", __name__, url_prefix="/likes")


@bp.route("/create", methods=("POST",))
@login_required
def create():
    post_id = request.form["post_id"]
    user_id = g.user["id"]

    db = get_db()
    db.execute(
        "INSERT INTO like (user_id, post_id) "
        " VALUES (?, ?)", (user_id, post_id)
    )

    return redirect(url_for("blog.detail", id=post_id))
