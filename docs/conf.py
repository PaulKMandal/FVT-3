import os, sys
from datetime import datetime
from pathlib import Path

# Make package importable for autodoc:
sys.path.insert(0, os.path.abspath('..'))
# (also make docs/ importable, in case you later add helper modules)
sys.path.insert(0, os.path.abspath('.'))

# Inherit documentation from parents by default
autodoc_default_options = {
    "members": True,
    "inherited-members": True,
    "exclude-members": "__init__",
    "show-inheritance": True,
}
autodoc_inherit_docstrings = True
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

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# MyST extensions for GitHub-like Markdown
myst_enable_extensions = [
    "colon_fence",   # ::: fenced blocks
    "deflist",       # definition lists
    "linkify",       # auto-link bare URLs
    "substitution",  # simple substitutions
    "tasklist",      # - [x] checkboxes
]

html_theme_options = {
    "navigation_depth": -1,      # unlimited depth in the left sidebar
    "collapse_navigation": False, # keep all sections expanded
    "sticky_navigation": True,    # keep sidebar in view as you scroll
    "titles_only": False,         # show section titles + nested items
}


autosummary_generate = True
napoleon_google_docstring = True
html_theme = "sphinx_rtd_theme"

# Optional: avoid importing heavy deps during autodoc
autodoc_mock_imports = []

# ---------------- external API doc injection (supports docs/api_docs/**) -----
API_DOCS_DIR = Path(__file__).parent / "api_docs"

def _camelcase_index(parts):
    """Return index of first CamelCase-like token (class name), else None."""
    for i, p in enumerate(parts):
        if p and p[0].isupper():
            return i
    return None

def _candidates_for(what: str, name: str):
    """
    Generate candidate external doc paths for an object.
    name examples:
      - orchestrator.main                      (module)
      - orchestrator.main.OrchestratorServicer (class)
      - orchestrator.main.OrchestratorServicer.Register (method)
      - orchestrator.main.serve                (function)

    Search order:
      1) <mod_path>/<Class>/<member>.(md|rst)       # method/attribute
      2) <mod_path>/<Class>.(md|rst)                # class-level
      3) <mod_path>/<member>.(md|rst)               # module-level function/attr
      4) <mod_path>.(md|rst)                        # module overview
      5) <full/dotted/name>.(md|rst)                # exact dotted path as dirs (fallback)
    """
    parts = name.split(".")
    cls_idx = _camelcase_index(parts)  # first likely class token
    mod_parts = parts[:cls_idx] if cls_idx is not None else parts[:-1]
    last = parts[-1] if parts else None

    candidates = []

    # 1) method/attribute under class
    if cls_idx is not None and what in {"method", "function", "attribute"} and len(parts) > cls_idx + 1:
        cls = parts[cls_idx]
        member = parts[-1]
        candidates.append(API_DOCS_DIR.joinpath(*mod_parts, cls, member))

    # 2) class-level
    if what == "class" and cls_idx is not None:
        cls = parts[cls_idx]
        candidates.append(API_DOCS_DIR.joinpath(*mod_parts, cls))

    # 3) module-level function/attribute
    if cls_idx is None and what in {"function", "attribute"} and last:
        candidates.append(API_DOCS_DIR.joinpath(*mod_parts, last))

    # 4) module overview
    if what == "module" and mod_parts:
        candidates.append(API_DOCS_DIR.joinpath(*mod_parts))

    # 5) exact dotted path as directories (universal fallback)
    candidates.append(API_DOCS_DIR.joinpath(*parts))

    # try both .md and .rst
    out = []
    for c in candidates:
        out.extend([c.with_suffix(".md"), c.with_suffix(".rst")])
    return out

def inject_external_docs(app, what, name, obj, options, lines):
    """Append external docs from docs/api_docs/** if a matching file exists."""
    for p in _candidates_for(what, name):
        if p.exists():
            text = p.read_text()
            # Append after any tiny inline docstring; replace if none present
            lines[:] = (lines + ["", text]) if lines else text.splitlines()
            break

def setup(app):
    # Optional: hide generated proto modules from listings (doesn't affect inheritance)
    def _skip_protobuf(app, what, name, obj, skip, options):
        return skip or name.endswith("_pb2") or name.endswith("_pb2_grpc") or ".proto." in name
    app.connect("autodoc-skip-member", _skip_protobuf)

    app.connect("autodoc-process-docstring", inject_external_docs)
# ---------------------------------------------------------------------------
