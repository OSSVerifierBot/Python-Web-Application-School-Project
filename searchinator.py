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

from utils import add_data_param, uses_template, login_required

# login_required, uses_template
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
    try:
        # Sorting inators by name
        lst = sorted(data['inators'].values(), key=lambda x: x['name'])
        # Sorting inators by condition
        lst = sorted(lst, key=lambda x: x['condition'], reverse=True)
        return {'inators': lst}

    except KeyError:
        return {}


@app.route('/add/', methods=['GET', 'POST'])
@login_required
@add_data_param(app.config['DATA_PATH'])
@uses_template('add-inator.html')
def add_inator(data):
    """Add a new inator."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        try:
            # Getting random UUID data
            ident = str(uuid.uuid4())
            # Creating new dictionary to append to data
            newInator = {
                'name': request.form['name'],
                'location': request.form['location'],
                'description': request.form['description'],
                'added': datetime.now(),
                'ident': ident,
                'condition': Condition(int(request.form['condition']))
                }

        except ValueError:
            # Bad gatway
            abort(400)

        try:
            # Make sure the identifier exists and add it to the data
            data['inators'][ident] = newInator
            flash('Successfully added {}.'
                  .format(newInator['name'], 'success'))
            return redirect(url_for('list_inators'))
        except KeyError:
            return redirect(url_for('list_inators'))


@app.route('/view/<ident>/', methods=['GET'])
@login_required
@add_data_param(app.config['DATA_PATH'])
@uses_template('view-inator.html')
def view_inator(data, ident):
    """View details of an inator."""
    try:
        # Return the dictionary requested
        dictInators = data['inators'][ident]
        return {'inator': dictInators}

    except KeyError:
        # Error for dictionary not present
        flash('No such inator with identifier {}.'.format(ident), 'danger')
        return redirect(url_for('list_inators'))


@app.route('/delete/<ident>/', methods=['GET', 'POST'])
@login_required
@add_data_param(app.config['DATA_PATH'])
@uses_template('delete-inator.html')
def delete_inator(data, ident):
    """Delete an existing inator."""
    try:
        # Get the dictionary user wants to delete
        dictInators = data['inators'][ident]
    except KeyError:
        flash('No such inator with identifier {}.'
              .format(ident), 'danger')
        return redirect(url_for('list_inators'))

    if request.method == 'GET':
        return {'inator': dictInators}

    if request.method == 'POST':
        # Delete the inator from the data
        data['inators'].pop(ident)
        flash('Successfully deleted {} ({}).'
              .format(dictInators['name'], ident, 'success'))
        return redirect(url_for('list_inators'))


@app.route('/login/', methods=['GET', 'POST'])
@add_data_param(app.config['DATA_PATH'])
@uses_template('login.html')
def login(data):
    """Login to the searchinator."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        # Make sure user isnt already logged in
        if 'username' in session:
            flash('You are already logged in.' +
                  'Log out to log in again.', 'danger')
            return redirect(url_for('login'))

        # look for the username
        username = request.form['username']
        try:
            user = data['users'][username]
        except KeyError:
            flash('Cannot find user {}. Try again.'.format(username), 'danger')
            return redirect(url_for('login'))

        # Look for the password
        try:
            correct_password = user['password']
        except KeyError:
            flash('Cannot find password for user {}!'
                  .format(username), 'danger')
            return redirect(url_for('login'))

        # Verify the password with the username
        password = request.form['password']
        if password == correct_password:
            session['username'] = username
            flash('Successfully logged in as {}.'.format(username), 'success')
            return redirect(url_for('list_inators'))
        else:
            flash('Incorrect password for user {}.'.format(username), 'danger')
            return redirect(url_for('login'))


@app.route('/logout/', methods=['GET', 'POST'])
@login_required
@uses_template('logout.html')
def logout():
    """Logout of the searchinator."""
    if request.method == 'GET':
        return {}

    # Remove the username from the session, logging user out
    if request.method == 'POST':
        session.pop('username')
        flash('Successfully logged out.', 'danger')
        return redirect(url_for('login'))
