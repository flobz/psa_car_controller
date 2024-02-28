import logging

from dash import callback_context, html, dcc
from dash.exceptions import PreventUpdate
from flask import request

from psa_car_controller.web.app import dash_app
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State

from psa_car_controller.web.view import config_views

logger = logging.getLogger(__name__)


def get_oauth_config_layout(redirect_url):
    return dbc.Row(dbc.Col(md=12, lg=2, className="m-3", children=[
        dbc.Row(html.H2('Connection to PSA')),
        dbc.Row(className="ms-2", children=[
            html.Div(html.P([
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
                html.Div([
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


@dash_app.callback(
    Output("oauth-result", "children"),
    Input("finish-oauth", "n_clicks"),
    State("psa-oauth-code", "value"))
def finish_oauth(n_clicks, code):  # pylint: disable=unused-argument
    ctx = callback_context
    if ctx.triggered:
        try:
            config_views.INITIAL_SETUP.connect(code)
            return dbc.Alert(["PSA login finish !",
                              html.A(" Go to otp config", href=request.url_root + "config_otp")],
                             color="success")
        except Exception as e:
            logger.exception("finish_oauth:")
            return dbc.Alert(str(e), color="danger")
    raise PreventUpdate()
