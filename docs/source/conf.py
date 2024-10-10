# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'zeafrost'
version = 'latest'
copyright = '2023, Pipeline.Yggdrazil Group'
author = 'Paniti Kliengsa-ard'
release = 'latest'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinxcontrib.httpdomain',
    'sphinx.ext.autodoc',
    'sphinx.ext.duration',
    'sphinx.ext.napoleon'
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = "_static/waves_64x64.png"


# ////// STEPS ////// #
# 1. sphinx-quickstart docs
# 2. edit docs/source/conf.py
#       import os
#       import sys
#       sys.path.insert(0, os.path.abspath('../..'))
#
#       extensions = [
#           'sphinxcontrib.httpdomain',
#           'sphinx.ext.autodoc',
#           'sphinx.ext.duration',
#           'sphinx.ext.napoleon'
#       ]
#
#       html_theme = 'sphinx_rtd_theme'
#       html_logo = "_static/waves_64x64.png"
# 3. sphinx-build -M html .\docs\source\ .\docs\build\