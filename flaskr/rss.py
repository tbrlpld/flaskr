import io

from flask import Blueprint, send_file, render_template

from flaskr.db import get_db

bp = Blueprint("rss", __name__)


@bp.route("/feed.rss")
def send_feed():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, p.title, p.created, u.username"
        " FROM post p "
        " JOIN user u ON p.author_id = u.id"
        " ORDER BY p.id DESC"
    ).fetchall()
    return render_template("rss/feed.rss.j2", posts=posts)
