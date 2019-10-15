import os
import uuid

from flask import Blueprint, send_from_directory, current_app

from flaskr.db import get_db


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
    return filename


def create_post_image_association(post_id, filename):
    """
    Create association of post id with image filename

    :param post_id: Id of the post for which the association shall be created
    :type post_id: int

    :param filename: Filename of the image which shall be associated with the
                     post. If the filename does not exist in the upload
                     directory of the current app, a `FileNotFoundError` is
                     raised.
    :type filename: string
    """
    if not os.path.exists(
            os.path.join(current_app.config["UPLOAD_DIR"], filename)):
        raise FileNotFoundError
    db = get_db()
    db.execute(
        "INSERT INTO post_image (post_id, filename)"
        " VALUES (?, ?)", (post_id, filename)
    )
    db.commit()


def get_image_of_post(post_id):
    """
    Get filename of image that is associated with post from DB

    Returns `None` is no association can be found.

    :param post_id: Id of the post for which the image filename should be
                    retrieved.
    :type post_id: int

    :returns: string or None
    """
    db = get_db()
    row = db.execute(
        "SELECT filename FROM post_image WHERE post_id = ?",
        (post_id,)
    ).fetchone()
    if row:
        return row["filename"]
    return None
