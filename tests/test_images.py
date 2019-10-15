import os
import shutil

import pytest
from flask import url_for
from werkzeug.datastructures import FileStorage

from flaskr import images
from flaskr.db import get_db


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
        saved_filename = images.save_image_to_upload_dir(
            filestrorage_obj=filestorage,
            _filename=example_image.filename
        )

        # File exists
        assert saved_filename == example_image.filename
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
        saved_filename = images.save_image_to_upload_dir(
            filestrorage_obj=filestorage)

        uploaded_files = os.listdir(app.config["UPLOAD_DIR"])
        assert len(uploaded_files) == 1
        # The saved file does not have the example filename!
        assert (example_image.filename
                not in uploaded_files)

        assert uploaded_files[0] == saved_filename
        _, saved_fileextension = os.path.splitext(saved_filename)
        assert saved_fileextension == ".png"
        # But the content is correct
        saved_image_path = os.path.join(app.config["UPLOAD_DIR"],
                                        saved_filename)
        with open(saved_image_path, mode="rb") as f:
            saved_image_content = f.read()
        assert saved_image_content == example_image.content


def test_post_image_association_none_exising_file(app):
    with app.app_context():
        # To create an association, the file has to exist in the upload
        # directory or an Exception is raised
        uploaded_files = os.listdir(app.config["UPLOAD_DIR"])
        assert len(uploaded_files) == 0

        filenotfound_raised = False
        try:
            images.create_post_image_association(
                post_id=1, filename="example.png")
        except FileNotFoundError:
            filenotfound_raised = True
        assert filenotfound_raised


def test_new_post_image_association(app, example_image_to_upload_dir):
    with app.app_context():
        images.create_post_image_association(
            post_id=1, filename="example.png")
        db = get_db()
        result = db.execute(
            "SELECT post_id, filename FROM post_image WHERE post_id = 1"
        ).fetchone()
        assert result["post_id"] == 1
        assert result["filename"] == "example.png"


def test_get_image_of_post(app, example_image_to_upload_dir):
    example_image = ExampleImage()
    with app.app_context():
        response_before_association = images.get_image_of_post(post_id=1)
        assert response_before_association is None

        images.create_post_image_association(
            post_id=1, filename=example_image.filename)
        image_filename = images.get_image_of_post(post_id=1)
        assert image_filename == example_image.filename


def test_delete_post_image_associations_of_post(
        app, example_image_to_upload_dir):
    example_image = ExampleImage()
    with app.app_context():
        images.create_post_image_association(
            post_id=1, filename=example_image.filename)
        image_filename = images.get_image_of_post(post_id=1)
        assert image_filename == example_image.filename
        assert image_filename in os.listdir(app.config["UPLOAD_DIR"])

        images.delete_post_image_associations_of_post(post_id=1)
        assert images.get_image_of_post(post_id=1) is None
        assert image_filename not in os.listdir(app.config["UPLOAD_DIR"])


def test_save_image_and_create_image_association(app):
    example_image = ExampleImage()
    filestorage = FileStorage(
        stream=example_image.fileobject,
        filename=example_image.filename)
    with app.app_context():
        # File does not exist
        assert len(os.listdir(app.config["UPLOAD_DIR"])) == 0

        # Saving file
        images.save_image_and_create_or_update_post_association(
            image=filestorage, post_id=1)

        uploaded_files = os.listdir(app.config["UPLOAD_DIR"])
        assert len(uploaded_files) == 1
        associated_image_filename = images.get_image_of_post(post_id=1)
        assert associated_image_filename is not None
        assert associated_image_filename in uploaded_files


def test_save_image_and_update_image_association(app):
    example_image = ExampleImage()
    filestorage = FileStorage(
        stream=example_image.fileobject,
        filename=example_image.filename)
    with app.app_context():
        # File does not exist
        assert len(os.listdir(app.config["UPLOAD_DIR"])) == 0

        # Saving file for the first time
        images.save_image_and_create_or_update_post_association(
            image=filestorage, post_id=1)

        uploaded_files = os.listdir(app.config["UPLOAD_DIR"])
        assert len(uploaded_files) == 1
        associated_image_filename_1 = images.get_image_of_post(post_id=1)
        assert associated_image_filename_1 is not None
        assert associated_image_filename_1 in uploaded_files

        # Saving the image again
        images.save_image_and_create_or_update_post_association(
            image=filestorage, post_id=1)
        uploaded_files = os.listdir(app.config["UPLOAD_DIR"])
        # There should still be only one file in the upload folder, because
        # the first one should be deleted.
        assert len(uploaded_files) == 1
        associated_image_filename_2 = images.get_image_of_post(post_id=1)
        # The name of the associated file should have changed and that should
        # the uploaded file.
        assert associated_image_filename_2 is not associated_image_filename_1
        assert associated_image_filename_2 in uploaded_files


