from sqlite3 import IntegrityError

from flask import Blueprint, request, redirect, url_for, g
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("likes", __name__, url_prefix="/likes")


def get_users_liking_post(post_id):
    db = get_db()
    likes = db.execute(
        "SELECT post_id, user_id FROM like WHERE post_id = ?",
        (post_id,)
    ).fetchall()
    user_ids = [like["user_id"] for like in likes]
    return user_ids


@bp.route("/create", methods=("POST",))
@login_required
def create():
    post_id = request.form["post_id"]
    user_id = g.user["id"]

    db = get_db()
    try:
        db.execute(
            "INSERT INTO like (user_id, post_id) "
            " VALUES (?, ?)",
            (user_id, post_id)
        )
        db.commit()
    except IntegrityError:
        abort(403, "Like already exists")

    return redirect(url_for("blog.detail", id=post_id))


@bp.route("/delete", methods=("POST",))
@login_required
def delete():
    post_id = request.form["post_id"]
    # Grabbing the logged in user. It is not possible trying to remove other
    # users likes.
    user_id = g.user["id"]

    db = get_db()
    db.execute(
        "DELETE FROM like WHERE user_id = ? AND post_id = ?",
        (user_id, post_id)
    )
    db.commit()

    return redirect(url_for("blog.detail", id=post_id))
