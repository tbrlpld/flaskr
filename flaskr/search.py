from flask import Blueprint, request, render_template

from flaskr.db import get_db


bp = Blueprint("search", __name__, url_prefix="/search")


@bp.route("/")
def display_search_filtered_index():
    query = request.args["q"]
    db = get_db()
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
        " ORDER BY p.created DESC",
        ("%" + query + "%",)
    ).fetchall()
    return render_template("blog/index.html", posts=posts, search=query)
