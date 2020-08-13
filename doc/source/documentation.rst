Creating documentation
======================

Setup
-----
1. (optional, but recommended) Create virtual environment::

    virtualenv doc -p python3.6

1. Install `Sphinx`_ and other documentation tools::

    pip install sphinx recommonmark sphinx_rtd_theme

1. As all subpackages need to be imported to create the documentation you now need to also install the dependencies of
    all sub packages, e.g. all microservice.

Build documentation
-------------------
1. Navigate into the doc folder and build html the doc::

    cd doc
    make html

.. _Sphinx:https://www.sphinx-doc.org/en/master/
