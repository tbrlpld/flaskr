from flask import url_for

import os


def test_get_example_image_from_url(app, client):
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
