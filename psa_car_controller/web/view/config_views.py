import logging
import configparser  # Moved from lines 113 and 400
from urllib import parse

from dash import callback_context, html, dcc
from dash.exceptions import PreventUpdate
from flask import request

from psa_car_controller.psa.otp.otp import new_otp_session
from psa_car_controller.psacc.application.car_controller import PSACarController
from psa_car_controller.psa.setup.app_decoder import InitialSetup
from psa_car_controller.common.mylogger import LOG_FILE
from psa_car_controller.web.app import dash_app
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State

from psa_car_controller.psacc.repository.config_repository import ConfigRepository

from psa_car_controller.web import figures  # pylint: disable=cyclic-import
from psa_car_controller.web.view import views  # pylint: disable=cyclic-import

logger = logging.getLogger(__name__)

app = PSACarController()
INITIAL_SETUP: InitialSetup = None

setup_config_layout = dbc.Row(dbc.Col(md=12, lg=2, className="m-3", children=[
    dbc.Row(html.H2('Config')),
    dbc.Row(className="ms-2", children=[
        dbc.Form([
            html.Div([
                dbc.Label("Car Brand", html_for="psa-app"),
                dcc.Dropdown(
                    id="psa-app",
                    options=[
                        {"label": "Peugeot", "value": "com.psa.mym.mypeugeot"},
                        {"label": "Opel", "value": "com.psa.mym.myopel"},
                        {"label": "CitroÃ«n", "value": "com.psa.mym.mycitroen"},
                        {"label": "DS", "value": "com.psa.mym.myds"},
                        {"label": "Vauxhall", "value": "com.psa.mym.myvauxhall"}
                    ],
                )]),
            html.Div([
                dbc.Label("Email", html_for="psa-email"),
                dbc.Input(type="email", id="psa-email", placeholder="Enter email"),
                dbc.FormText(
                    "PSA account email",
                    color="secondary",
                )]),
            html.Div([
                dbc.Label("Password", html_for="psa-password"),
                dbc.Input(
                    type="password",
                    id="psa-password",
                    placeholder="Enter password",
                ),
                dbc.FormText(
                    "PSA account password",
                    color="secondary",
                )]),
            html.Div([
                dbc.Label("Country code", html_for="countrycode"),
                dbc.Input(
                    type="text",
                    id="psa-countrycode",
                    placeholder="Enter your country code",
                ),
                dbc.FormText(
                    "Example: FR for FRANCE or GB for Great Britain...",
                    color="secondary",
                )]),
            dbc.Row(dbc.Button("Submit", color="primary", id="submit-form")),
            dbc.Row(dbc.FormText(
                "After submit be patient it can take some time...",
                color="secondary")),
            dcc.Loading(
                id="loading-2",
                children=[html.Div([html.Div(id="form_result")])],
                type="circle",
            ),
        ])
    ])]))

config_otp_layout = dbc.Row(dbc.Col(className="col-md-12 col-lg-2 m-3", children=[
    dbc.Row(html.H2('Config OTP')),
    dbc.Form(className="ms-2", children=[
        dbc.Label("Click to receive a code by SMS", html_for="ask-sms"),
        dbc.Button("Send SMS", color="info", id="ask-sms"),
        html.Div(id="sms-demand-result", className="mt-2"),
        dbc.Label("Write the code you just received by SMS", html_for="psa-email"),
        dbc.Input(type="text", id="psa-code", placeholder="Enter code"),
        dbc.Label("Enter your PIN code", html_for="psa-pin"),
        dbc.Input(
            type="password",
            id="psa-pin",
            placeholder="Enter codepin",
        ),
        dbc.FormText(
            "It's a digit password",
            color="secondary",
        ),
        html.Div([
            dbc.Button("Submit", color="primary", id="finish-otp"),
            html.Div(id="opt-result")]),
    ])]))


