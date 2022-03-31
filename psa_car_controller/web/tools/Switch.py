import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html
from dash.dependencies import Input

from psa_car_controller.web.app import dash_app
from psa_car_controller.web.tools.Button import Button


class Switch(Button):
    def __init__(self, role, element_id, label, fct, value, prevent_initial_call=True):
        # pylint: disable=too-many-arguments
        self.value = value
        super().__init__(role, element_id, label, fct, prevent_initial_call)

    def _set_callback(self, prevent_initial_call):
        dash_app.callback(self._output, Input(self.get_button_id(), 'value'),
                          prevent_initial_call=prevent_initial_call)(self.call)

    def get_html(self):
        return dbc.Col([daq.ToggleSwitch(  # pylint: disable=not-callable
            id=self.get_button_id(),
            value=self.value,
            label=self.label
        ), html.Div(id=self.get_response_id())])

    def call(self, value):
        self._fct(self._element_id, value)
        return " "
