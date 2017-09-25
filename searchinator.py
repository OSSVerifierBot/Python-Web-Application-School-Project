"""A web application for tracking inators.

This module contains route definitions for a web application. It uses
the Flask microframework.

To run the application, install all package requirements listed in
``requirements.txt`` and run::

  FLASK_APP=searchinator.py flask run

To run the application in debug mode, simply set the ``FLASK_DEBUG``
environment variable to ``1`` ::

  FLASK_APP=searchinator.py FLASK_DEBUG=1 flask run

Note that it is not suitable to run this application (or any web
application) in debug mode if it is running in production. Customers
get scared when they see tracebacks.

"""
import uuid

from flask import abort, Flask, flash, redirect, request, session, url_for
from datetime import datetime

from utils import add_data_param, login_required, uses_template
from condition import Condition

app = Flask(__name__)
app.secret_key = 'very.secret'
app.config['DATA_PATH'] = 'inator_data.json'


def list_inators(data):
    """List all inators."""
    return {}


def add_inator(data):
    """Add a new inator."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        return redirect(url_for('list_inators'))


def view_inator(data, ident):
    """View details of an inator."""
    return {}


def delete_inator(data, ident):
    """Delete an existing inator."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        return redirect(url_for('list_inators'))


def login(data):
    """Login to the searchinator."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        return redirect(url_for('list_inators'))


def logout():
    """Logout of the searchinator."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        return redirect(url_for('login'))
