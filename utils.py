"""Utility functions for searchinator."""
import datetime
import functools
import json

from flask import flash, redirect, render_template, request, session, url_for

from condition import Condition

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
"""Expected string format for :class:`datetime.datetime`."""


def load_time(x):
    """Load a :class:`datetime.datetime` from :class:`str`."""
    return datetime.datetime.strptime(x, TIME_FORMAT)


def dump_time(x):
    """Dump a :class:`datetime.datetime` to :class:`str`."""
    return x.strftime(TIME_FORMAT)


def as_inator(dct):
    """Attempt to construct values of an inator with appropriate types."""
    keyset = {'ident', 'name', 'location', 'description', 'condition', 'added'}
    if set(dct.keys()) == keyset:
        try:
            new_dct = dct.copy()
            new_dct['added'] = load_time(new_dct['added'])
            new_dct['condition'] = Condition(int(new_dct['condition']))
            return new_dct
        except ValueError:
            return dct
    else:
        return dct


def from_datetime(obj):
    """Convert :class:`datetime.datetime` objects to string."""
    if isinstance(obj, datetime.datetime):
        return dump_time(obj)
    raise TypeError("{} is not JSON serializable".format(repr(obj)))


def add_data_param(path):
    """Wrap a function to facilitate data storage."""
    # TODO implement this guy
    pass


def uses_template(template):
    """Wrap a function to add HTML template rendering functionality."""
    # TODO implement this guy
    pass


def login_required(func):
    """Wrap a function to enforce user authentication."""
    # TODO implement this guy
    pass
