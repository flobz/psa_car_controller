import logging

from dash import callback_context, html, dcc
from dash.exceptions import PreventUpdate

from psa_car_controller.psa.setup.app_decoder import InitialSetup
from psa_car_controller.web.app import dash_app
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State

from psa_car_controller.web.view import config_views

logger = logging.getLogger(__name__)

# Page Layout for Manual OAuth Configuration
def setup_config_manual_layout():
    return dbc.Col(md=12, lg=2, className="m-3", children=[
        dbc.Row(html.H2('Connection to PSA (Advanced)')),
        dbc.Row(html.A("Please follow the instructions here.", href="https://github.com/flobz/psa_car_controller/discussions/779")),
        dbc.Row(className="ms-2", children=[
            dbc.Form([
                html.Div(className="mb-3", children=[
                    dbc.Label("Car Brand", html_for="psa-manual-app"),
                    dcc.Dropdown(
                        id="psa-manual-app",
                        options=[
                            {"label": "Peugeot", "value": "com.psa.mym.mypeugeot"},
                            {"label": "Opel", "value": "com.psa.mym.myopel"},
                            {"label": "Citroën", "value": "com.psa.mym.mycitroen"},
                            {"label": "DS", "value": "com.psa.mym.myds"},
                            {"label": "Vauxhall", "value": "com.psa.mym.myvauxhall"}
                        ],
                    )
                ]),
                html.Div(className="mb-3", children=[
                    dbc.Label("Email", html_for="psa-manual-email"),
                    dbc.Input(type="email", id="psa-manual-email", placeholder="Enter email"),
                ]),
                html.Div(className="mb-3", children=[
                    dbc.Label("Password", html_for="psa-manual-password"),
                    dbc.Input(type="password", id="psa-manual-password", placeholder="Enter password"),
                ]),
                html.Div(className="mb-3", children=[
                    dbc.Label("Country code", html_for="psa-manual-countrycode"),
                    dbc.Input(type="text", id="psa-manual-countrycode", placeholder="Enter your country code"),
                ]),
                dbc.Row(dbc.Button("Generate OAuth URL", color="primary", id="generate-manual-oauth")),
                html.Div(id="manual-oauth-link", className="mt-3"),
                html.Div(className="mb-3", children=[
                    dbc.Label("Code", html_for="psa-oauth-code"),
                    dbc.Input(type="text", id="psa-oauth-code", placeholder="Enter OAuth Code"),
                    dbc.FormText("Enter PSA OAuth Code", color="secondary")
                ]),
                dbc.Row(dbc.Button("Submit", color="primary", id="finish-oauth")),
                dcc.Loading(
                    id="loading-2",
                    children=[html.Div([html.Div(id="oauth-result")])],
                    type="circle",
                ),
            ])
        ]),
    ])

def get_oauth_config_layout(redirect_url):
    return dbc.Row(dbc.Col(md=12, lg=2, className="m-3", children=[
        dbc.Row(html.H2('Connection to PSA (manual fallback)')),
        dbc.Row(className="ms-2", children=[
            html.Div(html.P([
                "Automatic login failed. Complete the OAuth flow manually:", html.Br(),
                html.A("1. Click here", href=redirect_url, target="_blank"), html.Br(),
                "2. Complete the login procedure there too until you see 'LOGIN SUCCESSFUL'", html.Br(),
                "3. Open your browser's DevTools (F12) and then the click on 'Network' tab", html.Br(),
                "4. Hit the final 'OK' button, under 'LOGIN SUCCESSFUL'", html.Br(),
                "5. Find in the network tab: xxxx://oauth2redirect....?code=<copy this part>&scope=openid... ",
                html.Br(),
                html.A("You can find more info here",
                       href="https://github.com/flobz/psa_car_controller/discussions/779"), html.Br()]
            )),
            dbc.Form([
                html.Div(className="mb-3", children=[
                    dbc.Label("Code", html_for="psa-oauth-code"),
                    dbc.Input(type="text", id="psa-oauth-code", placeholder="Enter login code"),
                    dbc.FormText(
                        "PSA code from step above",
                        color="secondary",
                    )]),
                dbc.Row(dbc.Button("Submit", color="primary", id="finish-oauth")),
                dcc.Loading(
                    id="loading-2",
                    children=[html.Div([html.Div(id="oauth-result")])],
                    type="circle",
                ),
            ])
        ])]))

# Generate the OAuth URL and display it to the user, so they can complete the login flow manually.
@dash_app.callback(
    Output("manual-oauth-link", "children"),
    Input("generate-manual-oauth", "n_clicks"),
    State("psa-manual-app", "value"),
    State("psa-manual-email", "value"),
    State("psa-manual-password", "value"),
    State("psa-manual-countrycode", "value"))
def generate_manual_oauth_url(n_clicks, app_name, email, password, countrycode):
    ctx = callback_context
    if ctx.triggered:
        try:
            config_views.INITIAL_SETUP = InitialSetup(app_name, email, password, countrycode)
            auth_url = config_views.INITIAL_SETUP.psacc.manager.generate_redirect_url()
            return dbc.Alert([
                html.P("Open the following login URL and then paste the code returned by the redirect."),
                html.A("Open OAuth login", href=auth_url, target="_blank"),
            ], color="info")
        except Exception as e:
            logger.exception("generate_manual_oauth_url:")
            return dbc.Alert(str(e), color="danger")
    raise PreventUpdate()


@dash_app.callback(
    Output("oauth-result", "children"),
    Input("finish-oauth", "n_clicks"),
    State("psa-oauth-code", "value"))
def finish_oauth(n_clicks, code):  # pylint: disable=unused-argument
    ctx = callback_context
    if ctx.triggered:
        try:
            config_views.INITIAL_SETUP.connect(code)
            return dbc.Alert(["PSA login finish !", html.A(" Go to otp config",
                             href=dash_app.config.requests_pathname_prefix + "config_otp")], color="success")
        except Exception as e:
            logger.exception("finish_oauth:")
            return dbc.Alert(str(e), color="danger")
    raise PreventUpdate()