def _get_options_layout():
    """Build the Options tab layout, reading current config for initial values."""
    try:
        config = ConfigRepository.read_config()
        current_imperial = config.Options.use_imperial
    except Exception:  # pylint: disable=broad-except
        current_imperial = False

    try:
        ini = configparser.ConfigParser(allow_no_value=True)
        ini.read("config.ini")

        def _get(section, key, fallback=""):
            return ini.get(section, key, fallback=fallback) if ini.has_section(section) else fallback
    except Exception:  # pylint: disable=broad-except
        # Added blank line before nested definition (E306)
        # Prefixed unused arguments with underscores
        def _get(_section, _key, fallback=""):  # pylint: disable=function-redefined
            return fallback

    def _row(label, input_el, hint=""):
        """Horizontal form row: label (left) | input (centre) | hint (right)."""
        return dbc.Row(className="align-items-center mb-2", children=[
            dbc.Col(dbc.Label(label, className="mb-0 text-end"), md=3),
            dbc.Col(input_el, md=4),
            dbc.Col(html.Small(hint, className="text-muted") if hint else None, md=5),
        ])

    currency = _get("General", "currency", "£")

    return dbc.Row(dbc.Col(md=12, lg=8, className="m-3", children=[
        dbc.Row(html.H2('Options')),

        dbc.Row(className="ms-2 mt-3 mb-3", children=[
            dbc.Label("Display units", html_for="options-unit-toggle", className="fw-bold"),
            dbc.Row(className="align-items-center g-2 mt-1", children=[
                dbc.Col(html.Span("Metric (km, km/h)", className="text-muted"), width="auto"),
                dbc.Col(
                    dbc.Switch(id="options-unit-toggle", value=current_imperial, className="mx-2"),
                    width="auto",
                ),
                dbc.Col(html.Span("Imperial (mi, mph)", className="text-muted"), width="auto"),
            ]),
            dbc.FormText(
                "Changes the units shown in the dashboard only. "
                "All data is always stored internally as metric.",
                color="secondary",
                className="mt-1",
            ),
        ]),

        html.Hr(className="my-4"),

        dbc.Row(className="ms-2 mb-3", children=[
            dbc.Label("General", className="fw-bold fs-6 mb-2"),
            _row(
                "Currency symbol",
                dbc.Input(type="text", id="opt-currency", value=currency,
                          placeholder="£", maxLength=5),
                "e.g. £, €, $",
            ),
            _row(
                "Minimum trip length",
                dbc.InputGroup([
                    dbc.Input(type="number", id="opt-min-trip",
                              value=_get("General", "minimum trip length", "1"),
                              placeholder="1", min=0, step=0.1),
                    dbc.InputGroupText("km"),
                ]),
                "Shorter trips are excluded from statistics",
            ),
        ]),

        html.Hr(className="my-4"),

        dbc.Row(className="ms-2 mb-3", children=[
            dbc.Label("Electricity pricing", className="fw-bold fs-6 mb-2"),
            _row(
                "Day price",
                dbc.InputGroup([
                    dbc.InputGroupText(currency, id="opt-currency-day"),
                    dbc.Input(type="number", id="opt-day-price",
                              value=_get("Electricity config", "day price", ""),
                              placeholder="0.15", min=0, step=0.001),
                ]),
                "Price per kWh for daytime charging",
            ),
            _row(
                "Night price",
                dbc.InputGroup([
                    dbc.InputGroupText(currency, id="opt-currency-night"),
                    dbc.Input(type="number", id="opt-night-price",
                              value=_get("Electricity config", "night price", ""),
                              placeholder="0.10", min=0, step=0.001),
                ]),
                "Optional off-peak rate",
            ),
            _row(
                "Night start",
                dbc.Input(type="text", id="opt-night-start",
                          value=_get("Electricity config", "night hour start", ""),
                          placeholder="22h30"),
                "Format: 22h30",
            ),
            _row(
                "Night end",
                dbc.Input(type="text", id="opt-night-end",
                          value=_get("Electricity config", "night hour end", ""),
                          placeholder="06h00"),
                "Format: 06h00",
            ),
        ]),

        html.Hr(className="my-4"),

        dbc.Row(className="ms-2 mb-3", children=[
            dbc.Label("DC / fast charging", className="fw-bold fs-6 mb-2"),
            _row(
                "DC charge price",
                dbc.InputGroup([
                    dbc.InputGroupText(currency, id="opt-currency-dc"),
                    dbc.Input(type="number", id="opt-dc-price",
                              value=_get("Electricity config", "dc charge price", ""),
                              placeholder="0.65", min=0, step=0.001),
                ]),
                "Price per kWh for DC charging",
            ),
            _row(
                "High-speed DC price",
                dbc.InputGroup([
                    dbc.InputGroupText(currency, id="opt-currency-hv"),
                    dbc.Input(type="number", id="opt-hv-price",
                              value=_get("Electricity config", "high speed dc charge price", ""),
                              placeholder="0.79", min=0, step=0.001),
                ]),
                "Price per kWh for high-speed DC",
            ),
            _row(
                "High-speed threshold",
                dbc.InputGroup([
                    dbc.Input(type="number", id="opt-hv-threshold",
                              value=_get("Electricity config", "high speed dc charge threshold", ""),
                              placeholder="50", min=0, step=1),
                    dbc.InputGroupText("kW"),
                ]),
                "Minimum kW to classify as high-speed",
            ),
            _row(
                "Charger efficiency",
                dbc.Input(type="number", id="opt-efficiency",
                          value=_get("Electricity config", "charger efficiency", "0.8942"),
                          placeholder="0.8942", min=0, max=1, step=0.0001),
                "0-1 (default: 0.8942)",
            ),
        ]),

        html.Hr(className="my-4"),

        dbc.Row(className="ms-2", children=[
            dbc.Col(width="auto", children=[
                dbc.Button("Save", color="primary", id="options-save-btn", className="w-auto"),
            ]),
            html.Div(id="options-save-result", className="mt-2"),
        ]),
    ]))


