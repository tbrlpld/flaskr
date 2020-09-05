Flaskr
======

This is my working repository for the [Flask tutorial](https://flask.palletsprojects.com/en/1.1.x/tutorial/#tutorial).

The basic functionality of the blog was created by following along the tutorial snippets.

My own work really starts with the implementation of the features listed in the [Keep Developing Section](https://flask.palletsprojects.com/en/1.1.x/tutorial/next/) of the tutorial. The added features are: detail post view, likes, comments, tags, title search, pagination, image upload, markdown formatting and RSS feed.

## Development

### Installation

Clone the repo to a local directory.

```shell
$ git clone git@github.com:tbrlpld/flaskr.git
```

Change in to the `flaskr` directory and create a virtual environment and activate it.

```shell
$ cd flaskr
$ python -m venv .venv
$ source .venv/bin/activate
```

Install the app (in editable mode) and its dependencies.

```shell
$ python -m pip install -e '.[dev]'
```

Initialize the database.

```shell
$ export FLASK_APP=flaskr
$ export FLASK_ENV=development
$ flask init-db
```

Run the app.

```shell
$ flask run
```

### Tests

To run the tests just run `pytest` in the project directory.
```shell
$ pytest
```

You can also run the tests and get a coverage report.
```shell
$ pytest --cov
```