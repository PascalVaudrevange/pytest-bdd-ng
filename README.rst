BDD library for the pytest runner
=================================

.. image:: http://img.shields.io/pypi/v/pytest-bdd-ng.svg
    :target: https://pypi.python.org/pypi/pytest-bdd-ng
.. image:: https://codecov.io/gh/elchupanebrej/pytest-bdd-ng/branch/default/graph/badge.svg
    :target: https://app.codecov.io/gh/elchupanebrej/pytest-bdd-ng
.. image:: https://readthedocs.org/projects/pytest-bdd-ng/badge/?version=default
    :target: https://pytest-bdd-ng.readthedocs.io/en/default/?badge=default
    :alt: Documentation Status
.. image:: https://badgen.net/badge/stand%20with/UKRAINE/?color=0057B8&labelColor=FFD700
    :target: https://savelife.in.ua/en/

.. _behave: https://pypi.python.org/pypi/behave
.. _pytest: https://docs.pytest.org
.. _Gherkin: https://cucumber.io/docs/gherkin/reference
.. _pytest-bdd-ng: https://pytest-bdd-ng.readthedocs.io/en/default/

**pytest-bdd-ng** combine descriptive clarity of Gherkin_ language
with power and fullness of pytest_ infrastructure.
It enables unifying unit and functional
tests, reduces the burden of continuous integration server configuration and allows the reuse of
test setups.

Pytest fixtures written for unit tests can be reused for setup and actions
mentioned in feature steps with dependency injection. This allows a true BDD
just-enough specification of the requirements without obligatory maintaining any context object
containing the side effects of Gherkin imperative declarations.

.. NOTE:: Project documentation: pytest-bdd-ng_

Install pytest-bdd-ng
---------------------

::

    pip install pytest-bdd-ng

Project layout
--------------
**pytest-bdd-ng** automatically collect `*.feature` files from pytest_ tests directory.
Important to remember, that feature files are used by other team members as live documentation,
so it's not a very good idea to mix documentation and test code.

The more features and scenarios you have, the more important becomes the question about
their organization. So recommended way is to organize your feature files in the folders by
semantic groups:

::

    features
    ├──frontend
    │  └──auth
    │     └──login.feature
    └──backend
       └──auth
          └──login.feature

And tests for this features could be organized in the next manner:

::

    tests
    └──conftest.py
    └──functional
    │     └──__init__.py
    │     └──conftest.py
    │     │     └── "User step library used by descendant tests"
    │     │
    │     │         from steps.auth.given import *
    │     │         from steps.auth.when import *
    │     │         from steps.auth.then import *
    │     │
    │     │         from steps.order.given import *
    │     │         from steps.order.when import *
    │     │         from steps.order.then import *
    │     │
    │     │         from steps.browser.given import *
    │     │         from steps.browser.when import *
    │     │         from steps.browser.then import *
    │     │
    │     └──frontend_auth.feature -> ../../features/frontend/auth.feature
    │     └──backend_auth.feature -> ../../features/backend/auth.feature
    ...

Step definitions could be organized in the next way

::

    steps
    └──auth
    │     └── given.py
    │     │      └── """User auth step definitions"""
    │     │          from pytest import fixture
    │     │          from pytest_bdd import given, when, then, step
    │     │
    │     │          @fixture
    │     │          def credentials():
    │     │             return 'test_login', 'test_very_secure_pass'
    │     │
    │     │          @given('User login into application')
    │     │          def user_login(credentials):
    │     │             ...
    │     └── when.py
    │     └── then.py
    └──order
    │     └── given.py
    │     └── when.py
    │     └── then.py
    └──browser
    │     └── ...
    ...

To make links between feature files at features directory and test directory there are few options
(for more information please investigate project tests):

#. Symlinks
#. `.desktop` files
#. `.webloc` files
#. `.url` files

.. NOTE:: Link files also could be used to load features by http://

License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_.

© 2013-2023 Oleg Pidsadnyi, Anatoly Bubenkov, Konstantin Goloveshko and others
