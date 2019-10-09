from flask import Blueprint, render_template

from flaskr.db import get_db


bp = Blueprint("search", __name__, url_prefix="/search")


@bp.route("<string:title>")
def display_search_filtered_index(title):
    return render_template("blog/index.html")
