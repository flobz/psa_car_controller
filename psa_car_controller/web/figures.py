from copy import deepcopy

import dash_bootstrap_components as dbc
from dash import html
from dash.dash_table import DataTable
import plotly.express as px
import plotly.graph_objects as go
from dash.dash_table.Format import Scheme, Symbol, Group, Format
from dash.dcc import Graph

from psa_car_controller.psacc.application.charging import Charging
from psa_car_controller.psacc.model.car import Car
from psa_car_controller.psacc.repository.trips import Trip
from psa_car_controller.psacc.repository.db import Database

# pylint: disable=invalid-name
from psa_car_controller.web.tools.utils import card_value_div, dash_date_to_datetime

ERROR_DIV = dbc.Alert("No data to show, there is probably no trips recorded yet", color="danger")
PADDING_TOP = {"padding-top": "1em"}
consumption_fig = ERROR_DIV
consumption_df = ERROR_DIV
trips_map = ERROR_DIV
consumption_fig_by_speed = ERROR_DIV
consumption_fig_by_temp = ERROR_DIV
table_fig = ERROR_DIV
info = ""
battery_table = ERROR_DIV

AVG_CHARGE_SPEED = "avg_chg_speed"
AVG_EMISSION_KM = "avg_emission_km"
AVG_EMISSION_KW = "avg_emission_kw"
ELEC_CONSUM_KW = "elec_consum_kw"
ELEC_CONSUM_PRICE = "elec_consum_price"
AVG_CONSUM_KW = "avg_consum_kw"
AVG_CONSUM_PRICE = "avg_consum_price"
CURRENCY = "€"
EXPORT_FORMAT = "csv"
USE_IMPERIAL = False  # view-layer flag: True = imperial (mi/mph), False = metric (km/km/h)

# Conversion factors (metric → imperial)
_KM_TO_MI = 0.621371
_KMH_TO_MPH = 0.621371
_KWH_PER_100KM_TO_KWH_PER_100MI = 1 / _KM_TO_MI  # consuming more kWh over fewer miles


def _dist_unit() -> str:
    return "mi" if USE_IMPERIAL else "km"


def _speed_unit() -> str:
    return "mph" if USE_IMPERIAL else "km/h"


def _consumption_unit() -> str:
    """Electric consumption per distance unit."""
    return f"kWh/100{_dist_unit()}"


def _fuel_consumption_unit() -> str:
    return f"L/100{_dist_unit()}"


def _dist_suffix() -> str:
    return f" {_dist_unit()}"


def _speed_suffix() -> str:
    return f" {_speed_unit()}"


def convert_trips_for_display(trips_dict: list) -> list:
    """
    Return a copy of the trips-as-dict list with distance, mileage,
    speed_average, consumption_km, and consumption_fuel_km converted to
    imperial values when USE_IMPERIAL is True. View-layer only.
    """
    if not USE_IMPERIAL:
        return trips_dict
    result = []
    for trip in trips_dict:
        t = dict(trip)
        if t.get("distance") is not None:
            t["distance"] = t["distance"] * _KM_TO_MI
        if t.get("mileage") is not None:
            t["mileage"] = t["mileage"] * _KM_TO_MI
        if t.get("speed_average") is not None:
            t["speed_average"] = t["speed_average"] * _KMH_TO_MPH
        if t.get("consumption_km") is not None:
            t["consumption_km"] = t["consumption_km"] * _KWH_PER_100KM_TO_KWH_PER_100MI
        if t.get("consumption_fuel_km") is not None:
            t["consumption_fuel_km"] = t["consumption_fuel_km"] * _KWH_PER_100KM_TO_KWH_PER_100MI
        result.append(t)
    return result


def convert_chargings_for_display(chargings_dict: list) -> list:
    """
    Return a copy of the chargings list with the mileage field converted
    to imperial when USE_IMPERIAL is True. View-layer only.
    """
    if not USE_IMPERIAL:
        return chargings_dict
    result = []
    for charge in chargings_dict:
        c = dict(charge)
        if c.get("mileage") is not None:
            c["mileage"] = c["mileage"] * _KM_TO_MI
        result.append(c)
    return result


