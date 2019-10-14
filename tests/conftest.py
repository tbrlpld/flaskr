import os
import shutil
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    upload_dir = tempfile.mkdtemp()

    app = create_app({
        "TESTING": True,
        "DATABASE": db_path,
        "UPLOAD_DIR": upload_dir
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    example_image_filename = "example.png"
    example_image_path = os.path.join(
        os.path.dirname(__file__), example_image_filename)
    shutil.copyfile(example_image_path,
                    os.path.join(app.config["UPLOAD_DIR"],
                                 example_image_filename))

    yield app

    os.close(db_fd)
    os.unlink(db_path)
    shutil.rmtree(upload_dir)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login",
            data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
