"""Tests for view_inator route."""
import json
import random

from http import HTTPStatus
from urllib.parse import urlparse

from utils import from_datetime


def test_login_required(app):
    """Redirect to login if we're not logged in."""
    rv = app.get("/view/uuid-goes-here/")
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/login/"

    rv = app.get("/view/uuid-goes-here/", follow_redirects=True)
    assert b"You must be logged in to access that page." in rv.data


def test_submit_invalid_methods(app):
    """Form submission doesn't work for invalid HTTP methods."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # HEAD and OPTIONS are implemented by Flask. No need to test those.

    # DELETE doesn't work
    rv = app.delete("/view/beep/")
    assert rv.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    # PUT doesn't work
    rv = app.put("/view/beep/")
    assert rv.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    # POST doesn't work
    rv = app.post("/view/beep/")
    assert rv.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_load_page(app, inator_data, data_path):
    """Page loads if the user is logged in."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Save some random inators to the data file
    with open(data_path, "w") as data_file:
        json.dump({"inators": inator_data}, data_file, default=from_datetime)

    # Choose an inator at random
    i = random.choice(list(inator_data.values()))

    # Try viewing it
    rv = app.get("/view/{}/".format(i["ident"]))
    assert rv.status_code == HTTPStatus.OK
    assert "Details for {}".format(i["name"]).encode("ascii") in rv.data

    # Make sure we see all the details for the inator on the page
    assert i["ident"].encode("ascii") in rv.data
    assert i["name"].encode("ascii") in rv.data
    assert i["location"].encode("ascii") in rv.data
    assert i["description"].encode("ascii") in rv.data
    assert i["added"].strftime("%Y-%m-%d %H:%M:%S").encode("ascii") in rv.data
    assert i["condition"].name.encode("ascii") in rv.data


def test_load_invalid(app, inator_data, data_path):
    """Redirected if the URL has an invalid UUID."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Save some random inators to the data file
    with open(data_path, "w") as data_file:
        json.dump({"inators": inator_data}, data_file, default=from_datetime)

    # Assert that we're redirected to the right place
    rv = app.get("/view/bleep-bloop-no-way-you-guys/")
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/"

    # Assert that we're flashed the correct message
    rv = app.get("/view/bleep-bloop/", follow_redirects=True)
    assert b"No such inator with identifier bleep-bloop." in rv.data


def test_load_invalid_no_data(app, inator_data, data_path):
    """Redirected if there's no data in the data file."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Working with an empty data file this time

    # Assert that we're redirected to the right place
    rv = app.get("/view/bleep-bloop-no-way-you-guys/")
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/"

    # Assert that we're flashed the correct message
    rv = app.get("/view/bleep-bloop/", follow_redirects=True)
    assert b"No such inator with identifier bleep-bloop." in rv.data
