"""Sphinx Configuration
"""

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import requests
import sys

from autodict import version as autodict

sys.path.insert(0, os.path.abspath("../.."))

on_rtd = os.environ.get("READTHEDOCS", None) == "True"

# -- Project information -----------------------------------------------------

project = "AutoDict"
copyright = "2021, Bradley Davis"  # pylint: disable=redefined-builtin
author = "Bradley Davis"

# The full version, including alpha/beta/rc tags
release = autodict.version
release_date = "!not released!"

r = requests.get(
    f"https://api.github.com/repos/WattsUp/{project}"
    f"/releases/tags/{autodict.tag}",
    headers={"Accept": "application/vnd.github.v3+json"})
if r.status_code == 200:
  j = r.json()
  release_date = j["published_at"][:10]
rst_epilog = f"""
.. |release_date| replace:: {release_date}
"""

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = ["sphinx.ext.napoleon"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

add_module_names = False
autoclass_content = "both"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
if not on_rtd:  # only import and set the theme if we're building docs locally
  import sphinx_rtd_theme
  html_theme = "sphinx_rtd_theme"
  html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
