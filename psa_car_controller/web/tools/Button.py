import dash_bootstrap_components as dbc
from dash import html
from dash._utils import create_callback_id
from dash.dependencies import Output, Input

from psa_car_controller.web.app import dash_app

RESPONSE = "-response"


class Button:
    def __init__(self, role, element_id, label, fct, prevent_initial_call=True):  # pylint: disable=too-many-arguments
        self.role = role
        self._element_id = element_id
        self._button_id = "{}-{}".format(self.role, element_id)
        self._response_id = "{}{}".format(self._button_id, RESPONSE)
        self.label = label
        self.html_el = self.get_html()
        self._fct = fct
        self._output = Output(self.get_response_id(), 'children')
        callback_id = create_callback_id(self._output)
        if callback_id not in dash_app.callback_map:
            self._set_callback(prevent_initial_call)

    def _set_callback(self, prevent_initial_call):
        dash_app.callback(self._output, Input(self.get_button_id(), 'n_clicks'),
                          prevent_initial_call=prevent_initial_call)(self.call)

    def get_button_id(self):
        return self._button_id

    def get_response_id(self):
        return self._response_id

    def get_html(self):
        return dbc.Col([dbc.Button(self.label, id=self.get_button_id(), n_clicks=0, color="light",
                                   className="w-100"),
                        html.Div(id=self.get_response_id())])

    def call(self, value):  # pylint: disable=unused-argument
        self._fct(self._element_id)
        return " "
