import json
import traceback
from datetime import datetime, timezone
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, MATCH
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq

from MyLogger import logger
from flask import jsonify, request, Response as FlaskResponse

from MyPSACC import MyPSACC
from Trip import Trips
from web import figures

from web.app import app, dash_app, myp, chc
import web.db

RESPONSE = "-response"

EMPTY_DIV = "empty-div"

ABRP_SWITCH = 'abrp-switch'

ERROR_DIV = dbc.Alert("No data to show, there is probably no trips recorded yet", color="danger")
trips: Trips
chargings: dict
min_date = max_date = min_millis = max_millis = step = marks = cached_layout = None


@dash_app.callback(Output('trips_map', 'figure'),
                   Output('consumption_fig', 'figure'),
                   Output('consumption_fig_by_speed', 'figure'),
                   Output('consumption_graph_by_temp', 'children'),
                   Output('consumption', 'children'),
                   Output('tab_trips', 'children'),
                   Output('tab_battery', 'children'),
                   Output('tab_charge', 'children'),
                   Output('date-slider', 'max'),
                   Output('date-slider', 'step'),
                   Output('date-slider', 'marks'),
                   Input('date-slider', 'value'))
def display_value(value):
    mini = datetime.fromtimestamp(value[0], tz=timezone.utc)
    maxi = datetime.fromtimestamp(value[1], tz=timezone.utc)
    filtered_trips = Trips()
    for trip in trips:
        if mini <= trip.start_at <= maxi:
            filtered_trips.append(trip)
    filtered_chargings = MyPSACC.get_chargings(mini, maxi)
    figures.get_figures(filtered_trips, filtered_chargings)
    consumption = "Average consumption: {:.1f} kWh/100km".format(float(figures.consumption_df["consumption_km"].mean()))
    return figures.trips_map, figures.consumption_fig, figures.consumption_fig_by_speed, \
           figures.consumption_graph_by_temp, consumption, figures.table_fig, figures.battery_info, \
           figures.battery_table, max_millis, step, marks


@dash_app.callback(Output({'role': ABRP_SWITCH + RESPONSE, 'vin': MATCH}, 'children'),
                   Input({'role': ABRP_SWITCH, 'vin': MATCH}, 'id'),
                   Input({'role': ABRP_SWITCH, 'vin': MATCH}, 'value'))
def update_abrp(div_id, value):
    vin = div_id["vin"]
    if value:
        myp.abrp.abrp_enable_vin.add(vin)
    else:
        myp.abrp.abrp_enable_vin.discard(vin)
    myp.save_config()
    return " "


