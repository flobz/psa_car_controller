from copy import deepcopy
from statistics import mean

import dash_bootstrap_components as dbc
import dash_table
from dash_table.Format import Format, Scheme, Symbol
import plotly.express as px
import plotly.graph_objects as go
from web.tools.import_dash_html import html
from web.tools.import_dash_core import dcc

from libs.car import Car
from libs.elec_price import ElecPrice
from trip import Trip
from web.db import Database
from web.utils import card_value_div, dash_date_to_datetime

# pylint: disable=invalid-name
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

SUMMARY_CARDS = {"Average consumption": {"text": [card_value_div(AVG_CONSUM_KW, "kWh/100km"),
                                                  card_value_div(AVG_CONSUM_PRICE, f"{ElecPrice.currency}/100km")],
                                         "src": "assets/images/consumption.svg"},
                 "Average emission": {"text": [card_value_div(AVG_EMISSION_KM, " g/km"),
                                               card_value_div(AVG_EMISSION_KW, "g/kWh")],
                                      "src": "assets/images/pollution.svg"},
                 "Average charge speed": {"text": [card_value_div(AVG_CHARGE_SPEED, " kW")],
                                          "src": "assets/images/battery-charge-line.svg"},
                 "Electricity consumption": {"text": [card_value_div(ELEC_CONSUM_KW, "kWh"),
                                                      card_value_div(ELEC_CONSUM_PRICE, ElecPrice.currency)],
                                             "src": "assets/images/electricity bill.svg"}
                 }


