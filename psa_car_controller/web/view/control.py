import logging
from collections import OrderedDict

import dash_bootstrap_components as dbc
from dash import html

from psa_car_controller.psacc.application.psa_client import PSAClient
from psa_car_controller.psacc.repository.db import Database
from psa_car_controller.web.tools.Button import Button
from psa_car_controller.web.tools.Switch import Switch
from psa_car_controller.web.tools.utils import card_value_div, create_card

logger = logging.getLogger(__name__)

REFRESH_SWITCH = "refresh-switch"
ABRP_SWITCH = 'abrp-switch'
CHARGE_SWITCH = "charge-switch"
PRECONDITIONING_SWITCH = "preconditioning-switch"


def convert_value_to_str(value):
    try:
        return str(int(value))
    except TypeError:
        return "-"


def get_control_tabs(config):
    tabs = []
    for car in config.myp.vehicles_list:
        if car.label is None:
            label = car.vin
        else:
            label = car.label
        myp: PSAClient = config.myp
        el = []
        buttons_row = []
        if car.status is not None:
            cards = OrderedDict({"Battery SOC": {"text": [card_value_div("battery_value", "%",
                                                                         value=convert_value_to_str(
                                                                             car.status.get_energy('Electric').level))],
                                                 "src": "assets/images/battery-charge.svg"},
                                 "Mileage": {"text": [card_value_div("mileage_value", "km",
                                                                     value=convert_value_to_str(
                                                                         car.status.timed_odometer.mileage))],
                                             "src": "assets/images/mileage.svg"}
                                 })
            soh = Database.get_last_soh_by_vin(car.vin)
            if soh:
                cards["Battery SOH"] = {"text": [card_value_div("battery_soh_value", "%",
                                                                value=convert_value_to_str(
                                                                    soh))],
                                        "src": "assets/images/battery-soh.svg"}
                cards.move_to_end("Mileage")
            el.append(dbc.Container(dbc.Row(children=create_card(cards)), fluid=True))
            if config.remote_control:
                try:
                    preconditionning_state = car.status.preconditionning.air_conditioning.status != "Disabled"
                    charging_state = car.status.get_energy('Electric').charging.status == "InProgress"

                    refresh_date = car.status.get_energy('Electric').updated_at.astimezone().strftime("%X %x")
                    buttons_row.extend([Button(REFRESH_SWITCH, car.vin,
                                               html.Div([html.Img(src="assets/images/sync.svg", width="50px"),
                                                         refresh_date]),
                                               myp.remote_client.wakeup).get_html(),
                                        Switch(CHARGE_SWITCH, car.vin, "Charge", myp.remote_client.charge_now,
                                               charging_state).get_html(),
                                        Switch(PRECONDITIONING_SWITCH, car.vin, "Preconditioning",
                                               myp.remote_client.preconditioning, preconditionning_state).get_html()])
                except (AttributeError, TypeError):
                    logger.exception("get_control_tabs:")
        if not config.offline:
            buttons_row.append(Switch(ABRP_SWITCH, car.vin, "Send data to ABRP", myp.abrp.enable_abrp,
                                      car.vin in config.myp.abrp.abrp_enable_vin).get_html())
        tabs.append(dbc.Tab(label=label, id="tab-" + car.vin, children=[dbc.Row(buttons_row), *el]))
    return dbc.Tabs(id="control-tabs", children=tabs)