@app.route('/get_vehicles')
def get_vehicules():
    response = app.response_class(
        response=json.dumps(myp.get_vehicles(), default=lambda car: car.to_dict()),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/get_vehicleinfo/<string:vin>')
def get_vehicle_info(vin):
    response = app.response_class(
        response=json.dumps(myp.get_vehicle_info(vin).to_dict(), default=str),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/charge_now/<string:vin>/<int:charge>')
def charge_now(vin, charge):
    return jsonify(myp.charge_now(vin, charge != 0))


@app.route('/charge_hour')
def change_charge_hour():
    return jsonify(myp.change_charge_hour(request.form['vin'], request.form['hour'], request.form['minute']))


@app.route('/wakeup/<string:vin>')
def wakeup(vin):
    return jsonify(myp.wakeup(vin))


@app.route('/preconditioning/<string:vin>/<int:activate>')
def preconditioning(vin, activate):
    return jsonify(myp.preconditioning(vin, activate))


@app.route('/position/<string:vin>')
def get_position(vin):
    res = myp.get_vehicle_info(vin)
    try:
        coordinates = res.last_position.geometry.coordinates
    except AttributeError:
        return jsonify({'error': 'last_position not available from api'})
    longitude, latitude, altitude = coordinates[:2]
    if len(coordinates) == 3:  # altitude is not always available
        altitude = coordinates[2]
    else:
        altitude = None
    return jsonify(
        {"longitude": longitude, "latitude": latitude, "altitude": altitude,
         "url": f"https://maps.google.com/maps?q={latitude},{longitude}"})


# Set a battery threshold and schedule an hour to stop the charge
@app.route('/charge_control')
def charge_control():
    logger.info(request)
    vin = request.args['vin']
    charge_control = chc.get(vin)
    if charge_control is None:
        return jsonify("error: VIN not in list")
    if 'hour' in request.args and 'minute' in request.args:
        charge_control.set_stop_hour([int(request.args["hour"]), int(request.args["minute"])])
    if 'percentage' in request.args:
        charge_control.percentage_threshold = int(request.args['percentage'])
    chc.save_config()
    return jsonify(charge_control.get_dict())


@app.route('/positions')
def get_recorded_position():
    return FlaskResponse(myp.get_recorded_position(), mimetype='application/json')


@app.route('/abrp')
def abrp():
    vin = request.args.get('vin', None)
    enable = request.args.get('enable', None)
    token = request.args.get('token', None)
    if vin is not None and enable is not None:
        if enable == '1':
            myp.abrp.abrp_enable_vin.add(vin)
        else:
            myp.abrp.abrp_enable_vin.discard(vin)
    if token is not None:
        myp.abrp.token = token
    return jsonify(dict(myp.abrp))


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


def update_trips():
    global trips, chargings, cached_layout
    logger.info("update_data")
    try:
        trips_by_vin = Trips.get_trips(myp.vehicles_list)
        trips = next(iter(trips_by_vin.values()))  # todo handle multiple car
        chargings = MyPSACC.get_chargings()
    except StopIteration:
        logger.debug("No trips yet")
        return
    except AssertionError:
        logger.error("update_trips: %s", traceback.format_exc())
    # update for slider
    global min_date, max_date, min_millis, max_millis, step, marks
    try:
        min_date = trips[0].start_at
        max_date = trips[-1].start_at
        min_millis = figures.unix_time_millis(min_date)
        max_millis = figures.unix_time_millis(max_date)
        step = (max_millis - min_millis) / 100
        marks = figures.get_marks_from_start_end(min_date, max_date)
        cached_layout = None  # force regenerate layout
    except (ValueError, IndexError):
        logger.error("update_trips (slider): %s", traceback.format_exc())
    return


def __get_control_tabs():
    tabs = []
    for car in myp.vehicles_list:
        if car.label is None:
            label = car.vin
        else:
            label = car.label
        tabs.append(dbc.Tab(label=label, id="tab-" + car.vin, children=[
            daq.ToggleSwitch(
                id={'role': ABRP_SWITCH, 'vin': car.vin},
                value=car.vin in myp.abrp.abrp_enable_vin,
                label="Send data to ABRP"
            ),
            html.Div(id={'role': ABRP_SWITCH + RESPONSE, 'vin': car.vin})
        ]))
    return tabs


def serve_layout():
    global cached_layout
    if cached_layout is None:
        logger.debug("Create new layout")
        try:
            figures.get_figures(trips, chargings)
            data_div = html.Div([dcc.RangeSlider(
                id='date-slider',
                min=min_millis,
                max=max_millis,
                step=step,
                marks=marks,
                value=[min_millis, max_millis],
            ),
                html.Div([
                    dbc.Tabs([
                        dbc.Tab(label="Summary", tab_id="summary", children=[
                            html.H2(id="consumption",
                                    children=figures.info),
                            dcc.Graph(figure=figures.consumption_fig, id="consumption_fig"),
                            dcc.Graph(figure=figures.consumption_fig_by_speed, id="consumption_fig_by_speed"),
                            figures.consumption_graph_by_temp
                        ]),
                        dbc.Tab(label="Trips", tab_id="trips", id="tab_trips", children=[figures.table_fig]),
                        dbc.Tab(label="Battery", tab_id="battery", id="tab_battery", children=[figures.battery_info]),
                        dbc.Tab(label="Charge", tab_id="charge", id="tab_charge", children=[figures.battery_table]),
                        dbc.Tab(label="Map", tab_id="map", children=[
                            dcc.Graph(figure=figures.trips_map, id="trips_map", style={"height": '90vh'})]),
                        dbc.Tab(label="Control", tab_id="control", children=dbc.Tabs(id="control-tabs",
                                                                                     children=__get_control_tabs()))
                    ],
                        id="tabs",
                        active_tab="summary",
                    ),
                    html.Div(id=EMPTY_DIV),
                ])])
        except (IndexError, TypeError, NameError):
            logger.warning("Failed to generate figure, there is probably not enough data yet")
            logger.debug(traceback.format_exc())
            data_div = ERROR_DIV
        cached_layout = dbc.Container(fluid=True, children=[html.H1('My car info'), data_div])
    return cached_layout


try:
    web.db.callback_fct = update_trips
    update_trips()
except (IndexError, TypeError):
    logger.debug("Failed to get trips, there is probably not enough data yet %s", traceback.format_exc())

dash_app.layout = serve_layout
