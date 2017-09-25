"""Tests for utility functions."""
import datetime
import json
import pytest

from condition import Condition

import utils


def test_json_loading():
    """Load a JSON string as an -inator dict."""
    d = {
        "ident": "c9aa6c58-c8bb-4a19-a5ae-3ad107757d40",
        "name": "juice-inator",
        "location": "airport",
        "description": "Ut neque ante, scelerisque sit amet orci.",
        "condition": Condition.USUALLY_WORKS,
        "added": datetime.datetime(2017, 9, 18, 2, 4, 57)
    }

    # Use a multi-line string for convenience
    s = """{
        "added": "2017-09-18T02:04:57",
        "condition": 4,
        "description": "Ut neque ante, scelerisque sit amet orci.",
        "ident": "c9aa6c58-c8bb-4a19-a5ae-3ad107757d40",
        "location": "airport",
        "name": "juice-inator"
    }"""

    # Loading s should give us an inator record exactly like d
    assert d == json.loads(s, object_hook=utils.as_inator)


def test_json_loading_invalid_condition():
    """Load an invalid JSON string as an -inator dict."""
    # 6 is an invalid condition
    s = """{
        "added": "2017-09-18T02:04:57",
        "condition": 6,
        "description": "Ut neque ante, scelerisque sit amet orci.",
        "ident": "c9aa6c58-c8bb-4a19-a5ae-3ad107757d40",
        "location": "airport",
        "name": "juice-inator"
    }"""

    d = json.loads(s, object_hook=utils.as_inator)

    # s should not load properly because it has an invalid condition
    assert not isinstance(d["condition"], Condition)
    assert not isinstance(d["added"], datetime.datetime)


def test_json_loading_invalid_date():
    """Load an invalid JSON string as an -inator dict."""
    # datetime format is invalid
    s = """{
        "added": "2017-09-18TTTTTTTTTT02:04:57",
        "condition": 4,
        "description": "Ut neque ante, scelerisque sit amet orci.",
        "ident": "c9aa6c58-c8bb-4a19-a5ae-3ad107757d40",
        "location": "airport",
        "name": "juice-inator"
    }"""

    d = json.loads(s, object_hook=utils.as_inator)

    # s should not load properly because it has an invalid datetime
    assert not isinstance(d["condition"], Condition)
    assert not isinstance(d["added"], datetime.datetime)


def test_json_dumping():
    """Dump an object with a datetime to a JSON string."""
    d = {
        "added": datetime.datetime(2017, 9, 18, 2, 4, 57)
    }

    s = '{"added": "2017-09-18T02:04:57"}'

    # The datetime object should be converted to a string
    assert s == json.dumps(d, default=utils.from_datetime)


def test_json_dump_other_object():
    """Dump an object with a datetime to a JSON string."""
    d = {
        "added": datetime.date(2017, 9, 18)
    }

    # We don't know how to serialize a **datetime.date**, so we expect
    # a TypeError
    with pytest.raises(TypeError):
        json.dumps(d, default=utils.from_datetime)


def test_add_data_param():
    """Save data to a file using a decorated function."""
    @utils.add_data_param("data.json")
    def myfunc(data):
        data["frog"] = "giraffe"
        data["things"] = ["frog", "dog", "apple"]

    # Remember that the "data" param is added to myfunc by the decorator!
    # The decorated function takes zero parameters when we call it.
    myfunc()

    # Open up the data file and load its contents
    with open("data.json") as f:
        content = json.load(f)

    assert content == {"frog": "giraffe", "things": ["frog", "dog", "apple"]}


def test_add_data_param_default_behavior():
    """Check behavior when file doesn't exist."""
    @utils.add_data_param("data.json")
    def myfunc(data):
        # We're not going to do anything.
        return "froggy"

    # Remember that the "data" param is added to myfunc by the decorator!
    # It takes zero parameters when we call it.
    # Make sure we held on to the return value
    assert "froggy" == myfunc()

    with open("data.json") as f:
        content = json.load(f)

    # We expect data to be an empty dict by default
    assert content == {}


def test_add_data_param_file_exists():
    """Check behavior when file doesn't exist."""
    with open("data.json", "w") as f:
        json.dump({"froggy": 12}, f)

    @utils.add_data_param("data.json")
    def myfunc(data):
        data["pigeon"] = 10

    # Remember that the "data" param is added to myfunc by the decorator!
    # It takes zero parameters when we call it.
    assert myfunc() is None

    with open("data.json") as f:
        content = json.load(f)

    # We should still see froggy, as well as the newly-added pigeon
    assert content == {"froggy": 12, "pigeon": 10}
