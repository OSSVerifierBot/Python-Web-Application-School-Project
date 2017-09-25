"""Local plugins for pytest.

This module contains fixtures that can be used in pytest unit
tests. Note that you don't have to import anything from this module to
use the fixtures. Pytest performs dependency injection based on each
test's argument list.

For more details, have a look at the `Pytest documentation
<https://docs.pytest.org/en/latest/fixture.html>`_.

"""
import pytest
import tempfile
import os

import generate
import searchinator


@pytest.fixture
def cleandir():
    """Create a temporary directory in which the test will be run.

    This fixture creates a temporary directory and changes our working
    directory to that temporary directory. After the test is complete,
    the temporary directory and all files in that directory are
    deleted.

    This fixture allows us to create files as we please without worry
    of interfering with future tests.

    """
    pwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        yield
        os.chdir(pwd)


@pytest.fixture
def app():
    """Instantiate a searchinator test client.

    The test client object is used to issue HTTP requests to our web
    application. We can send GET and POST (or any other type of
    request) to our application just like a browser would. Then, we
    can inspect the HTTP responses we receive and perform assertions
    on them.

    """
    searchinator.app.testing = True
    return searchinator.app.test_client()


@pytest.fixture
def inator_data():
    """Generate five random inators."""
    return generate.random_inators(5)


@pytest.fixture
def data_path():
    """Retrieve the path the app uses to store JSON data files."""
    return searchinator.app.config['DATA_PATH']
