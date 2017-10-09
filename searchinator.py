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
import functools
import operator

from flask import abort, Flask, flash, redirect, request, session, url_for
from datetime import datetime

from utils import add_data_param, uses_template, login_required

#, login_required, uses_template
from condition import Condition

app = Flask(__name__)
app.secret_key = 'very.secret'
app.config['DATA_PATH'] = 'inator_data.json'

@app.route('/')
@login_required
@add_data_param(app.config['DATA_PATH'])
@uses_template('list-inators.html')
def list_inators(data):
    """List all inators."""
    # Sorting inators by name
    lst = sorted(data['inators'].values(), key = lambda x: x['name'])
    # Sorting inators by condition
    lst = sorted(lst, key = lambda x: x['condition'], reverse=True)
    inators = {'inators':lst}

    return inators


@app.route('/add/')
@add_data_param(app.config['DATA_PATH'])
def add_inator(data):
    """Add a new inator."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        return redirect(url_for('list_inators'))


@app.route('/view/<ident>/')
@add_data_param(app.config['DATA_PATH'])
def view_inator(data, ident):
    """View details of an inator."""
    return {}


@app.route('/delete/<ident>/')
@add_data_param(app.config['DATA_PATH'])
def delete_inator(data, ident):
    """Delete an existing inator."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        return redirect(url_for('list_inators'))

@app.route('/login/', methods=['GET', 'POST'])
@add_data_param(app.config['DATA_PATH'])
@uses_template('login.html')
def login(data):
    """Login to the searchinator."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        if 'username' in session:
            flash('You are already logged in. Log out to log in again.', 'danger')
            return redirect(url_for('list_inators'))
        username = request.form['username']
        try:
            user = data['users'][username]
        except KeyError:
            flash('Cannot find user {}. Try again.'.format(username), 'danger')
            return redirect(url_for('login'))

        try:
            correct_password = user['password']
        except KeyError:
            flash('Cannot find password for user{}!'.format(username), 'danger')
            return redirect(url_for('login'))

        password = request.form['password']
        if password == correct_password:
            session['username'] = username
            flash('Successfully logged in as {}.'.format(username), 'success')
            return redirect(url_for('list_inators'))
        else:
            flash('Incorrect password for user{}.'.format(username), 'danger')
            return redirect(url_for('login'))

@app.route('/logout/')
@login_required
@uses_template('logout.html')
def logout():
    """Logout of the searchinator."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        return redirect(url_for('login'))
