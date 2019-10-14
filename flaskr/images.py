from flask import Blueprint, send_from_directory, current_app


bp = Blueprint("images", __name__, url_prefix="/images")


@bp.route("/<string:filename>")
def get(filename):
    return send_from_directory(current_app.config['UPLOAD_DIR'],
                               filename, as_attachment=False)