# pylint: disable=too-many-locals
def get_figures(car: Car):
    global consumption_fig, consumption_df, trips_map, consumption_fig_by_speed, table_fig, info, \
        battery_table, consumption_fig_by_temp
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
    nb_format = Format(precision=2, scheme=Scheme.fixed, symbol=Symbol.yes)  # pylint: disable=no-member
    style_cell_conditional = []
    if car.is_electric():
        style_cell_conditional.append({'if': {'column_id': 'consumption_fuel_km', }, 'display': 'None', })
    if car.is_thermal():
        style_cell_conditional.append({'if': {'column_id': 'consumption_km', }, 'display': 'None', })
    table_fig = dash_table.DataTable(
        id='trips-table',
        sort_action='custom',
        sort_by=[{'column_id': 'id', 'direction': 'desc'}],
        columns=[{'id': 'id', 'name': '#', 'type': 'numeric'},
                 {'id': 'start_at_str', 'name': 'start at', 'type': 'datetime'},
                 {'id': 'duration', 'name': 'duration', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" min").precision(0)},
                 {'id': 'speed_average', 'name': 'average speed', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" km/h").precision(0)},
                 {'id': 'consumption_km', 'name': 'average consumption', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" kWh/100km")},
                 {'id': 'consumption_fuel_km', 'name': 'average consumption fuel', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" L/100km")},
                 {'id': 'distance', 'name': 'distance', 'type': 'numeric',
                  'format': nb_format.symbol_suffix(" km").precision(1)},
                 {'id': 'mileage', 'name': 'mileage', 'type': 'numeric',
                  'format': nb_format},
                 {'id': 'altitude_diff', 'name': 'Altitude diff', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" m").precision(0)}
                 ],
        style_data_conditional=[
            {
                'if': {'column_id': ['altitude_diff']},
                'color': 'dodgerblue',
                "text-decoration": "underline"
            }
        ],
        style_cell_conditional=style_cell_conditional,
        data=[],
        page_size=50
    )
    # consumption_fig
    consumption_fig = px.histogram(x=[0], y=[1], title='Consumption of the car',
                                   histfunc="avg")
    consumption_fig.update_layout(yaxis_title="Consumption kWh/100Km", xaxis_title="date")

    consumption_fig_by_speed = px.histogram(data_frame=[{"start_at": 1, "speed_average": 2}], x="start_at",
                                            y="speed_average", histfunc="avg",
                                            title="Consumption by speed")
    consumption_fig_by_speed.update_traces(xbins_size=15)
    consumption_fig_by_speed.update_layout(bargap=0.05)
    consumption_fig_by_speed.add_trace(go.Scatter(mode="markers", x=[0],
                                                  y=[0], name="Trips"))
    consumption_fig_by_speed.update_layout(xaxis_title="average Speed km/h", yaxis_title="Consumption kWh/100Km")

    # battery_table
    battery_table = dash_table.DataTable(
        id='battery-table',
        sort_action='custom',
        sort_by=[{'column_id': 'start_at_str', 'direction': 'desc'}],
        columns=[{'id': 'start_at_str', 'name': 'start at', 'type': 'datetime'},
                 {'id': 'stop_at_str', 'name': 'stop at', 'type': 'datetime'},
                 {'id': 'start_level', 'name': 'start level', 'type': 'numeric'},
                 {'id': 'end_level', 'name': 'end level', 'type': 'numeric'},
                 {'id': 'co2', 'name': 'CO2', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" g/kWh").precision(1)},
                 {'id': 'kw', 'name': 'consumption', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" kWh").precision(2)},
                 {'id': 'price', 'name': 'price', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" " + ElecPrice.currency).precision(2), 'editable': True}
                 ],
        data=[],
        style_data_conditional=[
            {
                'if': {'column_id': ['start_level', "end_level"]},
                'color': 'dodgerblue',
                "text-decoration": "underline"
            },
            {
                'if': {'column_id': 'price'},
                'backgroundColor': '#ABE2FB'
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
                                          yaxis_title="Consumption kWh/100Km")
    return True


def get_battery_curve_fig(row: dict, car: Car):
    start_date = dash_date_to_datetime(row["start_at"])
    stop_at = dash_date_to_datetime(row["stop_at"])
    conn = Database.get_db()
    res = Database.get_battery_curve(conn, start_date, stop_at, car.vin)
    conn.close()
    battery_curves = []
    if len(res) > 0:
        battery_capacity = res[-1]["level"] * car.battery_power / 100
        km_by_kw = 0.8 * res[-1]["autonomy"] / battery_capacity
        start = 0
        speeds = []

        def speed_in_kw_from_km(row):
            try:
                speed = row["rate"] / km_by_kw
                if speed > 0:
                    speeds.append(speed)
            except (KeyError, TypeError):
                pass

        for end in range(1, len(res)):
            start_level = res[start]["level"]
            end_level = res[end]["level"]
            diff_level = end_level - start_level
            diff_sec = (res[end]["date"] - res[start]["date"]).total_seconds()
            speed_in_kw_from_km(res[end - 1])
            if diff_sec > 0 and diff_level > 3:
                speed_in_kw_from_km(res[end])
                speed = car.get_charge_speed(diff_level, diff_sec)
                if len(speeds) > 0:
                    speed = mean([*speeds, speed])
                speed = round(speed * 2) / 2
                battery_curves.append({"level": start_level, "speed": speed})
                start = end
                speeds = []
        battery_curves.append({"level": row["end_level"], "speed": 0})
    else:
        speed = car.get_charge_speed(row["end_level"]-row["start_level"], (stop_at-start_date).total_seconds())
        battery_curves.append({"level": row["start_level"], "speed": speed})
        battery_curves.append({"level": row["end_level"], "speed": speed})
    fig = px.line(battery_curves, x="level", y="speed")
    fig.update_layout(xaxis_title="Battery %", yaxis_title="Charging speed in kW")
    return html.Div(dcc.Graph(figure=fig))


def get_altitude_fig(trip: Trip):
    conn = Database.get_db()
    res = list(map(list, conn.execute("SELECT mileage, altitude FROM position WHERE Timestamp>=? and Timestamp<=?;",
                                      (trip.start_at, trip.end_at)).fetchall()))
    start_mileage = res[0][0]
    for line in res:
        line[0] = line[0] - start_mileage
    fig = px.line(res, x=0, y=1)
    fig.update_layout(xaxis_title="Distance km", yaxis_title="Altitude m")
    conn.close()
    return html.Div(dcc.Graph(figure=fig))
