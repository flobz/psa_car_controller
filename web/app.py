import threading
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

from charge_control import ChargeControls
from mylogger import logger
from my_psacc import MyPSACC

# pylint: disable=invalid-name

app = None
dash_app = None
dispatcher = None
# noinspection PyTypeChecker
myp: MyPSACC = None
# noinspection PyTypeChecker
chc: ChargeControls = None


def start_app(title, base_path, debug: bool, host, port, reloader=False,   # pylint: disable=too-many-arguments
              unminified=False):
    global app, dash_app, dispatcher
    try:
        lang = locale.getlocale()[0].split("_")[0]
        locale.setlocale(locale.LC_TIME, ".".join(locale.getlocale()))  # make sure LC_TIME is set
        locale_url = [f"https://cdn.plot.ly/plotly-locale-{lang}-latest.js"]
    except (IndexError, locale.Error):
        locale_url = None
        logger.warning("Can't get language")
    if unminified:
        locale_url = ["assets/plotly-with-meta.js"]
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config["DEBUG"] = debug
    if base_path == "/":
        application = DispatcherMiddleware(app)
        requests_pathname_prefix = None
    else:
        application = DispatcherMiddleware(Flask('dummy_app'), {base_path: app})
        requests_pathname_prefix = base_path + "/"
    dash_app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], external_scripts=locale_url, title=title,
                         server=app, requests_pathname_prefix=requests_pathname_prefix)
    dash_app.enable_dev_tools(reloader)
    # keep this line
    import web.views  # pylint: disable=unused-import,import-outside-toplevel
    return run_simple(host, port, application, use_reloader=reloader, use_debugger=debug)


def save_config(my_peugeot: MyPSACC, name):
    my_peugeot.save_config(name)
    threading.Timer(30, save_config, args=[my_peugeot, name]).start()
