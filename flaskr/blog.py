from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.comments import get_comments_for_post
from flaskr.db import get_db
from flaskr.likes import get_users_liking_post
from flaskr.tags import get_or_create_tags_from_string

bp = Blueprint("blog", __name__)


def get_post(id, check_author=True):
    post = get_db().execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ?",
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {} does not exist.".format(id))

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("blog/index.html", posts=posts)


@bp.route("/<int:id>/detail", methods=("GET",))
def detail(id):
    """
    Display a detail page with only one post
    """
    post = get_post(id, check_author=False)
    comments = get_comments_for_post(post_id=id)
    users_likes = get_users_liking_post(post_id=id)

    # Post existence is already checked in get_post
    return render_template(
        "blog/detail.html",
        post=post,
        comments=comments,
        users_likes=users_likes
    )


def create_post(title, body):
    db = get_db()
    db.execute(
        "INSERT INTO post (title, body, author_id)"
        " VALUES (?, ?, ?)",
        (title, body, g.user["id"])
    )
    db.commit()


def update_post(id, title, body):
    db = get_db()
    db.execute(
        "UPDATE post SET title = ?, body = ?"
        " WHERE id = ?",
        (title, body, id)
    )
    db.commit()


def create_or_update_post(id=None):
    post = None
    if id:
        post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        tag_string = request.form.get("tags", None)
        error = None

        if tag_string:
            tag_ids = get_or_create_tags_from_string(tag_string)

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            if id:
                update_post(id, title, body)
            else:
                create_post(title, body)
            return redirect(url_for("blog.index"))

    return render_template("blog/create_or_update.html", post=post)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    return create_or_update_post()


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    return create_or_update_post(id=id)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)  # This is to check permissions
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id, ))
    db.commit()
    return redirect(url_for("blog.index"))
