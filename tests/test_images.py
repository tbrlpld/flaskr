import os
import shutil

import pytest
from flask import url_for
from werkzeug.datastructures import FileStorage

from flaskr import images


class ExampleImage(object):
    def __init__(self):
        self.filename = "example.png"
        self.path = os.path.join(
            os.path.dirname(__file__), self.filename)
        self.fileobject = open(self.path, mode="rb")
        with open(self.path, mode="rb") as f:
            self.content = f.read()


@pytest.fixture
def example_image_to_upload_dir(app):
    example_image = ExampleImage()
    shutil.copyfile(example_image.path,
                    os.path.join(app.config["UPLOAD_DIR"],
                                 example_image.filename))


def test_get_example_image_from_url(app, client, example_image_to_upload_dir):
    example_image = ExampleImage()
    with app.app_context():
        assert example_image.filename in os.listdir(app.config["UPLOAD_DIR"])

    with app.test_request_context():
        response = client.get(
            url_for("images.get", filename=example_image.filename))
        assert response.status_code == 200
        assert response.mimetype == "image/png"
        assert response.data == example_image.content


def test_get_random_string():
    first_string = images.get_random_string()
    second_string = images.get_random_string()
    assert first_string != second_string
    assert "-" not in second_string
    assert "." not in second_string


def test_save_image_to_upload_dir_with_given_filename(app):
    example_image = ExampleImage()
    # The werkzeug filestorage type is how that uploaded image will be attached
    # to the request by Flask. The FileStorage object already comes with a save
    # method. It makes sense to utilize that.
    filestorage = FileStorage(
        stream=example_image.fileobject,
        filename=example_image.filename)
    with app.app_context():
        # File does not exist
        assert (example_image.filename
                not in os.listdir(app.config["UPLOAD_DIR"]))

        # Saving file
        images.save_image_to_upload_dir(filestrorage_obj=filestorage,
                                        _filename=example_image.filename)

        # File exists
        assert (example_image.filename
                in os.listdir(app.config["UPLOAD_DIR"]))
        saved_image_path = os.path.join(app.config["UPLOAD_DIR"],
                                        example_image.filename)
        # File has correct content
        with open(saved_image_path, mode="rb") as f:
            saved_image_content = f.read()
        assert saved_image_content == example_image.content


def test_save_image_to_upload_dir_without_given_filename(app):
    example_image = ExampleImage()
    filestorage = FileStorage(
        stream=example_image.fileobject,
        filename=example_image.filename)
    with app.app_context():
        # File does not exist
        uploaded_files = os.listdir(app.config["UPLOAD_DIR"])
        assert (example_image.filename
                not in uploaded_files)
        assert len(uploaded_files) == 0

        # Saving file
        images.save_image_to_upload_dir(filestrorage_obj=filestorage)

        uploaded_files = os.listdir(app.config["UPLOAD_DIR"])
        assert len(uploaded_files) == 1
        # The saved file does not have the example filename!
        assert (example_image.filename
                not in uploaded_files)

        saved_filename = uploaded_files[0]
        _, saved_fileextension = os.path.splitext(saved_filename)
        assert saved_fileextension == ".png"
        # But the content is correct
        saved_image_path = os.path.join(app.config["UPLOAD_DIR"],
                                        saved_filename)
        with open(saved_image_path, mode="rb") as f:
            saved_image_content = f.read()
        assert saved_image_content == example_image.content
