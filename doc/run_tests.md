# Running tests

This documents describes how to run test. Currently only covering the microservices.

## Prerequisites

Make sure `virtualenv` is installed.

## Execute Tests

We use [nox](https://nox.thea.codes/en/stable/) to automate testing. Basically [nox](https://nox.thea.codes/en/stable/)
helps to automate test in isolated environments and with multiple python versions.
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

## Useful stuff for newbies

For those who are new to nox, flake8, mypy here a short overview about things I think are good to know:

### Nox

If you are fine with an example check the `noxfile.py` in the capabilities service.

1) create a `noxfile.py` in your package
1) Create "Sessions" in the `noxfile.py`: A Session is defined as normal Python function decorated with `@nox.session()`
(don't forget to import nox first)
    * (Good to know): If you want to run the same session with different Python versions use e.g.
    `@nox.session(python=[3.6, 3.8])`
1) Do something in your Session:
    1) Install dependencies: Each Session starts of with a plane new environment. So the first thing to do is install
    all needed dependencies. E.g. to install via pip: `session.install("pytest")` or `session.install("-r",
    "requirements.txt")`
    1) Run Session: When we have a nice environment setup we can run e.g. some tests. For this call e.g.
    `session.run(pytest)`
        * (Good to know): If you want to pass additional parameters e.g. run `pytest` only for a specific file add
        `args = session.posargs` inside our session and change to run command to `session.run("pytest", *args)`
1) In your bash navigate into your package and run `nox` - all Sessions defined in you `noxfile.py` will be executed.

Useful options for nox:
* `-r/--reuse-existing-virtualenvs`: By default nox creates a new virtualenv each time you run it. To speed up tests and
if you are sure you didn't change any requirements you can add `-r` to reuse already existing virtual environments.

