import dash_bootstrap_components as dbc
from dash._utils import create_callback_id
from dash.dependencies import Output, MATCH, Input

from web.app import dash_app

RESPONSE = "-response"


class Button:
    def __init__(self, role, button_id, label, fct, prevent_initial_call=True):  # pylint: disable=too-many-arguments
        self.role = role
        self.button_id = button_id
        self.label = label
        self.html_el = self.get_html()
        self._fct = fct
        self._output = Output({'role': role + RESPONSE, 'id': MATCH}, 'children')
        callback_id = create_callback_id(self._output)
        if callback_id not in dash_app.callback_map:
            dash_app.callback(self._output, [Input({'role': role, 'id': MATCH}, 'id'),
                                             Input({'role': role, 'id': MATCH}, 'value')],
                              prevent_initial_call=prevent_initial_call)(self.call)

    def get_html(self):
        return dbc.Button(self.label, id={'role': self.role, 'id': self.button_id}, n_clicks=0, color="light",
                          className="col")

    def call(self, div_id, value):  # pylint: disable=unused-argument
        self._fct(div_id["id"])
        return " "