def log_layout():
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log_text = f.read()
    return html.H3(className="m-2", children=["Log:", dbc.Container(
        fluid=True,
        style={"height": "80vh",
               "overflow": "auto",
               "display": "flex",
               "flex-direction": "column-reverse",
               "white-space": "pre-line"},
        children=log_text,
        className="m-3 bg-light h5"),
        html.Div(id="empty-div")])


def config_layout(activeTabs="log"):
    return dbc.Tabs(active_tab=activeTabs, children=[
        dbc.Tab([log_layout()], label="Log", tab_id="log"),
        dbc.Tab([setup_config_layout], label="User config", tab_id="login"),
        dbc.Tab([config_otp_layout], label="OTP config", tab_id="otp"),
        dbc.Tab([_get_options_layout()], label="Options", tab_id="options"),
    ])


@dash_app.callback(
    Output("form_result", "children"),
    Input("submit-form", "n_clicks"),
    State("psa-app", "value"),
    State("psa-email", "value"),
    State("psa-password", "value"),
    State("psa-countrycode", "value"))
def connectPSA(_n_clicks, app_name, email, password, countrycode):  # pylint: disable=unused-argument
    ctx = callback_context
    if ctx.triggered:
        logger.info("Initial setup...")
        try:
            global INITIAL_SETUP
            INITIAL_SETUP = InitialSetup(app_name, email, password, countrycode)
            redirect_uri = parse.quote(INITIAL_SETUP.psacc.manager.generate_redirect_url())
            return dbc.Alert(["Success !",
                              html.A(" Go to login",
                                     href=f"{request.url_root}config_connect?url={redirect_uri}")],
                             color="success")
        except Exception as e:
            res = str(e)
            logger.exception(e)
            return dbc.Alert(res, color="danger")
    else:
        return ""


@dash_app.callback(
    Output("sms-demand-result", "children"),
    Input("ask-sms", "n_clicks"))
