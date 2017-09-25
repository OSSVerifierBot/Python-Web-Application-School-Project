"""Tests for delete_inator route."""
import json
import random

from http import HTTPStatus
from urllib.parse import urlparse

from utils import from_datetime


def test_login_required(app):
    """Redirect to login if we're not logged in."""
    rv = app.get("/delete/uuid-goes-here/")
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/login/"

    rv = app.get("/delete/uuid-goes-here/", follow_redirects=True)
    assert b"You must be logged in to access that page." in rv.data


def test_submit_invalid_methods(app):
    """Form submission doesn't work for invalid HTTP methods."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # HEAD and OPTIONS are implemented by Flask. No need to test those.

    # DELETE shouldn't work
    rv = app.delete("/delete/beep/")
    assert rv.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    # PUT shouldn't work
    rv = app.put("/delete/beep/")
    assert rv.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_load_page(app, inator_data, data_path):
    """Page loads if the user is logged in."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Save some random inators to the data path
    with open(data_path, "w") as data_file:
        json.dump({"inators": inator_data}, data_file, default=from_datetime)

    # Choose one inator at random
    i = random.choice(list(inator_data.values()))

    print(i)

    # Try loading its deletion page
    rv = app.get("/delete/{}/".format(i["ident"]))
    assert rv.status_code == HTTPStatus.OK

    # Check that the flashed message is present
    question = "Are you sure you want to delete {}?".format(i["name"])
    assert question.encode("ascii") in rv.data


def test_submit_valid(app, inator_data, data_path):
    """Submission works if URL is valid."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Create some random inator data and save it to the data file
    with open(data_path, "w") as data_file:
        json.dump({"inators": inator_data}, data_file, default=from_datetime)

    # Choose an inator at random
    i = random.choice(list(inator_data.values()))

    # Try deleting it
    rv = app.post("/delete/{}/".format(i["ident"]), follow_redirects=True)
    assert rv.status_code == HTTPStatus.OK

    # Check flashed message
    message = "Successfully deleted {} ({}).".format(i["name"], i["ident"])
    assert message.encode("ascii") in rv.data

    # Assert that it's actually gone from the list
    rv = app.get("/")
    assert i["name"].encode("ascii") not in rv.data
    assert i["ident"].encode("ascii") not in rv.data


def test_load_invalid(app, inator_data, data_path):
    """Redirected if the URL has an invalid UUID."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Save some random inator data to the data path
    with open(data_path, "w") as data_file:
        json.dump({"inators": inator_data}, data_file, default=from_datetime)

    # Assert that we're redirected to the right place
    rv = app.get("/delete/bleep-bloop-no-way-you-guys/")
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/"

    # Assert that we're flashed the correct message
    rv = app.get("/delete/bleep-bloop/", follow_redirects=True)
    assert b"No such inator with identifier bleep-bloop." in rv.data


def test_submit_invalid(app, inator_data, data_path):
    """Submission doesn't work if URL is invalid."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Save some random inator data to the data path
    with open(data_path, "w") as data_file:
        json.dump({"inators": inator_data}, data_file, default=from_datetime)

    # Try submitting a POST to delete something that doesn't exist
    rv = app.post("/delete/bleep-bloop-no-way-you-guys/")
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/"

    # Check flashed message
    rv = app.post("/delete/bleep-bloop/", follow_redirects=True)
    assert b"No such inator with identifier bleep-bloop." in rv.data


def test_load_invalid_no_data(app, inator_data, data_path):
    """Redirected if there's no data in the data file."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Try loading the page: There's nothing in the data file this time.
    rv = app.get("/delete/bleep-bloop-no-way-you-guys/")
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/"

    # Same deal -- check the flashed message
    rv = app.get("/delete/bleep-bloop/", follow_redirects=True)
    assert b"No such inator with identifier bleep-bloop." in rv.data
