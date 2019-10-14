import os
import uuid

from flask import Blueprint, send_from_directory, current_app


bp = Blueprint("images", __name__, url_prefix="/images")


@bp.route("/<string:filename>")
def get(filename):
    return send_from_directory(current_app.config['UPLOAD_DIR'],
                               filename, as_attachment=False)


def get_random_string():
    """Helper function returning a random uuid without the dashes"""
    return uuid.uuid4().hex


def save_image_to_upload_dir(filestrorage_obj, _filename=None):
    """
    Save the filestorage object as a file in the upload directory

    The file is saved with a random filename. The private `_filename` argument
    can be used during testing to force the file being saved with a defined
    filename.

    The random filename will have the same fileextension as the file extension
    on the client. The random filename is based on UUID which should make
    name clashes basically impossible.

    :param filestorage_obj: FileStorage object that is attached to the request
                            when uploaded.
    :type filestrorage_obj: werkzeug.datastructures.FileStorage

    :param _filename: Private argument for testing to override the randomly
                      generated filename
    :type filename: string
    """
    _, extension = os.path.splitext(filestrorage_obj.filename)
    filename = _filename or (get_random_string() + extension)
    save_image_path = os.path.join(
        current_app.config["UPLOAD_DIR"], filename)
    filestrorage_obj.save(dst=save_image_path)
