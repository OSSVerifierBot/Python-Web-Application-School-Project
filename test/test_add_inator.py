"""Tests for add_inator route."""
import json

from http import HTTPStatus
from urllib.parse import urlparse

from utils import from_datetime


def test_login_required(app):
    """Redirect to login if we're not logged in."""
    # Perform a GET and check that we're redirected properly
    rv = app.get("/add/")
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/login/"

    # Perform another GET and follow the redirect this time
    rv = app.get("/add/", follow_redirects=True)
    assert b"You must be logged in to access that page." in rv.data


def test_load_page(app):
    """Page loads if the user is logged in."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Load the page
    rv = app.get("/add/")
    assert rv.status_code == HTTPStatus.OK
    assert b"Add a New Inator" in rv.data


def test_submit_invalid_methods(app):
    """Form submission doesn't work for invalid HTTP methods."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # HEAD and OPTIONS are implemented by Flask. No need to test those.

    # DELETE shouldn't work
    rv = app.delete("/add/")
    assert rv.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    # PUT shouldn't work either
    rv = app.put("/add/")
    assert rv.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_submit_valid_form(app):
    """Form submission works for valid forms."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Submit a valid form, following redirects
    rv = app.post("/add/", data={
        "name": "Beep-inator",
        "location": "Upstairs computer science",
        "condition": 5,
        "description": "Someone needs to check the battery on their UPS" +
                       "or I am going to go insane."
    }, follow_redirects=True)

    # We should be redirected back to the home page
    assert rv.status_code == HTTPStatus.OK
    assert b"List of Inators" in rv.data

    # The new -inator should be present
    assert b"Beep-inator" in rv.data

    # Check that we see our flashed message.
    assert b"Successfully added Beep-inator." in rv.data


def test_submit_valid_check_redirect(app):
    """Check redirection for correct form submission."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Submit a valid form, don't follow redirects
    rv = app.post("/add/", data={
        "name": "Beep-inator",
        "location": "Upstairs computer science",
        "condition": 5,
        "description": "Someone needs to check the battery on their UPS" +
                       "or I am going to go insane."
    })

    # Check that the redirection is what we expect
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/"


def test_submit_valid_form_data_exists(app, inator_data, data_path):
    """Form submission works for valid forms when inators already exist."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Add some random inators to the data file
    with open(data_path, "w") as data_file:
        json.dump({"inators": inator_data}, data_file, default=from_datetime)

    # Submit a valid inator
    rv = app.post("/add/", data={
        "name": "Beep-inator",
        "location": "Upstairs computer science",
        "condition": 5,
        "description": "Someone needs to check the battery on their UPS" +
                       "or I am going to go insane."
    }, follow_redirects=True)

    # We should be redirected back to the home page
    assert rv.status_code == HTTPStatus.OK
    assert b"List of Inators" in rv.data

    # The new -inator should be present
    assert b"Beep-inator" in rv.data

    # So should all the old inators
    for ident, inator in inator_data.items():
        assert ident.encode("ascii") in rv.data
        assert inator["name"].encode("ascii") in rv.data


def test_submit_missing_field(app):
    """Form validates fields."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Post a form with a missing field
    rv = app.post("/add/", data={
        # Missing "name"
        "location": "Upstairs computer science",
        "condition": 5,
        "description": "Someone needs to check the battery on their UPS" + \
                       "or I am going to go insane."
    }, follow_redirects=True)

    # We should see a warning page
    # Flask aborts with BAD REQUEST automatically
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_submit_invalid_choice(app):
    """Form validates fields."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Post a form with an invalid condition
    rv = app.post("/add/", data={
        "name": "Beep-inator",
        "location": "Upstairs computer science",
        "condition": "blep",  # Invalid option
        "description": "Someone needs to check the battery on their UPS" + \
                       "or I am going to go insane."
    }, follow_redirects=True)

    # We should see a warning page
    # We should be redirected back to the home page
    assert rv.status_code == HTTPStatus.BAD_REQUEST

    # Post a form with another invalid condition
    rv = app.post("/add/", data={
        "name": "Beep-inator",
        "location": "Upstairs computer science",
        "condition": 6,  # Invalid option
        "description": "Someone needs to check the battery on their UPS" + \
                       "or I am going to go insane."
    }, follow_redirects=True)

    # We should see a warning page
    # We should be redirected back to the home page
    assert rv.status_code == HTTPStatus.BAD_REQUEST
