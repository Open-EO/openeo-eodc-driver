Creating documentation
======================

Setup
-----
1. (optional, but recommended) Create virtual environment::

    virtualenv doc -p python3.6

2. Install `Sphinx`_ and other documentation tools::

    pip install sphinx recommonmark sphinx_rtd_theme

3. As all subpackages need to be imported to create the documentation you now need to also install the dependencies of
  all sub packages, e.g. all microservice.

Build documentation
-------------------
Navigate into the doc folder and build html the doc::

    cd doc
    make html

This will create a ``_build`` folder inside ``/path/to/openeo/doc`` containing all types of generated documentation.
If you created ``html`` documentation as in the command above you will see a ``html`` folder. Open the
``/path/to/openeo/doc/_build/html/index.html`` file in your preferred browser to see the current status of you
documentation.

Extend API Documentation
---------------------
`Sphinx`_ comes with some handy commands - one of them setting up the basic files to create API documentation of your
code. To e.g. add API documentation of on of the capabilities microservices do the following::

    cd doc
    sphinx-apidoc -o source/ ../services/capabilities/capabilities

This creates two files in ``/path/to/openeo/doc/source/``:

* ``capabilities.rst``
* ``capabilities.dependencies.rst``

Directly showing the basic internal structure of the capabilities package. The general package description and files
directly in the capabilities package are referenced in ``capabilities.rst``. Also ``capabilities.dependencies.rst`` is
referenced there. To include those files in the documentation open ``services.rst`` and add ``capabilities`` - the name
of the parent file without the ``.rst`` extension.

For the microservices only that actual service code is presented in the documentation - Not the tests, Dockerfile, etc.

Obviously the documentation for the capabilities service is already setup - so there is no need to do this. But the same
procedure is applicable for any other microservice - or package assuming some minor changes.

Additional Information
----------------------
As already mentioned this documentation is build with `Sphinx`_. The easiest way to get started is to check their
`Sphinx Quickstart`_  page. Additionally I recommend reading `Sphinx reStructuredText`_ to get to know the syntax of
writing documentation in reStructuredText format.

.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _Sphinx Quickstart: https://www.sphinx-doc.org/en/master/usage/quickstart.html
.. _Sphinx reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html
