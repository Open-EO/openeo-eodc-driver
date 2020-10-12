"""Defines nox sessions for automatic test runs."""

import nox
from nox.sessions import Session
# TODO think about dependency management

locations = "capabilities", "tests", "noxfile.py"  # where to run flake8
nox.options.sessions = "lint", "mypy", "tests"


@nox.session(python=["3.6"])
def tests(session: Session) -> None:
    """Nox session for running unittests."""
    args = session.posargs or ["--cov"]
    session.install("-r", "requirements.txt")
    session.install(
        "pytest",
        "pytest-cov",
        "coverage[toml]",
        "nameko",
    )
    session.run("pytest", *args)


@nox.session(python=["3.6"])
def lint(session: Session) -> None:
    """Nox session for running code linting."""
    args = session.posargs or locations
    session.install(
        "flake8",
        "flake8-annotations",
        "flake8-bugbear",
        "flake8-bandit",
        "flake8-import-order",  # think about import order style!
        "flake8-builtins",
        "flake8-eradicate",
        "flake8-print",
        "flake8-docstrings",
    )
    session.run("flake8", *args)


@nox.session(python=["3.6"])
def mypy(session: Session) -> None:
    """Nox session for running static type analysis."""
    args = session.posargs or locations
    session.install("mypy")
    session.run("mypy", *args)
