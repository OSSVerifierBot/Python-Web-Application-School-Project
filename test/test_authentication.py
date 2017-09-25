"""Tests for login and logout routes."""
import json

from http import HTTPStatus
from urllib.parse import urlparse


def test_login_required_for_logout(app):
    """Redirect to login if we're not logged in."""
    # Check redirection
    rv = app.get("/logout/")
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/login/"

    # Check for flashed message
    rv = app.get("/logout/", follow_redirects=True)
    assert b"You must be logged in to access that page." in rv.data


def test_successful_logout_page_laods(app):
    """Check that we can log out."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Make sure the  page loads
    rv = app.get("/logout/")
    assert rv.status_code == HTTPStatus.OK
    assert b"Are you sure you want to log out?" in rv.data


def test_successful_logout_redirects(app):
    """Check that we're redirected properly after logout."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Check redirection
    rv = app.post("/logout/")
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/login/"

    # Check that we're actually logged out
    with app.session_transaction() as sess:
        assert "username" not in sess


def test_successful_logout(app):
    """Check that we get the right flash message after logout."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Log out and follow redirects
    rv = app.post("/logout/", follow_redirects=True)
    assert rv.status_code == HTTPStatus.OK

    # Check for the flashed message
    assert b"Successfully logged out." in rv.data

    # Check that we're actually logged out
    with app.session_transaction() as sess:
        assert "username" not in sess


def test_already_logged_in(app):
    """Redirect if we're already logged in."""
    # Log in
    with app.session_transaction() as sess:
        sess["username"] = "heinz"

    # Check that we're redirected home
    rv = app.get("/login/")
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/"

    # Follow redirects to check that we see the flashed message
    rv = app.get("/logout/", follow_redirects=True)
    assert b"You are already logged in. Log out to log in again." in rv.data


def test_successful_login_load(app):
    """Login page loads when not logged in."""
    # Check that we can get to the login page
    rv = app.get("/login/")
    assert rv.status_code == HTTPStatus.OK
    assert b"Login" in rv.data


def test_successful_login_redirect(app, data_path):
    """Login with valid credentials leads to correct redirect."""
    # Save some credentials to the data file
    with open(data_path, "w") as data_file:
        data = {
            "users": {
                "heinz": {
                    "username": "heinz",
                    "password": "doof"
                }
            }
        }
        json.dump(data, data_file)

    # Try logging in using the data
    rv = app.post("/login/", data={
        "username": "heinz",
        "password": "doof"
    })

    # We should be redirected home if it worked.
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/"


def test_successful_login(app, data_path):
    """Login with valid credentials."""
    # Save some credentials to the data file
    with open(data_path, "w") as data_file:
        data = {
            "users": {
                "norm": {
                    "username": "norm",
                    "password": "gug4evah"
                }
            }
        }
        json.dump(data, data_file)

    # Try logging in using the data, following redirects
    rv = app.post("/login/", data={
        "username": "norm",
        "password": "gug4evah"
    }, follow_redirects=True)

    # Make sure we made it home OK
    assert rv.status_code == HTTPStatus.OK
    assert b"List of Inators" in rv.data

    # Check that we see the flashed message
    assert b"Successfully logged in as norm." in rv.data

    # Make sure we're *actually* logged in
    with app.session_transaction() as sess:
        assert sess["username"] == "norm"


def test_invalid_username(app, data_path):
    """Login with invalid username."""
    # Log in with a non existent username
    rv = app.post("/login/", data={
        "username": "heinzzzzzzzzzz",
        "password": "doof"
    }, follow_redirects=True)

    assert rv.status_code == HTTPStatus.OK
    assert b"Login" in rv.data

    # Check flashed message
    assert b"Cannot find user heinzzzzzzzzzz. Try again." in rv.data


def test_missing_password(app, data_path):
    """Login with missing password."""
    # Save an invalid credential record
    with open(data_path, "w") as data_file:
        data = {
            "users": {
                "heinz": {
                    "username": "heinz",
                    # Leave out the password field
                }
            }
        }
        json.dump(data, data_file)

    # Try logging in
    rv = app.post("/login/", data={
        "username": "heinz",
        "password": "doooooooooof"
    }, follow_redirects=True)

    assert rv.status_code == HTTPStatus.OK
    assert b"Login" in rv.data

    # Check the flashed message
    assert b"Cannot find password for user heinz!" in rv.data


def test_wrong_password_redirect(app, data_path):
    """Login with incorrect password check redirect."""
    # Save some credentials to the data file
    with open(data_path, "w") as data_file:
        data = {
            "users": {
                "heinz": {
                    "username": "heinz",
                    "password": "doof"
                }
            }
        }
        json.dump(data, data_file)

    # Log in with incorrect credentials
    rv = app.post("/login/", data={
        "username": "heinz",
        "password": "doooooooooof"
    })

    # Check that we're redirected back to the login page
    assert rv.status_code == HTTPStatus.FOUND
    assert urlparse(rv.location).path == "/login/"


def test_wrong_password(app, data_path):
    """Login with incorrect password."""
    # Save some credentials to the data file
    with open(data_path, "w") as data_file:
        data = {
            "users": {
                "heinz": {
                    "username": "heinz",
                    "password": "doof"
                }
            }
        }
        json.dump(data, data_file)

    # Log in with incorrect credentials
    rv = app.post("/login/", data={
        "username": "heinz",
        "password": "doooooooooof"
    }, follow_redirects=True)

    assert rv.status_code == HTTPStatus.OK
    assert b"Login" in rv.data

    # Check that we see the flashed message
    assert b"Incorrect password for user heinz." in rv.data