def get_summary_cards():
    dist = _dist_unit()
    return {"Average consumption": {"text": [card_value_div(AVG_CONSUM_KW, f"kWh/100{dist}"),
                                             card_value_div(AVG_CONSUM_PRICE, f"{CURRENCY}/100{dist}")],
                                    "src": "assets/images/consumption.svg"},
            "Average emission": {"text": [card_value_div(AVG_EMISSION_KM, " g/km"),
                                          card_value_div(AVG_EMISSION_KW, "g/kWh")],
                                 "src": "assets/images/pollution.svg"},
            "Average charge speed": {"text": [card_value_div(AVG_CHARGE_SPEED, " kW")],
                                     "src": "assets/images/battery-charge-line.svg"},
            "Electricity consumption": {"text": [card_value_div(ELEC_CONSUM_KW, "kWh"),
                                                 card_value_div(ELEC_CONSUM_PRICE, CURRENCY)],
                                        "src": "assets/images/electricity bill.svg"}
            }


def get_figures(car: Car):
    global consumption_fig, trips_map, consumption_fig_by_speed, table_fig, battery_table, consumption_fig_by_temp
    lats = [42, 41]
    lons = [1, 2]
    names = ["undefined", "undefined"]
    trips_map = px.line_mapbox(lat=lats, lon=lons, hover_name=names, zoom=12, mapbox_style="style.json")
    trips_map.add_trace(go.Scattermapbox(
        mode="markers",
        marker={"symbol": "marker", "size": 20},
        lon=[lons[0]], lat=[lats[0]],
        showlegend=False, name="Last Position"))
    # table
    nb_format = Format(precision=2, scheme=Scheme.fixed, symbol=Symbol.yes, group=Group.yes)
    dist = _dist_unit()
    speed = _speed_unit()
    style_cell_conditional = []
    if car.is_electric():
        style_cell_conditional.append({'if': {'column_id': 'consumption_fuel_km', }, 'display': 'None', })
    if car.is_thermal():
        style_cell_conditional.append({'if': {'column_id': 'consumption_km', }, 'display': 'None', })
    table_fig = DataTable(
        id='trips-table',
        export_format=EXPORT_FORMAT,
        sort_action='custom',
        sort_by=[{'column_id': 'id', 'direction': 'desc'}],
        style_data={
            'width': '10%',
            'maxWidth': '10%',
            'minWidth': '10%',
            'color': 'gray'
        },
        columns=[{'id': 'id', 'name': '#', 'type': 'numeric'},
                 {'id': 'start_at_str', 'name': 'start at', 'type': 'datetime'},
                 {'id': 'duration', 'name': 'duration', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" min").precision(0)},
                 {'id': 'speed_average', 'name': 'avg. speed', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(f" {speed}").precision(0)},
                 {'id': 'consumption_km', 'name': 'avg. consumption', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(f" kWh/100{dist}")},
                 {'id': 'consumption_fuel_km', 'name': 'average consumption fuel', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(f" L/100{dist}")},
                 {'id': 'distance', 'name': 'distance', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(f" {dist}").precision(1)},
                 {'id': 'mileage', 'name': f'mileage ({dist})', 'type': 'numeric',
                  'format': Format(precision=1, scheme=Scheme.fixed, symbol=Symbol.no, group=Group.yes)},
                 {'id': 'altitude_diff', 'name': 'altitude diff', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" m").precision(0)}
                 ],
        style_data_conditional=[
            {
                'if': {'column_id': ['id']},
                'width': '5%'
            },
            {
                'if': {'column_id': ['altitude_diff']},
                'color': 'black'
            }
        ],
        style_cell_conditional=style_cell_conditional,
        data=[],
        page_size=50
    )
    # consumption_fig
    consumption_fig = px.histogram(x=[0], y=[1], title='Consumption of the car',
                                   histfunc="avg")
    consumption_fig.update_layout(yaxis_title=f"Consumption kWh/100{dist}", xaxis_title="date")
    consumption_fig.update_xaxes(type="date", tickformat="%d/%m/%Y")

    consumption_fig_by_speed = px.histogram(data_frame=[{"start_at": 1, "speed_average": 2}], x="start_at",
                                            y="speed_average", histfunc="avg",
                                            title="Consumption by speed")
    consumption_fig_by_speed.update_traces(xbins_size=15)
    consumption_fig_by_speed.update_layout(bargap=0.05)
    consumption_fig_by_speed.add_trace(go.Scatter(mode="markers", x=[0],
                                                  y=[0], name="Trips"))
    consumption_fig_by_speed.update_layout(xaxis_title=f"average Speed {speed}",
                                           yaxis_title=f"Consumption kWh/100{dist}")
    # battery_table
    battery_table = DataTable(
        id='battery-table',
        export_format=EXPORT_FORMAT,
        sort_action='custom',
        style_data={
            'width': '10%',
            'maxWidth': '10%',
            'minWidth': '10%',
            'color': 'gray'
        },
        sort_by=[{'column_id': 'start_at_str', 'direction': 'desc'}],
        columns=[{'id': 'start_at_str', 'name': 'start at', 'type': 'datetime'},
                 {'id': 'stop_at_str', 'name': 'stop at', 'type': 'datetime'},
                 {'id': 'duration_str', 'name': 'duration', 'type': 'text'},
                 {'id': 'duration_min', 'name': 'duration (min)', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" min").precision(0)},
                 {'id': 'start_level', 'name': 'start level', 'type': 'numeric'},
                 {'id': 'end_level', 'name': 'end level', 'type': 'numeric'},
                 {'id': 'co2', 'name': 'CO2', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" g/kWh").precision(1)},
                 {'id': 'kw', 'name': 'consumption', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" kWh").precision(2)},
                 {'id': 'price', 'name': 'price', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" " + CURRENCY).precision(2), 'editable': True},
                 {'id': 'charging_mode', 'name': 'charging mode', 'type': 'text'},
                 {'id': 'mileage', 'name': f'mileage ({dist})', 'type': 'numeric',
                  'format': Format(precision=1, scheme=Scheme.fixed, symbol=Symbol.no, group=Group.yes)},
                 ],
        data=[],
        page_size=50,
        style_data_conditional=[
            {
                'if': {'column_id': ['start_level', "end_level"]},
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{start_level} < 15',
                    'column_id': 'start_level'
                },
                'color': 'red'
            },
            {
                'if': {
                    'filter_query': '{end_level} > 85',
                    'column_id': 'end_level'
                },
                'color': 'green'
            },
            {
                'if': {
                    'filter_query': '{charging_mode} = "Quick"'
                },
                'backgroundColor': 'ivory'
            },
            {
                'if': {'column_id': 'price'},
                'color': 'dodgerblue',
                'font-weihgt': 'bold'
            }
        ],
    )
    consumption_fig_by_temp = px.histogram(x=[0], y=[0],
                                           histfunc="avg", title="Consumption by temperature")
    consumption_fig_by_temp.update_traces(xbins_size=2)
    consumption_fig_by_temp.update_layout(bargap=0.05)
    consumption_fig_by_temp.add_trace(
        go.Scatter(mode="markers", x=[0],
                   y=[0], name="Trips"))
    consumption_fig_by_temp.update_layout(xaxis_title="average temperature in °C",
                                          yaxis_title=f"Consumption kWh/100{dist}")
    return True


def get_battery_curve_fig(row: dict, car: Car):
    start_date = dash_date_to_datetime(row["start_at"])
    conn = Database.get_db()
    charge = Database.get_charge(car.vin, start_date)
    battery_curves = Charging.get_battery_curve(conn, charge, car)
    battery_curves_dict = list(map(lambda bc: bc.__dict__, battery_curves))
    fig = px.line(battery_curves_dict, x="level", y="speed")
    fig.update_layout(xaxis_title="Battery %", yaxis_title="Charging speed in kW")
    return html.Div(Graph(figure=fig))


def get_altitude_fig(trip: Trip):
    conn = Database.get_db()
    res = list(map(list, conn.execute("SELECT mileage, altitude FROM position WHERE Timestamp>=? and Timestamp<=?;",
                                      (trip.start_at, trip.end_at)).fetchall()))
    start_mileage = res[0][0]
    for line in res:
        line[0] = line[0] - start_mileage
    fig = px.line(res, x=0, y=1)
    dist = _dist_unit()
    fig.update_layout(xaxis_title=f"Distance {dist}", yaxis_title="Altitude m")
    return html.Div(Graph(figure=fig))
