from flask import Blueprint, request, render_template, current_app

from flaskr.db import get_db
from flaskr.pagination import Pagination


bp = Blueprint("search", __name__, url_prefix="/search")


@bp.route("/")
def display_search_filtered_index():
    query = request.args["q"]
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
        " WHERE p.title LIKE ?"
        " GROUP BY p.id"
        " ORDER BY p.created DESC"
        " LIMIT ? OFFSET ?",
        ("%" + query + "%", pagination.items_per_page, pagination.item_offset)
    ).fetchall()
    return render_template(
        "blog/index.html", posts=posts, search=query, pagination=pagination)
