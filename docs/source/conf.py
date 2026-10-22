import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

project = "awesomefigures"
author = "Heriberto Espino Montelongo"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "matplotlib.sphinxext.plot_directive",
    "sphinx_design",
    "myst_nb",
]

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "description"

html_theme = "pydata_sphinx_theme"
html_title = "AwesomeFigures"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_theme_options = {
    "logo": {"text": "awesomefigures"},
    "navbar_align": "content",
    "header_links_before_dropdown": 5,
    "show_nav_level": 2,
    "show_toc_level": 2,
    "navigation_with_keys": True,
    "back_to_top_button": True,
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/heri-espino/Colors",
            "icon": "fa-brands fa-github",
        }
    ],
}

html_context = {"default_mode": "light"}

html_sidebars = {
    "index": [],
    "gallery": [],
    "studio": [],
}

plot_include_source = False
plot_html_show_source_link = False
plot_html_show_formats = False
plot_formats = [("png", 180)]
plot_apply_rcparams = True


nb_execution_mode = os.environ.get("AWESOMEFIGURES_NB_EXECUTION", "auto")
nb_execution_timeout = 90
nb_execution_raise_on_error = True
