"""Tests for list_inators route."""
import json

from http import HTTPStatus
from urllib.parse import urlparse

from utils import from_datetime


def test_login_required(app):
    """Redirect to login if we're not logged in."""
    # Visit the home page
    rv = app.get("/")

    # Make sure we're redirected to /login/
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/login/"

    # Make sure we see the flashed message
    rv = app.get("/", follow_redirects=True)
    assert b"You must be logged in to access that page." in rv.data


def test_submit_invalid_methods(app):
    """Form submission doesn't work for invalid HTTP methods."""
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # HEAD and OPTIONS are implemented by Flask. No need to test those.

    # DELETE shouldn't work
    rv = app.delete("/")
    assert rv.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    # PUT shouldn't work
    rv = app.put("/")
    assert rv.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    # POST shouldn't work
    rv = app.post("/")
    assert rv.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_empty_data(app):
    """Everything's OK if we are logged in and the data file is empty."""
    # Set the session username, effectively logging in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Try visiting the page
    rv = app.get("/")
    assert rv.status_code == HTTPStatus.OK
    assert b"List of Inators" in rv.data   # Make sure we've pulled up the page
    assert b"/view/" not in rv.data        # It shouldn't have any inator links


def test_a_few_inators(app, data_path, inator_data):
    """Ensure we see our inators."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Create a data file of inators where the app expects to find it.
    with open(data_path, "w") as data_file:
        json.dump({"inators": inator_data}, data_file, default=from_datetime)

    # Load the page
    rv = app.get("/")
    assert rv.status_code == HTTPStatus.OK

    # We should see all five of the randomly generated inators in the
    # page content
    count = 0
    for name in inator_data:
        assert name.encode("ascii") in rv.data
        count += 1
    assert count == 5


def test_inators_sorted(app, data_path, inator_data):
    """Ensure inators are sorted by name, then by condition."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Save some random inators to the data file
    with open(data_path, "w") as data_file:
        json.dump({"inators": inator_data}, data_file, default=from_datetime)

    # Load the list page
    rv = app.get("/")
    assert rv.status_code == HTTPStatus.OK

    # Sort the inators by name, then by condition.
    inators = sorted(inator_data.values(), key=lambda x: x["name"])
    inators = sorted(inators, key=lambda x: x["condition"], reverse=True)

    # Determine the index at which we see each UUID
    indices = [rv.data.index(i["ident"].encode("ascii")) for i in inators]

    # We should see the inators in order: First grouped by condition,
    # then in order by name for each condition
    count = 0
    for i, j in zip(indices, indices[1:]):
        assert i < j
        count += 1
    assert count == 4
