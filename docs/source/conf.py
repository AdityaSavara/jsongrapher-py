import os
import sys

# Add the parent directory to sys.path so Sphinx can find the source code
sys.path.insert(0, os.path.abspath('../../'))

# Project information
project = 'JsonGrapher'
copyright = '2025, JsonGrapher'
author = 'JsonGrapher'
release = '0.1'

# Extensions to enable
extensions = [
    'sphinx.ext.napoleon'
]

# HTML theme to use
html_theme = 'sphinx_rtd_theme'