def askCode(_n_clicks):  # pylint: disable=unused-argument
    ctx = callback_context
    if ctx.triggered:
        try:
            app.myp.remote_client.get_sms_otp_code()
            return dbc.Alert("SMS sent", color="success")
        except Exception as e:
            res = str(e)
            return dbc.Alert(res, color="danger")
    raise PreventUpdate()


@dash_app.callback(
    Output("opt-result", "children"),
    Input("finish-otp", "n_clicks"),
    State("psa-pin", "value"),
    State("psa-code", "value"))
def finishOtp(_n_clicks, code_pin, sms_code):  # pylint: disable=unused-argument
    ctx = callback_context
    if ctx.triggered:
        try:
            otp_session = new_otp_session(sms_code, code_pin, app.myp.remote_client.otp)
            app.myp.remote_client.otp = otp_session
            app.myp.save_config()
            app.start_remote_control()
            return dbc.Alert(["OTP config finish !!! ", html.A("Go to home", href=request.url_root)],
                             color="success")
        except Exception as e:
            res = str(e)
            logger.exception("finishOtp:")
            return dbc.Alert(res, color="danger")
    raise PreventUpdate()


@dash_app.callback(
    Output("opt-currency-day", "children"),
    Output("opt-currency-night", "children"),
    Output("opt-currency-dc", "children"),
    Output("opt-currency-hv", "children"),
    Input("opt-currency", "value"),
)
def update_currency_symbols(currency):
    """Keep all currency prefix badges in sync with the currency input field."""
    symbol = (currency or "£").strip() or "£"
    return symbol, symbol, symbol, symbol


# Added disable for complexity as Dash callbacks require explicit arguments
@dash_app.callback(
    Output("options-save-result", "children"),
    Input("options-save-btn", "n_clicks"),
    State("options-unit-toggle", "value"),
    State("opt-currency", "value"),
    State("opt-min-trip", "value"),
    State("opt-day-price", "value"),
    State("opt-night-price", "value"),
    State("opt-night-start", "value"),
    State("opt-night-end", "value"),
    State("opt-dc-price", "value"),
    State("opt-hv-price", "value"),
    State("opt-hv-threshold", "value"),
    State("opt-efficiency", "value"),
    prevent_initial_call=True,
)
# pylint: disable=too-many-arguments, too-many-locals, too-many-positional-arguments
def save_options(_n_clicks, use_imperial,  # pylint: disable=unused-argument
                 currency, min_trip,
                 day_price, night_price, night_start, night_end,
                 dc_price, hv_price, hv_threshold, efficiency):
    """Persist all options to config and config.ini."""
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate()
    try:
        ini = configparser.ConfigParser(allow_no_value=True)
        ini.read("config.ini")

        if not ini.has_section("General"):
            ini.add_section("General")
        if not ini.has_section("Electricity config"):
            ini.add_section("Electricity config")

        ini.set("General", "currency", (currency or "£").strip())
        ini.set("General", "minimum trip length", str(min_trip or "1").strip())

        def _set_elec(key, value):
            ini.set("Electricity config", key, str(value).strip() if value not in (None, "") else "")

        _set_elec("day price", day_price)
        _set_elec("night price", night_price)
        _set_elec("night hour start", night_start)
        _set_elec("night hour end", night_end)
        _set_elec("dc charge price", dc_price)
        _set_elec("high speed dc charge price", hv_price)
        _set_elec("high speed dc charge threshold", hv_threshold)
        _set_elec("charger efficiency", efficiency or "0.8942")

        with open("config.ini", "w", encoding="utf-8") as f:
            ini.write(f)

        config = ConfigRepository.read_config()
        config.Options.use_imperial = bool(use_imperial)
        config.write_config()

        figures.USE_IMPERIAL = bool(use_imperial)
        figures.CURRENCY = (currency or "£").strip()
        views.cached_layout = None
        views.update_trips()

        # Removed unused 'unit_label' variable
        # Removed 'f' prefix from string without interpolation
        return dbc.Alert(
            "Saved! Settings applied immediately.",
            color="success",
            duration=6000,
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("save_options:")
        return dbc.Alert(str(e), color="danger")
