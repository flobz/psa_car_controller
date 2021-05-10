from copy import deepcopy
from statistics import mean

from typing import List

import dash_bootstrap_components as dbc
import dash_table
from dash_core_components import Graph
from dash_table.Format import Format, Scheme, Symbol
from dateutil.relativedelta import relativedelta
import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame
from pandas import options as pandas_options
import dash_html_components as html

from libs.car import Car
from libs.elec_price import ElecPrice
from trip import Trips, Trip
from web.db import Database


def unix_time_millis(date):
    return int(date.timestamp())


def get_marks_from_start_end(start, end):
    nb_marks = 10
    result = []
    time_delta = int((end - start).total_seconds() / nb_marks)
    current = start
    if time_delta > 0:
        while current <= end:
            result.append(current)
            current += relativedelta(seconds=time_delta)
        result[-1] = end
        if time_delta < 3600 * 24:
            if time_delta > 3600:
                date_f = '%x %Hh'
            else:
                date_f = '%x %Hh%M'
        else:
            date_f = '%x'
        marks = {}
        for date in result:
            marks[unix_time_millis(date)] = str(date.strftime(date_f))
        return marks
    return None


# pylint: disable=invalid-name
ERROR_DIV = dbc.Alert("No data to show, there is probably no trips recorded yet", color="danger")
PADDING_TOP = {"padding-top": "1em"}
consumption_fig = ERROR_DIV
consumption_df = ERROR_DIV
trips_map = ERROR_DIV
consumption_fig_by_speed = ERROR_DIV
consumption_fig_by_temp = ERROR_DIV
table_fig = ERROR_DIV
pandas_options.display.float_format = '${:.2f}'.format
info = ""
battery_info = ERROR_DIV
battery_table = None
consumption_df_dict = None

SUMMARY_CARDS = {"Average consumption": {"text": None, "src": "assets/images/consumption.svg"},
                 "Average emission": {"text": None, "src": "assets/images/pollution.svg"},
                 "Average charge speed": {"text": None, "src": "assets/images/battery-charge-line.svg"},
                 "Electricity consumption": {"text": None, "src": "assets/images/electricity bill.svg"}
                 }


