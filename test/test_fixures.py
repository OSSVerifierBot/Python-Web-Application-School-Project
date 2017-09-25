"""Tests for testing fixtures."""
import datetime
import re

import condition


def test_inator_data_length(inator_data):
    """Check the number of inators."""
    assert len(inator_data) == 5


def test_inator_fields(inator_data):
    """Check the fields in the inators."""
    for dct in inator_data.values():
        assert set(dct.keys()) == {"ident", "name", "location",
                                   "description", "condition", "added"}


def test_inator_ident(inator_data):
    """Check the ident field of generated inators."""
    uuid_re = re.compile(
        "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    )

    # Make sure the keys of inator_data and the "ident" field of the
    # value are valid UUIDs
    for ident, dct in inator_data.items():
        assert uuid_re.fullmatch(ident) is not None
        assert uuid_re.fullmatch(dct["ident"]) is not None
        assert ident == dct["ident"]


def test_inator_condition(inator_data):
    """Check the condition field of generated inators."""
    for dct in inator_data.values():
        assert isinstance(dct["condition"], condition.Condition)


def test_inator_added(inator_data):
    """Check the added field of generated inators."""
    for dct in inator_data.values():
        assert isinstance(dct["added"], datetime.datetime)


def test_inator_str_fields(inator_data):
    """Check that str fields are non-empty."""
    for dct in inator_data.values():
        for field in ("name", "location", "description"):
            assert isinstance(dct[field], str)  # Better be a str
            assert dct[field] != ""             # Better not be empty


def test_data_path(app, data_path):
    """Check that the data_path agrees with the flask app."""
    assert data_path == app.application.config["DATA_PATH"]
