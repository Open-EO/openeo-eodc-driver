# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../services/capabilities'))
sys.path.insert(0, os.path.abspath('../services/data'))
sys.path.insert(0, os.path.abspath('../services/files'))
sys.path.insert(0, os.path.abspath('../services/jobs'))
sys.path.insert(0, os.path.abspath('../services/processes'))
sys.setrecursionlimit(1500)


# -- Project information -----------------------------------------------------

project = 'OpenEO-EODC-Driver'
copyright = '2020, Luca Foresta, Sophie Herrmann'
author = 'Luca Foresta, Sophie Herrmann'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '1.0'
# The full version, including alpha/beta/rc tags.
release = '1.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'recommonmark',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.coverage',
    'sphinx.ext.intersphinx',
]

# Map suffix
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

napoleon_google_docstring = True
napoleon_use_param = True
napoleon_use_ivar = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- External mapping ------------------------------------------------------------
python_version = '.'.join(map(str, sys.version_info[0:2]))
intersphinx_mapping = {
    'sphinx': ('http://www.sphinx-doc.org/en/stable', None),
    'python': ('https://docs.python.org/' + python_version, None),
    'nameko': ('https://nameko.readthedocs.io/en/stable/', None),
    'dynaconf': ('https://dynaconf.readthedocs.io/en/docs_223/', None),
}
