from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    current_app
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.comments import get_comments_for_post
from flaskr.db import get_db
from flaskr.images import save_image_and_create_or_update_post_association
from flaskr.likes import get_users_liking_post
from flaskr.pagination import Pagination
from flaskr.tags import update_tag_associations_for_post

bp = Blueprint("blog", __name__)


def get_post(id, check_author=True):
    post = get_db().execute(
        "SELECT p.id, p.title, p.body, p.created, p.author_id, u.username,"
        " GROUP_CONCAT(t.name, ' ') AS tag_string"
        " FROM post p"
        " JOIN user u ON p.author_id = u.id"
        # LEFT JOIN makes the existence of values in the right table optional!
        " LEFT JOIN post_tag pt ON p.id = pt.post_id"
        " LEFT JOIN tag t ON pt.tag_id = t.id"
        " WHERE p.id = ?"
        " GROUP BY p.id",
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
    post_count = db.execute("SELECT COUNT() FROM post").fetchone()[0]
    page = int(request.args.get("page", default="1"))
    pagination = Pagination(
        total_items=post_count,
        items_per_page=current_app.config["POSTS_PER_PAGE"],
        current_page=page)
    posts = db.execute(
        "SELECT p.id, p.title, p.body, p.created, p.author_id, u.username,"
        " GROUP_CONCAT(t.name, ' ') AS tag_string"
        " FROM post p"
        " JOIN user u ON p.author_id = u.id"
        # LEFT JOIN makes the existence of values in the right table optional!
        " LEFT JOIN post_tag pt ON p.id = pt.post_id"
        " LEFT JOIN tag t ON pt.tag_id = t.id"
        " GROUP BY p.id"
        " ORDER BY p.id DESC"
        " LIMIT ? OFFSET ?",
        (pagination.items_per_page, pagination.item_offset)
    ).fetchall()
    return render_template(
        "blog/index.html", posts=posts, pagination=pagination)


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


def create_post(title, body, author_id):
    """
    Create post with given title and body in the db.

    :param title: Title of the post
    :type title: str

    :param body: Body text of the post
    :type body: str

    :param author_id: User id of the author of the post
    :type author_id: int

    :returns: Id of the post created in the db
    :rtype: int
    """
    db = get_db()
    cursor = db.execute(
        "INSERT INTO post (title, body, author_id)"
        " VALUES (?, ?, ?)",
        (title, body, author_id)
    )
    db.commit()
    return cursor.lastrowid


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
        post = get_post(id)  # This is also to check existence and ownership

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        tag_string = request.form.get("tags", "")
        image = request.files.get("image", None)
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            if id:
                update_post(id, title, body)
            else:
                id = create_post(title, body, g.user["id"])
            update_tag_associations_for_post(tag_string=tag_string, post_id=id)
            if image:
                save_image_and_create_or_update_post_association(
                    image=image,
                    post_id=id
                )
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
    get_post(id)  # This is to check  existence and ownership
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id, ))
    db.commit()
    update_tag_associations_for_post(tag_string="", post_id=id)
    return redirect(url_for("blog.index"))
