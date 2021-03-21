from copy import deepcopy
from typing import List

import dash_bootstrap_components as dbc
import dash_table
import numpy as np
from dash_table.Format import Format, Scheme, Symbol
from dateutil.relativedelta import relativedelta
from pandas import DataFrame
import plotly.express as px
import plotly.graph_objects as go
from Trip import Trips
from pandas import options as pandas_options
import dash_html_components as html


def unix_time_millis(dt):
    return int(dt.timestamp())


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


consumption_fig = None
consumption_df = None
trips_map = None
consumption_fig_by_speed = None
table_fig = None
pandas_options.display.float_format = '${:.2f}'.format
info = ""
battery_info = dbc.Alert("No data to show", color="danger")
battery_table = None


def get_figures(trips: Trips, charging: List[dict]):
    global consumption_fig, consumption_df, trips_map, consumption_fig_by_speed, table_fig, info, battery_info, battery_table
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
    nb_format = Format(precision=2, scheme=Scheme.fixed, symbol=Symbol.yes)
    table_fig = dash_table.DataTable(
        id='trips-table',
        sort_action='native',
        sort_by=[{'column_id': 'start_at', 'direction': 'desc'}],
        columns=[{'id': 'start_at', 'name': 'start at', 'type': 'datetime'},
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
                  'format': nb_format.symbol_suffix(" km").precision(1)}],
        data=[tr.get_info() for tr in trips],
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
    try:
        co2_data = charging_data[charging_data["co2"] > 0]
        co2_per_kw = co2_data["co2"].sum() / co2_data["kw"].sum()
    except (ZeroDivisionError, KeyError):
        co2_per_kw = 0
    co2_per_km = co2_per_kw * kw_per_km / 100
    try:
        charge_speed = 3600 * charging_data["kw"].mean() / \
                       (charging_data["stop_at"] - charging_data["start_at"]).mean().total_seconds()
    except (TypeError, KeyError):  # when there is no data yet:
        charge_speed = 0

    battery_info = dash_table.DataTable(
        id='battery_info',
        sort_action='native',
        columns=[{'id': 'name', 'name': ''},
                 {'id': 'value', 'name': ''}],
        style_header={'display': 'none'},
        style_data={'border': '0px'},
        data=[{"name": "Average emission:", "value": "{:.1f} g/km".format(co2_per_km)},
              {"name": " ", "value:": "{:.1f} g/kWh".format(co2_per_kw)},
              {"name": "Average charge speed:", "value": "{:.3f} kW".format(charge_speed)}])
    battery_info = html.Div(children=[html.Tr(
            [
                html.Td('Average emission:', rowSpan=2),
                html.Td("{:.1f} g/km".format(co2_per_km)),
            ]
        ),
        html. Tr(
            [
                "{:.1f} g/kWh".format(co2_per_kw),
            ]
        ),
        html.Tr(
            [
                html.Td("Average charge speed:"),
                html.Td("{:.3f} kW".format(charge_speed))
            ]
        )
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
                  'format': deepcopy(nb_format).symbol_suffix(" kWh").precision(3)}],
        data=charging,
    )
