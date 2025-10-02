import os, sys
from datetime import datetime
# Make package importable for autodoc:
sys.path.insert(0, os.path.abspath('..'))

autodoc_default_options = {
    "members": True,
    "inherited-members": True,
    "exclude-members": "__init__",
    "show-inheritance": True,
}

autoclass_content = "both" 
autodoc_inherit_docstrings = True   # default is True; make it explicit
autoclass_content = "both"   

project = "Your Project"
author = "Your Name"
copyright = f"{datetime.now():%Y}, {author}"
extensions = [
    "myst_parser",                 # render README.md if you include it
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]
autosummary_generate = True
napoleon_google_docstring = True
html_theme = "sphinx_rtd_theme"
# Optional: avoid importing heavy deps during autodoc
autodoc_mock_imports = []