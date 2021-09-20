from dash import callback_context
from dash.exceptions import PreventUpdate
from flask import request

from app_decoder import firstLaunchConfig
from libs.config import Config
from mylogger import LOG_FILE
from otp.otp import new_otp_session
from web.app import dash_app
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html

config = Config()
config_layout = dbc.Row(dbc.Col(className="col-md-12 col-lg-2 ml-2", children=[
    html.H2('Config'),
    dbc.Form([
        dbc.FormGroup([
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
        dbc.FormGroup(
            [
                dbc.Label("Email", html_for="psa-email"),
                dbc.Input(type="email", id="psa-email", placeholder="Enter email"),
                dbc.FormText(
                    "PSA account email",
                    color="secondary",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Password", html_for="psa-password"),
                dbc.Input(
                    type="password",
                    id="psa-password",
                    placeholder="Enter password",
                ),
                dbc.FormText(
                    "PSA account password",
                    color="secondary",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Country code", html_for="countrycode"),
                dbc.Input(
                    type="text",
                    id="psa-countrycode",
                    placeholder="Enter your country code",
                ),
                dbc.FormText(
                    "Example: FR for FRANCE or GB for Great Britain...",
                    color="secondary",
                )
            ]
        ),
        dbc.FormGroup([
            dbc.Button("Submit", color="primary", id="submit-form"),
            dbc.FormText(
                "After submit be patient it can take some time...",
                color="secondary",
            ),
            dcc.Loading(
                id="loading-2",
                children=[html.Div([html.Div(id="form_result")])],
                type="circle",
            )]
        ),
    ])]))

config_otp_layout = dbc.Row(dbc.Col(className="col-md-12 col-lg-2 ml-2", children=[
    html.H2('Config OTP'),
    dbc.Form([
        dbc.FormGroup([
            dbc.Label("Click to receive a code by SMS", html_for="ask-sms"),
            dbc.Button("Send SMS", color="info", id="ask-sms"),
            html.Div(id="sms-demand-result", className="mt-2")
        ]),
        dbc.FormGroup(
            [
                dbc.Label("Write the code you just received by SMS", html_for="psa-email"),
                dbc.Input(type="text", id="psa-code", placeholder="Enter code"),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Enter your code PIN", html_for="psa-pin"),
                dbc.Input(
                    type="password",
                    id="psa-pin",
                    placeholder="Enter codepin",
                ),
                dbc.FormText(
                    "It's a digit password",
                    color="secondary",
                ),
                dbc.Button("Submit", color="primary", id="finish-otp")
            ]
        ),
        html.Div(id="opt-result")
    ])]))


def log_layout():
    with open(LOG_FILE, "r") as f:
        log_text = f.read()
    return html.H3(children=["Log:", dbc.Textarea(
        valid=True,
        bs_size="sm",
        className="mt-3",
        style={"height": "80vh"},
        placeholder="Log",
        contentEditable=False,
        value=log_text
    )])


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
        try:
            res = firstLaunchConfig(app_name, email, password, countrycode)
            config.load_app()
            return dbc.Alert([res, html.A(" Go to otp config", href=request.url_root + "config_otp")], color="success")
        except Exception as e:
            res = str(e)
            return dbc.Alert(res, color="danger")
    else:
        return ""
    raise PreventUpdate()


@dash_app.callback(
    Output("sms-demand-result", "children"),
    Input("ask-sms", "n_clicks"))
def askCode(n_clicks):  # pylint: disable=unused-argument
    ctx = callback_context
    if ctx.triggered:
        try:
            config.myp.get_sms_otp_code()
            return dbc.Alert("Sms sent", color="success")
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
            otp_session = new_otp_session(smscode=sms_code, codepin=code_pin)
            config.myp.otp = otp_session
            config.myp.save_config()
            config.start_remote_control()
            return dbc.Alert(["OTP config finish !!! ", html.A("Go to home", href=request.url_root)],
                             color="success")
        except Exception as e:
            res = str(e)
            return dbc.Alert(res, color="danger")
    raise PreventUpdate()
