import locale
import logging
import sys

import dash_bootstrap_components as dbc
from flask import Flask
from werkzeug import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix

from psa_car_controller.web.dash_custom import DashCustom

try:
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
except ImportError:
    from werkzeug import DispatcherMiddleware

from psa_car_controller.common.mylogger import file_handler
if sys.version_info >= (3, 8):
    import importlib
else:
    import importlib_metadata as importlib

# pylint: disable=invalid-name
app = None
dash_app = None

logger = logging.getLogger(__name__)


class MyProxyFix(ProxyFix):
    def __init__(self, dashapp):
        self.flask_app = dashapp.server
        self.dash_app = dash_app
        super().__init__(self.flask_app.wsgi_app, x_host=1, x_port=1, x_prefix=1)

    def __call__(self, environ, start_response):
        prefix = environ.get("HTTP_X_INGRESS_PATH") or environ.get("HTTP_X_FORWARDED_PREFIX")
        if prefix:
            environ["HTTP_X_FORWARDED_PREFIX"] = prefix
            self.flask_app.config['APPLICATION_ROOT'] = environ['SCRIPT_NAME'] = prefix
            prefix += "/"
            self.dash_app.requests_pathname_external_prefix = prefix
            self.dash_app.config.assets_external_path = prefix
        else:
            # In Dash 4.0, requests_pathname_prefix is "/" when base_path is "/"
            # but APPLICATION_ROOT should be None (not "/") for root-mounted apps
            rpp = self.dash_app.config.requests_pathname_prefix
            # APPLICATION_ROOT should not have trailing slash (Flask convention)
            if rpp and rpp != "/":
                self.flask_app.config['APPLICATION_ROOT'] = rpp.rstrip('/')
            else:
                self.flask_app.config['APPLICATION_ROOT'] = None
            # requests_pathname_external_prefix should be empty string for root
            self.dash_app.requests_pathname_external_prefix = rpp if rpp and rpp != "/" else ""
        return super().__call__(environ, start_response)


def start_app(*args, **kwargs):
    run(config_flask(*args, **kwargs))


def config_flask(title, base_path, debug: bool, host, port, reloader=False,
                 # pylint: disable=too-many-arguments,too-many-positional-arguments
                 unminified=False, view="psa_car_controller.web.view.views"):
    global app, dash_app
    reload_view = app is not None
    app = Flask(__name__)
    app.logger.addHandler(file_handler)
    try:
        lang = locale.getlocale()[0].split("_")[0]
        locale.setlocale(locale.LC_TIME, ".".join(locale.getlocale()))  # make sure LC_TIME is set
        if lang != "en":
            locale_url = [f"https://cdn.plot.ly/plotly-locale-{lang}-latest.js"]
        else:
            locale_url = None
    except (IndexError, locale.Error):
        locale_url = None
        logger.warning("Can't get language")
    if unminified:
        locale_url = ["assets/plotly-with-meta.js"]
    app.config["DEBUG"] = debug
    if base_path == "/":
        application = DispatcherMiddleware(app)
        requests_pathname_prefix = "/"
    else:
        application = DispatcherMiddleware(Flask('dummy_app'), {base_path: app})
        requests_pathname_prefix = base_path + "/"
    dash_app = DashCustom(external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
                          external_scripts=locale_url, title=title,
                          server=app, requests_pathname_prefix=requests_pathname_prefix,
                          suppress_callback_exceptions=True)
    dash_app.enable_dev_tools(debug)
    app.wsgi_app = MyProxyFix(dash_app)
    # keep this line
    importlib.import_module(view)
    if reload_view:
        importlib.reload(view)
    return {"hostname": host, "port": port, "application": application, "use_reloader": reloader, "use_debugger": debug}


def run(config):
    return run_simple(**config)
