# Running tests

This documents describes how to run test. Currently only covering the microservices.

## Prerequisites

Make sure `virtualenv` is installed.

## Execute Tests

We use [nox](https://nox.thea.codes/en/stable/) to automate testing. Basically [nox](https://nox.thea.codes/en/stable/)
helps to automate tests in isolated environments and with multiple python versions.
To use it install it via pip (optionally, but recommended: in a virtual environment)
``` bash
virtualenv nox-env -p python3.6
source nox-env/bin/activate
pip install nox
```

This installation can now be reused to run all microservice tests, as nox creates a new isolated env with the specified
dependencies each time you run tests.

To run e.g. capabilities-service tests (assuming you created the `nox-env`):
```bash
source /path/to/nox-env/bin/activate
cd /path/to/openeo-openshift-driver/services/capabilities
nox
```
That's it!

## What do we test?

Currently three types of tests are run:
* Unittests (defined in the `tests` folder of each microservice)
* Linting (using [flake8](https://flake8.pycqa.org/en/latest/) with extensions)
* Static type checking (using [mypy](https://mypy.readthedocs.io/en/stable/))

### Unittests

* Dependencies:
    * `pytest`: to execute the tests
    * `pytest-cov`: to get tests coverage
    * `coverage[toml]`: to configure coverage with the `pyproject.toml` file
    * microservices also need: `nameko`: because all of them are `nameko` microservices

### Linting

* Dependencies:
    * `flake8`: to find invalid Python code, check [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines,
     check code complexity
    * `flake8-annotations`: to find unannotated functions (typing)
    * `flake8-bugbear`: to find more bugs and design problems
    * `flake8-bandit`: to find security issues
    * `flake8-import-order`: to check import order to be [PEP 8](https://www.python.org/dev/peps/pep-0008/) compliant

### Static Type Checking

* Dependencies:
    * `mypy`: to check static types

## Useful stuff for newbies

For those who are new to nox, flake8, mypy here is a short overview about the most important things:

### Nox

If you are fine with an example check the `noxfile.py` in the capabilities service. Below you find a list of required
steps to setup your own nox pipeline.

1) create a `noxfile.py` in your package
1) Create "Sessions" in the `noxfile.py`: A Session is defined as a normal Python function decorated with `@nox.session()`
(don't forget to import nox first)
    * (Good to know): If you want to run the same session with different Python versions use e.g.
    `@nox.session(python=[3.6, 3.8])`
1) Do something in your Session:
    1) Install dependencies: Each Session starts off with a plane new environment. So the first thing to do is to install
    all needed dependencies. E.g. to install via pip: `session.install("pytest")` or `session.install("-r",
    "requirements.txt")`
    1) Run Session: When we have a nice environment setup we can run e.g. some tests. For this call e.g.
    `session.run(pytest)`
        * (Good to know): If you want to pass additional parameters e.g. run `pytest` only for a specific file add
        `args = session.posargs` inside our session and change the run command to `session.run("pytest", *args)`
        Then you can execute `nox -- tests/file1.py`
1) In your bash navigate into your package folder and run `nox` - all Sessions defined in you `noxfile.py` will be executed.

Useful options for nox:
* `-r/--reuse-existing-virtualenvs`: By default nox creates a new virtualenv each time you run it. To speed up tests and
if you are sure you didn't change any requirements you can add `-r` to reuse already existing virtual environments.
* `-s/--session`: If you only want to run a specific session instead of all. e.g. `nox -s tests`

### Flake8

Flake8 is a linter aggregation. In general linters analyse code to check for programming errors, bugs, stylistic errors,
and suspicious constructs. To configure Flake8 which tools to use and for which errors to check either a `.flake8` or
`setup.cfg` file can be used.

All additional flake8 tools which are installed also need to be setup in this configuration.

### mypy

mypy can also be configured within the `setup.cfg` or `mypy.ini`. The most important setting is to disable type
annotation checks for imported packages. Add the following section to ignore `pytest` and `mypy-nox`:
```ini
[mypy-nox.*,pytest]
ignore_missing_imports = True
```
