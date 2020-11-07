# flake8: noqa
# Disable Flake8 because of all the sphinx imports
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


# Airflow documentation build configuration file, created by
# sphinx-quickstart on Thu Oct  9 20:50:01 2014.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.
"""Configuration of Airflow Docs"""
import os
import sys
from glob import glob
from typing import List

import airflow
from airflow.configuration import default_config_yaml

try:
    import sphinx_airflow_theme  # pylint: disable=unused-import

    airflow_theme_is_available = True
except ImportError:
    airflow_theme_is_available = False

# Hack to allow changing for piece of the code to behave differently while
# the docs are being built. The main objective was to alter the
# behavior of the utils.apply_default that was hiding function headers
os.environ['BUILDING_AIRFLOW_DOCS'] = 'TRUE'

# == Sphinx configuration ======================================================

# -- Project information -------------------------------------------------------
# See: https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# General information about the project.
project = 'Airflow'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
# version = '1.0.0'
version = airflow.__version__

# The full version, including alpha/beta/rc tags.
# release = '1.0.0'
release = airflow.__version__

# -- General configuration -----------------------------------------------------
# See: https://www.sphinx-doc.org/en/master/usage/configuration.html

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'provider_init_hack',
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
    'sphinxarg.ext',
    'sphinxcontrib.httpdomain',
    'sphinxcontrib.jinja',
    'sphinx.ext.intersphinx',
    'autoapi.extension',
    'exampleinclude',
    'docroles',
    'removemarktransform',
    'sphinx_copybutton',
    'redirects',
    # First, generate redoc
    'sphinxcontrib.redoc',
    # Second, update redoc script
    "sphinx_script_update",
    "sphinxcontrib.spelling",
]

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

sys.path.append(os.path.join(os.path.dirname(__file__), 'exts'))

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns: List[str] = [
    # We only link to selected subpackages.
    '_api/airflow/index.rst',
    # We have custom page - operators-and-hooks-ref.rst
    '_api/airflow/providers/index.rst',
    # Packages with subpackages
    "_api/airflow/providers/amazon/index.rst",
    "_api/airflow/providers/facebook/index.rst",
    "_api/airflow/providers/microsoft/index.rst",
    "_api/airflow/providers/google/index.rst",
    "_api/airflow/providers/apache/index.rst",
    "_api/airflow/providers/yandex/index.rst",
    "_api/airflow/providers/cncf/index.rst",
    # Packages without operators
    "_api/airflow/providers/sendgrid",
    # Setup.py files of the providers
    "_api/airflow/providers/*/*setup/index.rst",
    "_api/airflow/providers/*/*/*setup/index.rst",
    # Templates or partials
    'autoapi_templates',
    'howto/operator/google/_partials',
    'howto/operator/microsoft/_partials',
]

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def _get_rst_filepath_from_path(filepath: str):
    if os.path.isdir(filepath):
        result = filepath
    elif os.path.isfile(filepath) and filepath.endswith('/__init__.py'):
        result = filepath.rpartition("/")[0]
    else:
        result = filepath.rpartition(
            ".",
        )[0]
    result += "/index.rst"

    result = f"_api/{os.path.relpath(result, ROOT_DIR)}"
    return result


# Exclude top-level packages
# do not exclude these top-level modules from the doc build:
_allowed_top_level = ("exceptions.py",)

for path in glob(f"{ROOT_DIR}/airflow/*"):
    name = os.path.basename(path)
    if os.path.isfile(path) and not path.endswith(_allowed_top_level):
        exclude_patterns.append(f"_api/airflow/{name.rpartition('.')[0]}")
    browsable_packages = ["operators", "hooks", "sensors", "providers", "executors", "models", "secrets"]
    if os.path.isdir(path) and name not in browsable_packages:
        exclude_patterns.append(f"_api/airflow/{name}")

# Exclude package index
_providers_packages_roots = {
    name.rpartition("/")[0]
    for entity in ["hooks", "operators", "secrets", "sensors"]
    for name in glob(f"{ROOT_DIR}/airflow/providers/**/{entity}", recursive=True)
}

_providers_package_indexes = {
    f"_api/{os.path.relpath(name, ROOT_DIR)}/index.rst" for name in _providers_packages_roots
}

exclude_patterns.extend(_providers_package_indexes)

# Exclude auth_backend, utils, _internal_client, example_dags in providers packages
_excluded_packages_in_providers = {
    name
    for entity in ['auth_backend', 'utils', '_internal_client', 'example_dags']
    for name in glob(f"{ROOT_DIR}/airflow/providers/**/{entity}/", recursive=True)
}
_excluded_files_in_providers = {
    _get_rst_filepath_from_path(path)
    for p in _excluded_packages_in_providers
    for path in glob(f"{p}/**/*", recursive=True)
}
_excluded_files_in_providers |= {
    _get_rst_filepath_from_path(name) for name in _excluded_packages_in_providers
}

