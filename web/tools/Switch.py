import dash_bootstrap_components as dbc
import dash_daq as daq
import dash_html_components as html

from web.tools.Button import Button, RESPONSE


class Switch(Button):
    def __init__(self, role, button_id, label, fct, value): # pylint: disable=too-many-arguments
        self.value = value
        super().__init__(role, button_id, label, fct)

    def get_html(self):
        return dbc.Col([daq.ToggleSwitch( # pylint: disable=not-callable
            id={'role': self.role, 'id': self.button_id},
            value=self.value,
            label=self.label
        ), html.Div(id={'role': self.role + RESPONSE, 'id': self.button_id})])

    def call(self, div_id, value):
        self._fct(div_id["id"], value)
        return " "