@pytest.mark.parametrize(("path", "post_id"), (
    ("/create", 2),
    ("/1/update", 1)
))
def test_post_view_saves_files_and_creates_association(
        app, client, auth, path, post_id):
    auth.login()
    example_image = ExampleImage()
    with app.test_request_context():
        # No uploads yet
        uploaded_files = os.listdir(app.config["UPLOAD_DIR"])
        assert len(uploaded_files) == 0

        form_data = {
            "title": "post with image",
            "body": "some body",
            "image": [(example_image.fileobject, example_image.filename)]
        }
        response = client.post(
            path, data=form_data, follow_redirects=True)
        assert response.status_code == 200

        # The associated files should be in the uploads
        associated_image_filename = images.get_image_of_post(post_id=post_id)
        assert associated_image_filename is not None
        uploaded_files = os.listdir(app.config["UPLOAD_DIR"])
        assert len(uploaded_files) == 1
        assert associated_image_filename in uploaded_files
        # The associated file should have the example files content
        saved_image_path = os.path.join(app.config["UPLOAD_DIR"],
                                        associated_image_filename)
        with open(saved_image_path, mode="rb") as f:
            saved_image_content = f.read()
        assert saved_image_content == example_image.content


def test_sending_empty_value_for_image_to_create_post_view(
        app, client, auth):
    auth.login()
    with app.test_request_context():
        # No uploads yet
        uploaded_files = os.listdir(app.config["UPLOAD_DIR"])
        assert len(uploaded_files) == 0

        form_data = {
            "title": "post with image",
            "body": "some body",
            "image": []
        }
        response = client.post(
            url_for("blog.create"), data=form_data, follow_redirects=True)
        assert response.status_code == 200

        uploaded_files = os.listdir(app.config["UPLOAD_DIR"])
        assert len(uploaded_files) == 0
        associated_image_filename = images.get_image_of_post(post_id=2)
        assert associated_image_filename is None


def test_file_input_for_image_on_post_create_view(app, client, auth):
    auth.login()
    with app.test_request_context():
        response = client.get(url_for("blog.create"))
        assert b'<input type="file" name="image">' in response.data
        # The enctype is required by flask to have data actually being attached
        # to the request object.
        assert b'enctype="multipart/form-data"' in response.data


def test_file_input_for_image_on_post_update_view(app, client, auth):
    auth.login()
    with app.test_request_context():
        response = client.get(url_for("blog.update", id=1))
        assert b'<input type="file" name="image">' in response.data
        # The enctype is required by flask to have data actually being attached
        # to the request object.
        assert b'enctype="multipart/form-data"' in response.data


def test_image_url_on_post_detail_page(app, client, auth):
    auth.login()
    example_image = ExampleImage()
    with app.test_request_context():
        # Adding image to post 1
        form_data = {
            "title": "post with image",
            "body": "some body",
            "image": [(example_image.fileobject, example_image.filename)]
        }
        response = client.post(
            "/1/update", data=form_data, follow_redirects=True)
        assert response.status_code == 200

        # The associated files should be in the uploads
        associated_image_filename = images.get_image_of_post(post_id=1)
        assert associated_image_filename is not None

        response = client.get("/1/detail")
        assert bytes(
            associated_image_filename, encoding="utf8") in response.data


def test_delete_image_association_via_url(app, client, auth):
    auth.login()
    example_image = ExampleImage()
    with app.app_context():
        # Adding image to post 1
        form_data = {
            "title": "post with image",
            "body": "some body",
            "image": [(example_image.fileobject, example_image.filename)]
        }
        response = client.post(
            "/1/update", data=form_data, follow_redirects=True)
        assert response.status_code == 200
        associated_image_filename = images.get_image_of_post(post_id=1)
        assert associated_image_filename is not None

        # Removing association via URL
        response = client.post("/images/remove-associations/1")
        assert response.headers["Location"] == "http://localhost/1/update"
        associated_image_filename = images.get_image_of_post(post_id=1)
        assert associated_image_filename is None


def test_post_with_image_shows_image_and_image_delete_link_on_update_page(
        app, client, auth):
    auth.login()
    example_image = ExampleImage()
    with app.test_request_context():
        # Adding image to post 1
        form_data = {
            "title": "post with image",
            "body": "some body",
            "image": [(example_image.fileobject, example_image.filename)]
        }
        response = client.post(
            "/1/update", data=form_data, follow_redirects=True)
        assert response.status_code == 200

        # The associated files should be in the uploads
        associated_image_filename = images.get_image_of_post(post_id=1)
        assert associated_image_filename is not None

        response = client.get("/1/update")
        assert bytes(
            associated_image_filename, encoding="utf8") in response.data
        delete_url = url_for("images.delete_post_image_association_of_post_per_url",
                             post_id=1)
        assert bytes(delete_url, encoding="utf8") in response.data