exclude_patterns.extend(_excluded_files_in_providers)

# Add any paths that contain templates here, relative to this directory.
templates_path = ['templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, keep warnings as "system message" paragraphs in the built documents.
keep_warnings = True

# -- Options for HTML output ---------------------------------------------------
# See: https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

if airflow_theme_is_available:
    html_theme = 'sphinx_airflow_theme'

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "Airflow Documentation"

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = ""

#  given, this must be the name of an image file (path relative to the
#  configuration directory) that is the favicon of the docs. Modern browsers
#  use this as the icon for tabs, windows and bookmarks. It should be a
#  Windows-style icon file (.ico), which is 16x16 or 32x32 pixels large.
html_favicon = "../airflow/www/static/pin_32.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['static']

# A list of JavaScript filename. The entry must be a filename string or a
# tuple containing the filename string and the attributes dictionary. The
# filename must be relative to the html_static_path, or a full URI with
# scheme like http://example.org/script.js.
html_js_files = ['jira-links.js']

# Custom sidebar templates, maps document names to template names.
if airflow_theme_is_available:
    html_sidebars = {
        '**': [
            'version-selector.html',
            'searchbox.html',
            'globaltoc.html',
        ]
    }

# If false, no index is generated.
html_use_index = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = False

# A dictionary of values to pass into the template engine’s context for all pages.
html_context = {
    # Google Analytics ID.
    # For more information look at:
    # https://github.com/readthedocs/sphinx_rtd_theme/blob/master/sphinx_rtd_theme/layout.html#L222-L232
    'theme_analytics_id': 'UA-140539454-1',
}
if airflow_theme_is_available:
    html_context = {
        # Variables used to build a button for editing the source code
        #
        # The path is created according to the following template:
        #
        # https://{{ github_host|default("github.com") }}/{{ github_user }}/{{ github_repo }}/
        # {{ theme_vcs_pageview_mode|default("blob") }}/{{ github_version }}{{ conf_py_path }}
        # {{ pagename }}{{ suffix }}
        #
        # More information:
        # https://github.com/readthedocs/readthedocs.org/blob/master/readthedocs/doc_builder/templates/doc_builder/conf.py.tmpl#L100-L103
        # https://github.com/readthedocs/sphinx_rtd_theme/blob/master/sphinx_rtd_theme/breadcrumbs.html#L45
        # https://github.com/apache/airflow-site/blob/91f760c/sphinx_airflow_theme/sphinx_airflow_theme/suggest_change_button.html#L36-L40
        #
        'theme_vcs_pageview_mode': 'edit',
        'conf_py_path': '/docs/',
        'github_user': 'apache',
        'github_repo': 'airflow',
        'github_version': 'master',
        'display_github': 'master',
        'suffix': '.rst',
    }

# == Extensions configuration ==================================================

# -- Options for sphinxcontrib.jinjac ------------------------------------------
# See: https://github.com/tardyp/sphinx-jinja

# Jinja context
jinja_contexts = {'config_ctx': {"configs": default_config_yaml()}}

# -- Options for sphinx.ext.autodoc --------------------------------------------
# See: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

# This value contains a list of modules to be mocked up. This is useful when some external dependencies
# are not met at build time and break the building process.
autodoc_mock_imports = [
    'MySQLdb',
    'adal',
    'analytics',
    'azure',
    'azure.cosmos',
    'azure.datalake',
    'azure.kusto',
    'azure.mgmt',
    'boto3',
    'botocore',
    'bson',
    'cassandra',
    'celery',
    'cloudant',
    'cryptography',
    'cx_Oracle',
    'datadog',
    'distributed',
    'docker',
    'google',
    'google_auth_httplib2',
    'googleapiclient',
    'grpc',
    'hdfs',
    'httplib2',
    'jaydebeapi',
    'jenkins',
    'jira',
    'kubernetes',
    'msrestazure',
    'pandas',
    'pandas_gbq',
    'paramiko',
    'pinotdb',
    'psycopg2',
    'pydruid',
    'pyhive',
    'pyhive',
    'pymongo',
    'pymssql',
    'pysftp',
    'qds_sdk',
    'redis',
    'simple_salesforce',
    'slackclient',
    'smbclient',
    'snowflake',
    'sshtunnel',
    'tenacity',
    'vertica_python',
    'winrm',
    'zdesk',
]

# The default options for autodoc directives. They are applied to all autodoc directives automatically.
autodoc_default_options = {'show-inheritance': True, 'members': True}

# -- Options for sphinx.ext.intersphinx ----------------------------------------
# See: https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

# This config value contains the locations and names of other projects that should
# be linked to in this documentation.
intersphinx_mapping = {
    'boto3': ('https://boto3.amazonaws.com/v1/documentation/api/latest/', None),
    'celery': ('https://docs.celeryproject.org/en/stable/', None),
    'hdfs': ('https://hdfscli.readthedocs.io/en/latest/', None),
    'jinja2': ('https://jinja.palletsprojects.com/en/master/', None),
    'mongodb': ('https://api.mongodb.com/python/current/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'python': ('https://docs.python.org/3/', None),
    'requests': ('https://requests.readthedocs.io/en/master/', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/latest/', None),
    # google-api
    'google-api-core': ('https://googleapis.dev/python/google-api-core/latest', None),
    'google-cloud-automl': ('https://googleapis.dev/python/automl/latest', None),
    'google-cloud-bigquery': ('https://googleapis.dev/python/bigquery/latest', None),
    'google-cloud-bigquery-datatransfer': ('https://googleapis.dev/python/bigquerydatatransfer/latest', None),
    'google-cloud-bigquery-storage': ('https://googleapis.dev/python/bigquerystorage/latest', None),
    'google-cloud-bigtable': ('https://googleapis.dev/python/bigtable/latest', None),
    'google-cloud-container': ('https://googleapis.dev/python/container/latest', None),
    'google-cloud-core': ('https://googleapis.dev/python/google-cloud-core/latest', None),
    'google-cloud-datacatalog': ('https://googleapis.dev/python/datacatalog/latest', None),
    'google-cloud-datastore': ('https://googleapis.dev/python/datastore/latest', None),
    'google-cloud-dlp': ('https://googleapis.dev/python/dlp/latest', None),
    'google-cloud-kms': ('https://googleapis.dev/python/cloudkms/latest', None),
    'google-cloud-language': ('https://googleapis.dev/python/language/latest', None),
    'google-cloud-monitoring': ('https://googleapis.dev/python/monitoring/latest', None),
    'google-cloud-pubsub': ('https://googleapis.dev/python/pubsub/latest', None),
    'google-cloud-redis': ('https://googleapis.dev/python/redis/latest', None),
    'google-cloud-spanner': ('https://googleapis.dev/python/spanner/latest', None),
    'google-cloud-speech': ('https://googleapis.dev/python/speech/latest', None),
    'google-cloud-storage': ('https://googleapis.dev/python/storage/latest', None),
    'google-cloud-tasks': ('https://googleapis.dev/python/cloudtasks/latest', None),
    'google-cloud-texttospeech': ('https://googleapis.dev/python/texttospeech/latest', None),
    'google-cloud-translate': ('https://googleapis.dev/python/translation/latest', None),
    'google-cloud-videointelligence': ('https://googleapis.dev/python/videointelligence/latest', None),
    'google-cloud-vision': ('https://googleapis.dev/python/vision/latest', None),
}

# -- Options for sphinx.ext.viewcode -------------------------------------------
# See: https://www.sphinx-doc.org/es/master/usage/extensions/viewcode.html

# If this is True, viewcode extension will emit viewcode-follow-imported event to resolve the name of
# the module by other extensions. The default is True.
viewcode_follow_imported_members = True

# -- Options for sphinx-autoapi ------------------------------------------------
# See: https://sphinx-autoapi.readthedocs.io/en/latest/config.html

# Paths (relative or absolute) to the source code that you wish to generate
# your API documentation from.
autoapi_dirs = [
    os.path.abspath('../airflow'),
]

# A directory that has user-defined templates to override our default templates.
autoapi_template_dir = 'autoapi_templates'

# A list of patterns to ignore when finding files
autoapi_ignore = [
    '*/airflow/kubernetes/kubernetes_request_factory/*',
    '*/_internal*',
    '*/node_modules/*',
    '*/example_dags/*,',
    '*/migrations/*',
]
# Keep the AutoAPI generated files on the filesystem after the run.
# Useful for debugging.
autoapi_keep_files = True

# Relative path to output the AutoAPI files into. This can also be used to place the generated documentation
# anywhere in your documentation hierarchy.
autoapi_root = '_api'

# -- Options for ext.exampleinclude --------------------------------------------
exampleinclude_sourceroot = os.path.abspath('..')

# -- Options for ext.redirects -------------------------------------------------
redirects_file = 'redirects.txt'

# -- Options for sphinxcontrib.redoc -------------------------------------------
# See: https://sphinxcontrib-redoc.readthedocs.io/en/stable/
OPENAPI_FILE = os.path.join(os.path.dirname(__file__), "..", "airflow", "api_connexion", "openapi", "v1.yaml")
redoc = [
    {
        'name': 'Airflow REST API',
        'page': 'stable-rest-api-ref',
        'spec': OPENAPI_FILE,
        'opts': {
            'hide-hostname': True,
            'no-auto-auth': True,
        },
    },
]

# Options for script updater
redoc_script_url = "https://cdn.jsdelivr.net/npm/redoc@2.0.0-rc.30/bundles/redoc.standalone.js"
