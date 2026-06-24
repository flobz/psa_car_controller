import logging
from urllib import parse

from dash import callback_context, html, dcc
from dash.exceptions import PreventUpdate

from psa_car_controller.psa.otp.otp import new_otp_session
from psa_car_controller.psa.setup.headless_oauth import HeadlessOAuthError, get_oauth_code_headless
from psa_car_controller.psacc.application.car_controller import PSACarController
from psa_car_controller.psa.setup.app_decoder import InitialSetup
from psa_car_controller.common.mylogger import LOG_FILE
from psa_car_controller.web.app import dash_app
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State

logger = logging.getLogger(__name__)

app = PSACarController()
INITIAL_SETUP: InitialSetup = None

setup_config_layout = dbc.Row(dbc.Col(md=12, lg=2, className="m-3", children=[
    dbc.Row(html.H2('Config')),
    dbc.Row(className="ms-2", children=[
        dbc.Form([
            html.Div(className="mb-3", children=[
                dbc.Label("Car Brand", html_for="psa-app"),
                dcc.Dropdown(
                    id="psa-app",
                    options=[
                        {"label": "Peugeot", "value": "com.psa.mym.mypeugeot"},
                        {"label": "Opel", "value": "com.psa.mym.myopel"},
                        {"label": "Citroën", "value": "com.psa.mym.mycitroen"},
                        {"label": "DS", "value": "com.psa.mym.myds"},
                        {"label": "Vauxhall", "value": "com.psa.mym.myvauxhall"}
                    ],
                )]),
            html.Div(className="mb-3", children=[
                dbc.Label("Email", html_for="psa-email"),
                dbc.Input(type="email", id="psa-email", placeholder="Enter email"),
                dbc.FormText(
                    "PSA account email",
                    color="secondary",
                )]),
            html.Div(className="mb-3", children=[
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
            html.Div(className="mb-3", children=[
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


def log_layout():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            log_text = f.read()
    except Exception as e:
        log_text = f"Can't read log file: {e}"
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
        dbc.Tab([config_otp_layout], label="OTP config", tab_id="otp")])


@dash_app.callback(
    Output("form_result", "children"),
    Input("submit-form", "n_clicks"),
    State("psa-app", "value"),
    State("psa-email", "value"),
    State("psa-password", "value"),
    State("psa-countrycode", "value"))
def connectPSA(n_clicks, app_name, email, password, countrycode):  # pylint: disable=unused-argument
    ctx = callback_context
    if ctx.triggered:
        logger.info("Initial setup...")
        try:
            global INITIAL_SETUP
            INITIAL_SETUP = InitialSetup(app_name, email, password, countrycode)
            auth_url = INITIAL_SETUP.psacc.manager.generate_redirect_url()
            scheme = INITIAL_SETUP.psacc.manager.redirect_uri.split("://")[0]
        except Exception as e:
            logger.exception(e)
            return dbc.Alert(str(e), color="danger")

        # Attempt automatic headless OAuth
        try:
            code = get_oauth_code_headless(auth_url, email, password, scheme)
            INITIAL_SETUP.connect(code)
            return dbc.Alert(["Login successful! ",
                              html.A("Go to OTP config",
                                     href=dash_app.config.requests_pathname_prefix + "config_otp")], color="success")
        except HeadlessOAuthError as e:
            redirect_uri = parse.quote(auth_url)
            return dbc.Alert(
                [
                    html.P("Automatic login failed. Please complete manually: "),
                    html.A(
                        "Go to login",
                        href=f"{dash_app.config.requests_pathname_prefix}config_connect?url={redirect_uri}"),
                    html.Hr(),
                    html.P("Debug information (please include in GitHub issue):"),
                    dbc.Label("Last URL:"),
                    dbc.Input(
                        value=e.url,
                        readonly=True,
                        style={
                            "margin-bottom": "10px"}),
                    dbc.Label("Console Logs:"),
                    dbc.Textarea(
                        value="\n".join(
                            e.logs),
                        style={
                            "height": "100px",
                            "font-family": "monospace",
                            "font-size": "12px",
                            "margin-bottom": "10px"},
                        readonly=True,
                    ),
                    dbc.Label("HTML Content:"),
                    dbc.Textarea(
                        value=e.html,
                        style={
                            "height": "200px",
                            "font-family": "monospace",
                            "font-size": "12px"},
                        readonly=True,
                    ),
                ],
                color="warning")
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Headless OAuth failed (%s), falling back to manual flow", e)

        # Manual fallback
        redirect_uri = parse.quote(auth_url)
        return dbc.Alert(
            ["Automatic login failed. Please complete manually: ",
             html.A("Go to login",
                    href=f"{dash_app.config.requests_pathname_prefix}config_connect?url={redirect_uri}")],
            color="warning"
        )
    return ""


@dash_app.callback(
    Output("sms-demand-result", "children"),
    Input("ask-sms", "n_clicks"))
def askCode(n_clicks):  # pylint: disable=unused-argument
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
def finishOtp(n_clicks, code_pin, sms_code):  # pylint: disable=unused-argument
    ctx = callback_context
    if ctx.triggered:
        try:
            otp_session = new_otp_session(sms_code, code_pin, app.myp.remote_client.otp)
            app.myp.remote_client.otp = otp_session
            app.myp.save_config()
            app.start_remote_control()
            return dbc.Alert(["OTP config finish !!! ", html.A(
                "Go to home", href=dash_app.config.requests_pathname_prefix)], color="success")
        except Exception as e:
            res = str(e)
            logger.exception("finishOtp:")
            return dbc.Alert(res, color="danger")
    raise PreventUpdate()
