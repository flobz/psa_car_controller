import json
import traceback
from datetime import datetime, timezone
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html

from MyLogger import logger
from flask import jsonify, request, Response as FlaskResponse

from MyPSACC import MyPSACC
from web import figures

from web.app import app, dash_app, myp, chc
import web.db

trips = None
chargings = None


@dash_app.callback(Output('trips_map', 'figure'),
                   Output('consumption_fig', 'figure'),
                   Output('consumption_fig_by_speed', 'figure'),
                   Output('consumption', 'children'),
                   Output('tab_trips', 'children'),
                   Output('tab_battery', 'children'),
                   Input('date-slider', 'value'))
def display_value(value):
    min = datetime.fromtimestamp(value[0], tz=timezone.utc)
    max = datetime.fromtimestamp(value[1], tz=timezone.utc)
    filtered_trips = []
    for trip in trips:
        if min <= trip.start_at <= max:
            filtered_trips.append(trip)
    filtered_chargings = MyPSACC.get_chargings(min,max)
    figures.get_figures(filtered_trips,filtered_chargings)
    consumption = "Average consumption: {:.1f} kW/100km".format(float(figures.consumption_df.mean(numeric_only=True)))
    return figures.trips_map, figures.consumption_fig, figures.consumption_fig_by_speed, consumption, figures.table_fig


@app.route('/getvehicles')
def get_vehicules():
    return jsonify(myp.getVIN())


@app.route('/get_vehicleinfo/<string:vin>')
def get_vehicle_Info(vin):
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
    longitude, latitude = res.last_position.geometry.coordinates
    return jsonify(
        {"longitude": longitude, "latitude": latitude, "url": f"http://maps.google.com/maps?q={latitude},{longitude}"})


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


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


def update_trips():
    global trips, chargings
    logger.info("update_data")
    try:
        trips = MyPSACC.get_trips()
        chargings = MyPSACC.get_chargings()
    except:
        logger.error("update_trips: " + traceback.format_exc())


try:
    web.db.callback_fct = update_trips
    update_trips()

    min_date = trips[0].start_at
    max_date = trips[-1].start_at
    min_millis = figures.unix_time_millis(min_date)
    max_millis = figures.unix_time_millis(max_date)
    step = (max_millis - min_millis) / 100
    figures.get_figures(trips, chargings)
    data_div = html.Div([dcc.RangeSlider(
        id='date-slider',
        min=min_millis,
        max=max_millis,
        step=step,
        marks=figures.get_marks_from_start_end(min_date,
                                               max_date),
        value=[min_millis, max_millis],
    ),
        html.Div([
            dbc.Tabs([
                dbc.Tab(label="Summary", tab_id="summary", children=[
                    html.H2(id="consumption",
                            children=figures.info),
                    dcc.Graph(figure=figures.consumption_fig, id="consumption_fig"),
                    dcc.Graph(figure=figures.consumption_fig_by_speed, id="consumption_fig_by_speed")
                ]),
                dbc.Tab(label="Trips", tab_id="trips", id="tab_trips", children=[figures.table_fig]),
                dbc.Tab(label="Battery", tab_id="battery", id="tab_battery", children=[figures.battery_info]),
                dbc.Tab(label="Map", tab_id="map", children=[
                    dcc.Graph(figure=figures.trips_map, id="trips_map", style={"height": '90vh'})]),
            ],
                id="tabs",
                active_tab="summary",
            ),
            html.Div(id="tab-content", className="p-4"),
        ])])
except:
    logger.error("Failed to generate figure, there is probably not enough data yet")
    logger.error(traceback.format_exc())
    data_div = dbc.Alert("No data to show", color="danger")

dash_app.layout = dbc.Container(fluid=True, children=[
    html.H1('My car info'),
    data_div
])