# pylint: disable=too-many-locals
def get_figures(trips: Trips, charging: List[dict]):
    global consumption_fig, consumption_df, trips_map, consumption_fig_by_speed, table_fig, info, battery_info, \
        battery_table, consumption_fig_by_temp, consumption_df_dict
    lats = [42, 41]
    lons = [1, 2]
    names = ["undefined", "undefined"]
    trips_map = px.line_mapbox(lat=lats, lon=lons, hover_name=names, zoom=12, mapbox_style="assets/style2.json")
    trips_map.add_trace(go.Scattermapbox(
        mode="markers",
        marker={"symbol": "marker", "size": 20},
        lon=[lons[0]], lat=[lats[0]],
        showlegend=False, name="Last Position"))
    # table
    nb_format = Format(precision=2, scheme=Scheme.fixed, symbol=Symbol.yes)  # pylint: disable=no-member
    table_fig = dash_table.DataTable(
        id='trips-table',
        sort_action='native',
        sort_by=[{'column_id': 'id', 'direction': 'desc'}],
        columns=[{'id': 'id', 'name': '#', 'type': 'numeric'},
                 {'id': 'start_at', 'name': 'start at', 'type': 'datetime'},
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
        data=trips.get_info(),
        page_size=50
    )
    # consumption_fig
    consumption_df_dict = trips.get_long_trips()
    consumption_fig = px.histogram(x=[0], y=[1], title='Consumption of the car',
                                   histfunc="avg")
    consumption_fig.update_layout(yaxis_title="Consumption kWh/100Km")

    consumption_fig_by_speed = px.histogram(x=[0], y=[1], histfunc="avg",
                                            title="Consumption by speed")
    consumption_fig_by_speed.update_traces(xbins_size=15)
    consumption_fig_by_speed.update_layout(bargap=0.05)
    consumption_fig_by_speed.add_trace(go.Scatter(mode="markers", x=[0],
                                                  y=[0], name="Trips"))
    consumption_fig_by_speed.update_layout(xaxis_title="average Speed km/h", yaxis_title="Consumption kWh/100Km")
    kw_per_km = mean([t.consumption_km for t in trips])
    info = "Average consumption: {:.1f} kWh/100km".format(kw_per_km)

    # charging
    charging_data = DataFrame.from_records(charging)
    co2_per_kw = __calculate_co2_per_kw(charging_data)
    co2_per_km = co2_per_kw * kw_per_km / 100
    try:
        charge_speed = 3600 * charging_data["kw"].mean() / \
                       (charging_data["stop_at"] - charging_data["start_at"]).mean().total_seconds()
        price_kw = (charging_data["price"] / charging_data["kw"]).mean()
        total_elec = kw_per_km * trips.get_distance() / 100
    except (TypeError, KeyError, ZeroDivisionError):  # when there is no data yet:
        charge_speed = 0
        price_kw = 0
        total_elec = 0

    SUMMARY_CARDS["Average charge speed"]["text"] = f"{charge_speed:.2f} kW"
    SUMMARY_CARDS["Average emission"]["text"] = [html.P(f"{co2_per_km:.1f} g/km"), html.P(f"{co2_per_kw:.1f} g/kWh")]
    SUMMARY_CARDS["Electricity consumption"]["text"] = [f"{total_elec:.0f} kWh", html.Br(), \
                                                        f"{total_elec * price_kw:.0f} {ElecPrice.currency}"]
    SUMMARY_CARDS["Average consumption"]["text"] = f"{kw_per_km:.1f} kWh/100km"
    battery_table = dash_table.DataTable(
        id='battery-table',
        sort_action='native',
        sort_by=[{'column_id': 'start_at', 'direction': 'desc'}],
        columns=[{'id': 'start_at', 'name': 'start at', 'type': 'datetime'},
                 {'id': 'stop_at', 'name': 'stop at', 'type': 'datetime'},
                 {'id': 'start_level', 'name': 'start level', 'type': 'numeric'},
                 {'id': 'end_level', 'name': 'end level', 'type': 'numeric'},
                 {'id': 'co2', 'name': 'CO2', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" g/kWh").precision(1)},
                 {'id': 'kw', 'name': 'consumption', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" kWh").precision(2)},
                 {'id': 'price', 'name': 'price', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" " + ElecPrice.currency).precision(2), 'editable': True}
                 ],
        data=charging,
        style_data_conditional=[
            {
                'if': {'column_id': ['start_level', "end_level"]},
                'color': 'dodgerblue',
                "text-decoration": "underline"
            },
            {
                'if': {'column_id': 'price'},
                'backgroundColor': 'rgb(230, 246, 254)'
            }
        ],
    )
    consumption_fig_by_temp = None
    temp_value = False
    for trip in trips:
        if trip.get_temperature() is not None:
            temp_value = True
            break
    if temp_value:
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


def __calculate_co2_per_kw(charging_data):
    try:
        co2_data = charging_data[charging_data["co2"] > 0]
        co2_kw_sum = co2_data["kw"].sum()
        if co2_kw_sum > 0:
            return co2_data["co2"].sum() / co2_kw_sum
    except KeyError:
        return 0
    return 0


def get_battery_curve_fig(row: dict, car: Car):
    start_date = Database.convert_datetime_from_string(row["start_at"])
    stop_at = Database.convert_datetime_from_string(row["stop_at"])
    conn = Database.get_db()
    res = Database.get_battery_curve(conn, start_date, car.vin)
    conn.close()
    res.insert(0, {"level": row["start_level"], "date": start_date})
    res.append({"level": row["end_level"], "date": stop_at})
    battery_curves = []
    speed = 0
    for x in range(1, len(res)):
        start_level = res[x - 1]["level"]
        end_level = res[x]["level"]
        speed = car.get_charge_speed(start_level, end_level, (res[x]["date"] - res[x - 1]["date"]).total_seconds())
        battery_curves.append({"level": start_level, "speed": speed})
    battery_curves.append({"level": row["end_level"], "speed": speed})
    fig = px.line(battery_curves, x="level", y="speed")
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
    fig.update_layout(xaxis_title="Distance km", yaxis_title="Altitude m")
    conn.close()
    return html.Div(Graph(figure=fig))
