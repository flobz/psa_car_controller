from copy import deepcopy
from datetime import datetime

from typing import List

import pytz
import dash_bootstrap_components as dbc
import dash_table
import numpy as np
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
consumption_graph_by_temp = ERROR_DIV
table_fig = ERROR_DIV
pandas_options.display.float_format = '${:.2f}'.format
info = ""
battery_info = ERROR_DIV
battery_table = None


# pylint: disable=too-many-locals
def get_figures(trips: Trips, charging: List[dict]):
    global consumption_fig, consumption_df, trips_map, consumption_fig_by_speed, table_fig, info, battery_info, \
        battery_table, consumption_graph_by_temp
    lats = []
    lons = []
    names = []
    for trip in trips:
        for points in trip.positions:
            lats = np.append(lats, points.longitude)
            lons = np.append(lons, points.latitude)
            names = np.append(names, [str(trip.start_at)])
        lats = np.append(lats, None)
        lons = np.append(lons, None)
        names = np.append(names, None)
    trips_map = px.line_mapbox(lat=lats, lon=lons, hover_name=names,
                               mapbox_style="stamen-terrain", zoom=12)
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
    consumption_df = DataFrame.from_records(trips.get_long_trips())
    consumption_fig = px.line(consumption_df, x="date", y="consumption", title='Consumption of the car')
    consumption_fig.update_layout(yaxis_title="Consumption kWh/100Km")

    consumption_fig_by_speed = px.histogram(consumption_df, x="speed", y="consumption_km", histfunc="avg",
                                            title="Consumption by speed")
    consumption_fig_by_speed.update_traces(xbins_size=15)
    consumption_fig_by_speed.update_layout(bargap=0.05)
    consumption_fig_by_speed.add_trace(
        go.Scatter(mode="markers", x=consumption_df["speed"], y=consumption_df["consumption_km"],
                   name="Trips"))
    consumption_fig_by_speed.update_layout(xaxis_title="average Speed km/h", yaxis_title="Consumption kWh/100Km")
    kw_per_km = float(consumption_df["consumption_km"].mean())
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

    battery_info = html.Div(children=[
        html.Tr(
            [
                html.Td('Average emission:', rowSpan=2),
                html.Td("{:.1f} g/km".format(co2_per_km))]),
        html.Tr(
            [
                "{:.1f} g/kWh".format(co2_per_kw),
            ]
        ),
        html.Tr([
            html.Td("Average charge speed:", style=PADDING_TOP),
            html.Td("{:.3f} kW".format(charge_speed))
        ]),
        html.Tr(html.Td(" ", colSpan=2)),
        html.Tr([
            html.Td('Average Price:', rowSpan=2, style=PADDING_TOP),
            html.Td("{:.2f} {}/100km".format(price_kw * kw_per_km, ElecPrice.currency)),
        ]),
        html.Tr([
            "{:.2f} {}/kWh".format(price_kw, ElecPrice.currency),
        ]),
        html.Tr(html.Td(" ", colSpan=2)),
        html.Tr([
            html.Td('Electricity consumption:', rowSpan=2, style=PADDING_TOP),
            html.Td("{:.0f} kWh".format(total_elec)),
        ]),
        html.Tr([
            "{:.0f} {}".format(total_elec * price_kw, ElecPrice.currency),
        ]),
    ])

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
    consumption_by_temp_df = consumption_df[consumption_df["consumption_by_temp"].notnull()]
    if len(consumption_by_temp_df) > 0:
        consumption_fig_by_temp = px.histogram(consumption_by_temp_df, x="consumption_by_temp", y="consumption_km",
                                               histfunc="avg", title="Consumption by temperature")
        consumption_fig_by_temp.update_traces(xbins_size=2)
        consumption_fig_by_temp.update_layout(bargap=0.05)
        consumption_fig_by_temp.add_trace(
            go.Scatter(mode="markers", x=consumption_by_temp_df["consumption_by_temp"],
                       y=consumption_by_temp_df["consumption_km"], name="Trips"))
        consumption_fig_by_temp.update_layout(xaxis_title="average temperature in °C",
                                              yaxis_title="Consumption kWh/100Km")
        consumption_graph_by_temp = html.Div(Graph(figure=consumption_fig_by_temp), id="consumption_graph_by_temp")

    else:
        consumption_graph_by_temp = html.Div(Graph(style={'display': 'none'}), id="consumption_graph_by_temp")
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


def dash_date_to_datetime(dash_date):
    return datetime.strptime(dash_date, "%Y-%m-%dT%H:%M:%S+00:00").replace(tzinfo=pytz.UTC)


def get_battery_curve_fig(row: dict, car: Car):
    start_date = dash_date_to_datetime(row["start_at"])
    stop_at = dash_date_to_datetime(row["stop_at"])
    res = Database.get_battery_curve(Database.get_db(), start_date, car.vin)
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
    return html.Div(Graph(figure=fig))
