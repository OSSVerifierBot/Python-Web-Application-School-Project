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
    def wrapper(func):
        @functools.wraps(func)
        def wrapper2(*args, **kwargs):
            # Attmepting to load the file path
            try:
                with open(path, 'r') as f:
                    data = json.loads(f.read(), object_hook=as_inator)
            # If no file exists, set to an empty dictionary
            except FileNotFoundError:
                data = {}
            retVal = func(data, *args, **kwargs)
            # Write new data to file
            with open(path, 'w') as f:
                f.write(json.dumps(data, default=from_datetime))
            return retVal
        return wrapper2
    return wrapper


def uses_template(template):
    """Wrap a function to add HTML template rendering functionality."""
    # TODO implement this guy
    def wrapper(func):
        @functools.wraps(func)
        def wrapper2(*args, **kwargs):
            retVal = func(*args, **kwargs)
            if isinstance(retVal, dict):
                return render_template(template, **retVal)
            else:
                return retVal
        return wrapper2
    return wrapper


def login_required(func):
    """Wrap a function to enforce user authentication."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' in session:
            return func(*args, **kwargs)
        else:
            flash('You must be logged in to access that page.', 'danger')
            return redirect('/login/')
    return wrapper
