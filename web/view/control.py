import dash_bootstrap_components as dbc
from dash import html

from my_psacc import MyPSACC
from mylogger import logger
from web.tools.Button import Button
from web.tools.Switch import Switch
from web.utils import card_value_div, create_card

REFRESH_SWITCH = "refresh-switch"
ABRP_SWITCH = 'abrp-switch'
CHARGE_SWITCH = "charge-switch"
PRECONDITIONING_SWITCH = "preconditioning-switch"


def get_control_tabs(config):
    tabs = []
    for car in config.myp.vehicles_list:
        if car.label is None:
            label = car.vin
        else:
            label = car.label
        myp: MyPSACC = config.myp
        el = []
        buttons_row = []
        if config.remote_control:
            try:
                preconditionning_state = car.status.preconditionning.air_conditioning.status != "Disabled"
                charging_state = car.status.get_energy('Electric').charging.status == "InProgress"
                cards = {"Battery": {"text": [card_value_div("battery_value", "%",
                                                             value=str(int(car.status.get_energy('Electric').level)))],
                                     "src": "assets/images/battery-charge.svg"},
                         "Mileage": {"text": [card_value_div("mileage_value", "km",
                                                             value=str(int(car.status.timed_odometer.mileage)))],
                                     "src": "assets/images/mileage.svg"}
                         }
                el.append(dbc.Container(dbc.Row(children=create_card(cards)), fluid=True))
                buttons_row.extend([Button(REFRESH_SWITCH, car.vin,
                                           html.Img(src="assets/images/sync.svg", width="50px"),
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
