import locale

import dash
import dash_bootstrap_components as dbc
from flask import Flask

from werkzeug import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix

try:
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
except ImportError:
    from werkzeug import DispatcherMiddleware

from mylogger import logger
import importlib

# pylint: disable=invalid-name
app = None
dash_app = None
dispatcher = None


def start_app(*args, **kwargs):
    run(config_flask(*args, **kwargs))


def config_flask(title, base_path, debug: bool, host, port, reloader=False,  # pylint: disable=too-many-arguments
                 unminified=False, view="web.views"):
    global app, dash_app, dispatcher
    reload_view = app is not None
    app = Flask(__name__)
    try:
        lang = locale.getlocale()[0].split("_")[0]
        locale.setlocale(locale.LC_TIME, ".".join(locale.getlocale()))  # make sure LC_TIME is set
        locale_url = [f"https://cdn.plot.ly/plotly-locale-{lang}-latest.js"]
    except (IndexError, locale.Error):
        locale_url = None
        logger.warning("Can't get language")
    if unminified:
        locale_url = ["assets/plotly-with-meta.js"]
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config["DEBUG"] = debug
    if base_path == "/":
        application = DispatcherMiddleware(app)
        requests_pathname_prefix = None
    else:
        application = DispatcherMiddleware(Flask('dummy_app'), {base_path: app})
        requests_pathname_prefix = base_path + "/"
    dash_app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], external_scripts=locale_url, title=title,
                         server=app, requests_pathname_prefix=requests_pathname_prefix,
                         suppress_callback_exceptions=True)
    dash_app.enable_dev_tools(reloader)
    # keep this line
    importlib.import_module(view)
    if reload_view:
        importlib.reload(view)
    return {"hostname": host, "port": port, "application": application, "use_reloader": reloader, "use_debugger": debug}


def run(config):
    return run_simple(**config)
