import os
import shutil

import pytest
from flask import url_for

from flaskr import images


class ExampleImage(object):
    def __init__(self):
        self.filename = "example.png"
        self.path = os.path.join(
            os.path.dirname(__file__), self.filename)
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


def test_save_image_to_upload_dir(app):
    example_image = ExampleImage()
    with app.app_context():
        # File does not exist
        assert (example_image.filename
                not in os.listdir(app.config["UPLOAD_DIR"]))

        # Saving file
        images.save_image_to_upload_dir(content=example_image.content,
                                    filename=example_image.filename)

        # File exists
        assert (example_image.filename
                in os.listdir(app.config["UPLOAD_DIR"]))
        saved_image_path = os.path.join(app.config["UPLOAD_DIR"],
                                        example_image.filename)
        # File has correct content
        with open(saved_image_path, mode="rb") as f:
            saved_image_content = f.read()
        assert saved_image_content == example_image.content
