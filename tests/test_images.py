import os
import shutil

import pytest
from flask import url_for


@pytest.fixture
def example_image_to_upload_dir(app):
    example_image_filename = "example.png"
    example_image_path = os.path.join(
        os.path.dirname(__file__), example_image_filename)
    shutil.copyfile(example_image_path,
                    os.path.join(app.config["UPLOAD_DIR"],
                                 example_image_filename))


def test_get_example_image_from_url(app, client, example_image_to_upload_dir):
    with app.app_context():
        example_image_filename = "example.png"
        assert example_image_filename in os.listdir(app.config["UPLOAD_DIR"])
        example_image_path = os.path.join(app.config["UPLOAD_DIR"],
                                          example_image_filename)
        with open(example_image_path, mode="rb") as f:
            example_image_content = f.read()

    with app.test_request_context():
        response = client.get(
            url_for("images.get", filename=example_image_filename))
        assert response.status_code == 200
        assert response.mimetype == "image/png"
        assert response.data == example_image_content
