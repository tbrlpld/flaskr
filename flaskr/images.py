import os

from flask import Blueprint, send_from_directory, current_app


bp = Blueprint("images", __name__, url_prefix="/images")


@bp.route("/<string:filename>")
def get(filename):
    return send_from_directory(current_app.config['UPLOAD_DIR'],
                               filename, as_attachment=False)


def save_image_to_upload_dir(content, filename):
    save_image_path = os.path.join(current_app.config["UPLOAD_DIR"], filename)
    with open(save_image_path, "wb") as f:
        f.write(content)
