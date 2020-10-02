Testing
=======
This documents describes how to run test. In general we use unittests and integration tests.

Microservice Tests
__________________

Prerequisites
-------------

Make sure ``virtualenv`` is installed.

Execute Tests
--------------

We use `nox`_ to automate testing. Basically `nox`_ helps to automate tests in isolated environments and with multiple
python versions. To use it install it via pip (optionally, but recommended: in a virtual environment)::

    virtualenv nox-env -p python3.6
    source nox-env/bin/activate
    pip install nox

This installation can now be reused to run all microservice tests, as nox creates a new isolated env with the specified
dependencies each time you run tests.

To run e.g. capabilities-service tests (assuming you created the ``nox-env``)::

    source /path/to/nox-env/bin/activate
    cd /path/to/openeo-openshift-driver/services/capabilities
    nox

That's it!

What do we test?
________________

Currently three types of tests are run:
* Unittests (defined in the ``tests`` folder of each microservice)
* Linting (using `flake8`_ with extensions)
* Static type checking (using `mypy`_)

Unittests
---------

* Dependencies:
    * ``pytest``: to execute the tests
    * ``pytest-cov``: to get tests coverage
    * ``coverage[toml]``: to configure coverage with the ``pyproject.toml`` file
    * microservices also need: ``nameko``: because all of them are ``nameko`` microservices

Linting
-------

* Dependencies:
    * ``flake8``: to find invalid Python code, check `PEP 8`_ style guidelines,
     check code complexity
    * ``flake8-annotations``: to find unannotated functions (typing)
    * ``flake8-bugbear``: to find more bugs and design problems
    * ``flake8-bandit``: to find security issues
    * ``flake8-import-order``: to check import order to be `PEP 8`_ compliant

Static Type Checking
--------------------

* Dependencies:
    * ``mypy``: to check static types

Integration tests
_________________

To be updated.
A first implementation is found in some micro-services. In the tests folder of the microservice copy the file
``sample-auth`` to ``auth`` (which is not tracked by git) and fill the credentials of an existing user in your users-db.
With the API running, run the following (e.g. in the files microservice)::

    python tests/rest_calls.py

.. _nox: https://nox.thea.codes/en/stable/
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _mypy: https://mypy.readthedocs.io/en/stable/
.. _PEP 8: https://www.python.org/dev/peps/pep-0008/