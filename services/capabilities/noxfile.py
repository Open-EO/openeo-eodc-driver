import nox
from nox.sessions import Session
# TODO think about dependency management

locations = "capabilities", "tests", "noxfile.py"
nox.options.sessions = "tests"


@nox.session(python=["3.6"])
def tests(session: Session) -> None:
    args = session.posargs or ["--cov"]
    # no requirements needed for the package itself
    session.install(
        "pytest",
        "pytest-cov",
        "coverage[toml]",
        "nameko",
    )
    session.run("pytest", *args)
