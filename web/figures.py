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
from Trip import Trip
from pandas import options as pandas_options


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


consumption_fig = None
consumption_df = None
trips_map = None
consumption_fig_by_speed = None
table_fig = None
pandas_options.display.float_format = '${:.2f}'.format
info = ""
battery_info = dbc.Alert("No data to show", color="danger")


def get_figures(trips: List[Trip], charging: List[dict]):
    global consumption_fig, consumption_df, trips_map, consumption_fig_by_speed, table_fig, info, battery_info
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
                  'format': deepcopy(nb_format).symbol_suffix(" km/h")},
                 {'id': 'consumption_km', 'name': 'average consumption', 'type': 'numeric',
                  'format': deepcopy(nb_format).symbol_suffix(" kw/100km")},
                 {'id': 'distance', 'name': 'distance', 'type': 'numeric', 'format': nb_format.symbol_suffix(" km")}],
        data=[tr.get_info() for tr in trips],
    )
    # consumption_fig
    consumption_df = DataFrame.from_records([tr.get_consumption() for tr in trips])
    consumption_fig = px.line(consumption_df, x="date", y="consumption", title='Consumption of the car')
    consumption_fig.update_layout(yaxis_title="Consumption kWh/100Km")

    consum_df_by_speed = DataFrame.from_records(
        [{"speed": tr.speed_average, "consumption": tr.consumption_km} for tr in trips])
    consumption_fig_by_speed = px.histogram(consum_df_by_speed, x="speed", y="consumption", histfunc="avg",
                                            title="Consumption by speed")
    consumption_fig_by_speed.update_traces(xbins_size=15)
    consumption_fig_by_speed.update_layout(bargap=0.05)
    consumption_fig_by_speed.add_trace(
        go.Scatter(mode="markers", x=consum_df_by_speed["speed"], y=consum_df_by_speed["consumption"],
                   name="Trips"))
    consumption_fig_by_speed.update_layout(xaxis_title="average Speed km/h", yaxis_title="Consumption kWh/100Km")
    kw_per_km = float(consumption_df.mean(numeric_only=True))
    info = "Average consumption: {:.1f} kW/100km".format(kw_per_km)

    # charging
    charging_data = DataFrame.from_records(charging)
    try:
        co2_per_kw = charging_data["co2"].sum() / charging_data["kw"].sum()
    except ZeroDivisionError:
        co2_per_kw = 0
    co2_per_km = co2_per_kw * kw_per_km / 100
    try:
        charge_speed = 3600 * charging_data["kw"].mean() / \
                   (charging_data["stop_at"] - charging_data["start_at"]).mean().total_seconds()
    except TypeError: #when there is no data yet:
        charge_speed=0
    battery_info = "Average gC02/kW: {:.1f}\n" \
                   "Average gC02/km: {:1f}\n" \
                   "Average Charge SPEED {:1f} gC02/kW".format(co2_per_kw, co2_per_km, charge_speed)
